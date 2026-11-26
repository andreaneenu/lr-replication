"""Out-of-sample return forecasts (paper Section 2.4).

Owner: Member 5. Reads: chars_clean, crsp_monthly. Writes: mu_hat.
Spec: docs/members/member-5.md

Training scheme (our 6-day version of the paper's monthly retraining):
 - At each retraining month t0 (every CFG['forecast']['retrain_every_months'] months), fit on
   pairs (chars at s, exret at s+1) for s in the CFG['forecast']['train_months'] months
   ENDING AT t0 - 1, so the latest target used is exret at t0. Nothing after t0 is used.
 - Use that fitted model to predict exret(t+1) from chars(t) for t = t0, ..., t0 + 11.
 - Models: OLS (fast, first), LASSO, random forest with
   CFG['forecast']['random_forest'] (500 trees, max depth 5). Seed CFG['seed'].
 - Output mu_hat: permno, month (= t, the formation month), mu_ols, mu_lasso, mu_rf.
   Ship mu_ols and mu_lasso first (day 2-3) so Member 6 can build Table 6; add mu_rf when the
   forest finishes (run it overnight; save partial progress per year so a crash loses little).

Forecast quality to report (docs/members/member-5.md): out-of-sample R^2 vs a zero forecast,
and the average spread in realized exret between the top and bottom deciles of mu.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import load, save

MODELS = ("ols", "lasso", "rf")


def make_model(name: str):
    """Return an unfitted sklearn estimator for 'ols', 'lasso' or 'rf' using CFG values."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import Lasso, LassoCV, LinearRegression
    from sklearn.model_selection import TimeSeriesSplit

    f = CFG["forecast"]
    if name == "ols":
        return LinearRegression()
    if name == "lasso":
        if f.get("lasso_alpha") is None:
            # rows are sorted by month, so TimeSeriesSplit validates on later months only
            return LassoCV(cv=TimeSeriesSplit(n_splits=5), max_iter=5000, random_state=CFG["seed"])
        return Lasso(alpha=f["lasso_alpha"], max_iter=5000)
    if name == "rf":
        return RandomForestRegressor(**f["random_forest"], random_state=CFG["seed"])
    raise ValueError(f"unknown model {name!r}; expected one of {MODELS}")


def _feature_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("c_")]


