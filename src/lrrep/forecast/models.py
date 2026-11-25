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


def rolling_forecasts(pairs: pd.DataFrame, chars: pd.DataFrame, model: str) -> pd.Series:
    """Fit every retrain_every_months on the trailing train_months window and predict forward.
    Returns a Series indexed like `chars` (permno, month) of forecasts for model `model`.
    Must never fit on targets dated after the formation month being predicted."""
    f = CFG["forecast"]
    feats = _feature_cols(chars)
    months = pd.DatetimeIndex(sorted(chars["month"].unique()))
    out = pd.Series(np.nan, index=chars.index, name=f"mu_{model}")

    for t0 in retrain_months(chars):
        i0 = months.get_loc(t0)
        # training formation months s = t0-60 .. t0-1, so the latest target is exret at t0
        train_s = months[i0 - f["train_months"]: i0]
        train = pairs[pairs["month"].isin(train_s)].dropna(subset=["y"]).sort_values("month")
        if train.empty:
            continue
        est = make_model(model)
        est.fit(train[feats].fillna(0.0).to_numpy(), train["y"].to_numpy())
        # predict formation months t0 .. t0+11 with this fit
        pred_t = months[i0: i0 + f["retrain_every_months"]]
        mask = chars["month"].isin(pred_t)
        if mask.any():
            out[mask] = est.predict(chars.loc[mask, feats].fillna(0.0).to_numpy())
        print(f"  {model}: fit at {t0:%Y-%m} on {len(train):,} rows -> "
              f"predicted {pred_t[0]:%Y-%m}..{pred_t[-1]:%Y-%m}")
    return out


def run(fake: bool = False, models: tuple[str, ...] = MODELS) -> None:
    chars, monthly = load("chars_clean", fake), load("crsp_monthly", fake)
    pairs = training_pairs(chars, monthly)
    out = chars[["permno", "month"]].copy()
    for m in MODELS:
        out[f"mu_{m}"] = rolling_forecasts(pairs, chars, m).to_numpy() if m in models else np.nan
    save(out, "mu_hat", fake)
    _ = CFG
