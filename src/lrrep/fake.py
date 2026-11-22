"""Generate synthetic versions of EVERY contract file so all members can work from day 1.

Owner: Member 1. Run with `make fake` (or `python -m lrrep.fake`). Writes to data/fake/.

The fake world has a real factor structure and a characteristic-driven alpha that is
NOT explained by the factors, so the full pipeline should show the paper's pattern:
factor-exposure portfolios earn ~0, the beta-neutral portfolio earns a positive return
with lower volatility than the unhedged one. Use it to check your code runs end to end
and gives sensible signs; never report fake-data numbers.

Derived files (betas_svd, eigen, chars_clean, mu_hat, factor_portfolios, portfolios)
are also faked so downstream members are never blocked. Each member's real code
overwrites only their own files.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import save


def _month_end(s: pd.Series | pd.DatetimeIndex) -> pd.Series:
    return pd.to_datetime(s) + pd.offsets.MonthEnd(0)


def make_fake_data(seed: int | None = None) -> dict[str, pd.DataFrame]:
    f = CFG["fake"]
    rng = np.random.default_rng(CFG["seed"] if seed is None else seed)
    n, k, n_chars = f["n_stocks"], f["n_factors"], f["n_chars"]
    days = pd.bdate_range(f["start"], pd.Timestamp(f["end"]) + pd.offsets.MonthEnd(0))
    months = pd.date_range(f["start"], pd.Timestamp(f["end"]) + pd.offsets.MonthEnd(0), freq="ME")
    permnos = np.arange(10001, 10001 + n)

    # --- characteristics: persistent AR(1) per stock, monthly ---------------------------
    T_m = len(months)
    chars = np.zeros((T_m, n, n_chars))
    chars[0] = rng.standard_normal((n, n_chars))
    for t in range(1, T_m):
        chars[t] = 0.95 * chars[t - 1] + np.sqrt(1 - 0.95**2) * rng.standard_normal((n, n_chars))
    # true expected monthly excess return: alpha from chars (not from factor betas)
    mu_true = 0.004 + 0.006 * np.tanh(chars[:, :, 0]) - 0.004 * chars[:, :, 1] * (chars[:, :, 2] > 0)

    # --- daily returns with a k-factor structure ------------------------------------------
    T_d = len(days)
    fac_sd = 0.012 * np.linspace(1.0, 0.3, k)
    factors = rng.standard_normal((T_d, k)) * fac_sd
    factors[:, 0] += 0.0001  # small market-like drift
    betas_true = rng.standard_normal((n, k)) * 0.5
    betas_true[:, 0] = 1.0 + 0.3 * rng.standard_normal(n)
    rf_d = 0.0001
    month_idx = np.searchsorted(months.values, (days + pd.offsets.MonthEnd(0)).values)
    alpha_d = mu_true[month_idx] / 21.0                       # (T_d, n)
    eps = rng.standard_normal((T_d, n)) * 0.02
    exret_d = alpha_d + factors @ betas_true.T + eps
    # listing windows and random missing days
    first = rng.integers(0, T_d // 6, n)
    last = T_d - rng.integers(0, T_d // 6, n) * (rng.random(n) < 0.3)
    alive = (np.arange(T_d)[:, None] >= first) & (np.arange(T_d)[:, None] < last)
    alive &= rng.random((T_d, n)) > 0.01
    di, si = np.nonzero(alive)
    crsp_daily = pd.DataFrame({
        "permno": permnos[si].astype("int64"),
        "date": days[di],
        "exret": exret_d[di, si],
    })
    crsp_daily["rf"] = rf_d
    crsp_daily["ret"] = crsp_daily["exret"] + rf_d
    crsp_daily = crsp_daily[["permno", "date", "ret", "rf", "exret"]]

    # --- monthly returns, size, universe ----------------------------------------------------
    crsp_daily["month"] = _month_end(crsp_daily["date"])
    g = crsp_daily.groupby(["permno", "month"])
    mon = g["ret"].apply(lambda r: np.prod(1 + r) - 1).rename("ret").to_frame()
    mon["rf"] = g["rf"].apply(lambda r: np.prod(1 + r) - 1)
    mon = mon.reset_index()
    mon["exret"] = mon["ret"] - mon["rf"]
    log_size = pd.Series(rng.normal(6, 1.5, n), index=permnos)
    mon["me"] = np.exp(log_size.reindex(mon["permno"]).to_numpy()) * (1 + mon.groupby("permno")["ret"].cumsum().to_numpy())
    mon["me"] = mon["me"].clip(lower=1.0)
    exch = pd.Series(rng.choice([1, 2, 3], n, p=[0.4, 0.1, 0.5]), index=permnos)
    mon["exchcd"] = exch.reindex(mon["permno"]).to_numpy().astype("int64")
    mon["shrcd"] = np.where(rng.random(len(mon)) < 0.5, 10, 11).astype("int64")
    nyse_p20 = mon[mon["exchcd"] == 1].groupby("month")["me"].quantile(CFG["universe"]["nyse_size_pct"])
    mon["in_universe"] = (mon["me"] >= mon["month"].map(nyse_p20)).astype(bool)
    crsp_monthly = mon[["permno", "month", "ret", "exret", "me", "exchcd", "shrcd", "in_universe"]].copy()
    crsp_daily = crsp_daily.drop(columns="month")

    # --- market and external factors -------------------------------------------------------
    vw = mon.assign(w=mon.groupby("month")["me"].shift(0)).groupby("month").apply(
        lambda d: np.average(d["exret"], weights=d["w"]), include_groups=False)
    market = pd.DataFrame({"month": vw.index, "mkt_exret": vw.to_numpy()})
    market["rf"] = mon.groupby("month")["rf"].first().to_numpy()
    fx = pd.DataFrame({"month": months})
    fx["mkt_rf"] = market.set_index("month")["mkt_exret"].reindex(months).to_numpy()
    for col in ["smb", "hml", "rmw", "cma", "umd", "q_me", "q_ia", "q_roe", "q_eg", "sy_mgmt", "sy_perf"]:
        fx[col] = rng.normal(0.002, 0.03, T_m)

    # --- fake derived files (overwritten by the owners' real code) --------------------------
    mi, si2 = np.meshgrid(np.arange(T_m), np.arange(n), indexing="ij")
    base = pd.DataFrame({"permno": permnos[si2.ravel()].astype("int64"), "month": months[mi.ravel()]})
    present = crsp_monthly[["permno", "month"]]
    base = base.merge(present, on=["permno", "month"])
    pos_m = np.searchsorted(months.values, base["month"].values)
    pos_s = base["permno"].to_numpy() - 10001
    kb = max(CFG["hedge"]["k_main"], 10)
    noise_b = rng.standard_normal((len(base), kb)) * 0.05
    bt = np.zeros((len(base), kb))
    bt[:, :k] = betas_true[pos_s]
    betas_svd = base.copy()
    for j in range(kb):
        betas_svd[f"beta_{j + 1}"] = bt[:, j] + noise_b[:, j]
    eig = fac_sd**2
    tot = eig.sum() + 0.02**2 * 1.0
    eigen = pd.DataFrame([(m, j + 1, (eig[j] if j < k else 1e-6), (eig[j] if j < k else 1e-6) / tot)
                          for m in months for j in range(kb)], columns=["month", "k", "eigenvalue", "share_explained"])
    eigen["k"] = eigen["k"].astype("int64")
    chars_clean = base.copy()
    for j in range(n_chars):
        chars_clean[f"c_{j + 1:02d}"] = chars[pos_m, pos_s, j]
    # forecasts made at t for t+1: true mu at t+1 plus noise (chars are persistent)
    nxt = np.minimum(pos_m + 1, T_m - 1)
    mu_hat = base.copy()
    # like real ML forecasts, the fake ones also load on factor betas, which carry no premium:
    # hedging those betas should cut volatility without cutting the mean
    tilt = 0.004 * (betas_true[pos_s, 1] + betas_true[pos_s, 2])
    mu_hat["mu_ols"] = mu_true[nxt, pos_s] * 0.6 + tilt + rng.normal(0, 0.004, len(base))
    mu_hat["mu_lasso"] = mu_true[nxt, pos_s] * 0.6 + tilt + rng.normal(0, 0.004, len(base))
    mu_hat["mu_rf"] = mu_true[nxt, pos_s] * 0.7 + tilt + rng.normal(0, 0.003, len(base))
    fp = pd.DataFrame({"month": months})
    for j in range(kb):
        fp[f"fexp_{j + 1}"] = rng.normal(0.0, 0.02, T_m)
    pf = pd.DataFrame({"month": months, "mkt": fx["mkt_rf"].to_numpy(),
                       "ls_main": rng.normal(0.008, 0.035, T_m), "bn_main": rng.normal(0.007, 0.015, T_m)})

    return {"crsp_daily": crsp_daily, "crsp_monthly": crsp_monthly, "market": market,
            "factors_ext": fx, "betas_svd": betas_svd, "eigen": eigen, "chars_clean": chars_clean,
            "mu_hat": mu_hat, "factor_portfolios": fp, "portfolios": pf}


def main() -> None:
    files = make_fake_data()
    for name, df in files.items():
        p = save(df, name, fake=True)
        print(f"wrote {p.relative_to(p.parents[2])}  rows={len(df):,}  cols={df.shape[1]}")


if __name__ == "__main__":
    main()