def training_pairs(chars: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Join chars at month t to exret at month t+1 (by permno). Column 'y' = next-month exret."""
    nxt = crsp_monthly[["permno", "month", "exret"]].copy()
    nxt["month"] = nxt["month"] - pd.offsets.MonthEnd(1)  # return realized in t+1 -> formation month t
    nxt = nxt.rename(columns={"exret": "y"})
    return chars.merge(nxt, on=["permno", "month"], how="left")


def retrain_months(chars: pd.DataFrame) -> list[pd.Timestamp]:
    """Retraining dates t0: the first month with a full training window, then every
    retrain_every_months. Built from the chars calendar only, so it never depends on returns."""
    f = CFG["forecast"]
    months = sorted(chars["month"].unique())
    return [pd.Timestamp(m) for m in months[f["train_months"]::f["retrain_every_months"]]]


def rolling_forecasts(pairs: pd.DataFrame, chars: pd.DataFrame, model: str, cache_dir=None) -> pd.Series:
    """Fit every retrain_every_months on the trailing train_months window and predict forward.
    Returns a Series indexed like `chars` (permno, month) of forecasts for model `model`.
    Must never fit on targets dated after the formation month being predicted.
    cache_dir: if given, each retraining year's predictions are saved there and reused on a rerun,
    so a crash part-way through the random forest loses at most one year."""
    f = CFG["forecast"]
    feats = _feature_cols(chars)
    months = pd.DatetimeIndex(sorted(chars["month"].unique()))
    out = pd.Series(np.nan, index=chars.index, name=f"mu_{model}")

    for t0 in retrain_months(chars):
        i0 = months.get_loc(t0)
        pred_t = months[i0: i0 + f["retrain_every_months"]]
        mask = chars["month"].isin(pred_t)
        cache = None if cache_dir is None else Path(cache_dir) / f"{model}_{t0:%Y%m}.parquet"
        if cache is not None and cache.exists():
            got = chars.loc[mask, ["permno", "month"]].merge(pd.read_parquet(cache), on=["permno", "month"], how="left")
            out[mask] = got["mu"].to_numpy()
            print(f"  {model}: {t0:%Y-%m} loaded from cache")
            continue
        # training formation months s = t0-60 .. t0-1, so the latest target is exret at t0
        train_s = months[i0 - f["train_months"]: i0]
        train = pairs[pairs["month"].isin(train_s)].dropna(subset=["y"]).sort_values("month")
        if train.empty:
            continue
        # paper Section 3.1: within each training window, drop characteristics missing for more than
        # 1 - min_coverage of rows, then fill the rest with the median (0 after rank standardization)
        use = [c for c in feats if train[c].notna().mean() >= f["min_coverage"]]
        est = make_model(model)
        est.fit(train[use].fillna(0.0).to_numpy(dtype="float64"), train["y"].to_numpy(dtype="float64"))
        # predict formation months t0 .. t0+11 with this fit
        if mask.any():
            out[mask] = est.predict(chars.loc[mask, use].fillna(0.0).to_numpy(dtype="float64"))
        if cache is not None:
            cache.parent.mkdir(parents=True, exist_ok=True)
            chars.loc[mask, ["permno", "month"]].assign(mu=out[mask].to_numpy()).to_parquet(cache, index=False)
        print(f"  {model}: fit at {t0:%Y-%m} on {len(train):,} rows x {len(use)} chars -> "
              f"predicted {pred_t[0]:%Y-%m}..{pred_t[-1]:%Y-%m}")
    return out


def run(fake: bool = False, models: tuple[str, ...] = MODELS) -> None:
    """Forecast with `models` and save mu_hat after each one (OLS/LASSO land before the slow
    forest). Columns of models not run now are kept from an existing mu_hat, else NaN."""
    from lrrep.io import path_for

    chars = load("chars_clean", fake)
    monthly = load("crsp_monthly", fake, columns=["permno", "month", "exret"])
    pairs = training_pairs(chars, monthly)
    out = chars[["permno", "month"]].copy()
    old = load("mu_hat", fake) if path_for("mu_hat", fake).exists() else None
    for m in MODELS:
        col = f"mu_{m}"
        out[col] = (out[["permno", "month"]].merge(old[["permno", "month", col]], on=["permno", "month"], how="left")[col]
                    .to_numpy() if old is not None else np.nan)
    # cache keyed to this chars_clean version, so rebuilding chars_clean never reuses stale fits
    stamp = int(path_for("chars_clean", fake).stat().st_mtime)
    cache_dir = None if fake else path_for("mu_hat").parent / "forecast_cache" / str(stamp)
    for m in models:
        out[f"mu_{m}"] = rolling_forecasts(pairs, chars, m, cache_dir=cache_dir).to_numpy()
        save(out, "mu_hat", fake)
        print(f"mu_hat saved with {m}")
    print(forecast_quality(out, monthly).to_string())


def forecast_quality(mu: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    """REPORT: per model, over formation months sample.start-1 .. sample.end-1 (returns realized
    in the sample): out-of-sample R^2 against a zero forecast, 1 - sum((y - mu)^2) / sum(y^2),
    and the average monthly top-minus-bottom decile spread in realized exret (%, with t-stat).
    Saved as forecast_quality."""
    from lrrep.io import save_table

    s = CFG["sample"]
    lo = pd.Timestamp(s["start"]) + pd.offsets.MonthEnd(0) - pd.offsets.MonthEnd(1)
    d = training_pairs(mu, monthly)
    d = d[d["month"] >= lo].dropna(subset=["y"])
    rows = []
    for m in MODELS:
        col = f"mu_{m}"
        x = d.dropna(subset=[col])
        if x.empty:
            rows.append({"model": m})
            continue
        r2 = 1.0 - ((x["y"] - x[col]) ** 2).sum() / (x["y"] ** 2).sum()
        dec = x.groupby("month")[col].transform(lambda v: pd.qcut(v.rank(method="first"), 10, labels=False))
        by = x.assign(dec=dec).groupby(["month", "dec"])["y"].mean().unstack()
        spread = (by[9] - by[0]).dropna()
        rows.append({"model": m, "oos_r2_vs_zero_pct": 100 * r2, "decile_spread_pct_per_month": 100 * spread.mean(),
                     "spread_tstat": spread.mean() / spread.std() * np.sqrt(len(spread)),
                     "n_months": len(spread), "first_month": f"{x.month.min():%Y-%m}",
                     "last_month": f"{x.month.max():%Y-%m}"})
    q = pd.DataFrame(rows).set_index("model")
    save_table(q, "forecast_quality")
    return q


if __name__ == "__main__":
    # python -m lrrep.forecast.models ols lasso   (real data; add --fake for fake data)
    import sys

    args = [a for a in sys.argv[1:] if a != "--fake"]
    run(fake="--fake" in sys.argv, models=tuple(args) or MODELS)
