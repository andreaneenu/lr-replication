"""Fama-MacBeth predictive cross-sectional regressions (paper Table 8).

Owner: Member 4. Reads: mu_hat, betas_svd, crsp_monthly. Writes: results/tables/table8.csv.
Spec: docs/members/member-4.md

Each formation month t, regress exret_{t+1} across stocks on:
  (1) a constant and mu_hat_t
  (2) a constant, mu_hat_t and beta_1..beta_K at t  (K = 5 and K = k_main)
Report the time-series average of each slope with Newey-West t-stats (lrrep.stats.nw_mean_test).
Paper finding: the mu_hat slope is positive, below 1, and stays significant (often more so)
when betas are added. Optional: weighted by market cap (Table 9).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.io import load, save_table
from lrrep.stats import nw_mean_test


def _panel(mu_hat, betas_svd, crsp_monthly, mu_col: str, k: int) -> pd.DataFrame:
    cur = crsp_monthly[["permno", "month", "in_universe"]]
    nxt = crsp_monthly[["permno", "month", "exret"]].copy()
    nxt["month"] = nxt["month"] - pd.offsets.MonthEnd(1)  # t+1 return indexed by formation month t
    nxt = nxt.rename(columns={"exret": "exret_next"})
    bcols = [f"beta_{j}" for j in range(1, k + 1)]
    d = (mu_hat[["permno", "month", mu_col]]
         .merge(cur, on=["permno", "month"])
         .merge(nxt, on=["permno", "month"]))
    if k > 0:
        d = d.merge(betas_svd[["permno", "month", *bcols]], on=["permno", "month"])
    return d[d["in_universe"].astype(bool)].dropna(subset=[mu_col, "exret_next", *bcols])


def monthly_slopes(mu_hat, betas_svd, crsp_monthly, mu_col: str, k: int) -> pd.DataFrame:
    """One row per formation month: slopes of the cross-sectional OLS.

    exret_{t+1} = a + b*mu_hat_t [+ c_1 beta_1,t + ... + c_k beta_k,t]. k = 0 means mu_hat only.
    Columns: const, mu, [beta_1..beta_k], r2, n. Index: formation month.
    """
    d = _panel(mu_hat, betas_svd, crsp_monthly, mu_col, k)
    xcols = [mu_col] + [f"beta_{j}" for j in range(1, k + 1)]
    names = ["const", "mu"] + [f"beta_{j}" for j in range(1, k + 1)]
    out = {}
    for t, g in d.groupby("month", sort=True):
        if len(g) < len(xcols) + 5:
            continue
        X = np.column_stack([np.ones(len(g)), g[xcols].to_numpy(float)])
        y = g["exret_next"].to_numpy(float)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ coef
        tss = ((y - y.mean()) ** 2).sum()
        out[t] = dict(zip(names, coef)) | {"r2": 1 - (resid @ resid) / tss if tss > 0 else np.nan, "n": len(g)}
    res = pd.DataFrame.from_dict(out, orient="index")
    res.index.name = "month"
    return res


def table8(slopes_by_spec: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Average slopes and NW t-stats per specification; save_table(..., 'table8').

    One row per (spec, term): the constant and the mu_hat slope (slopes on the individual betas are
    not reported, as in the paper), plus the average R-squared and average number of stocks.
    """
    rows = []
    for spec, s in slopes_by_spec.items():
        for term in ("const", "mu"):
            m, t = nw_mean_test(s[term])
            rows.append({"spec": spec, "term": term, "Mean": m, "NW t-stat": t})
        rows.append({"spec": spec, "term": "R2 (avg)", "Mean": s["r2"].mean(), "NW t-stat": np.nan})
        rows.append({"spec": spec, "term": "N stocks (avg)", "Mean": s["n"].mean(), "NW t-stat": np.nan})
        rows.append({"spec": spec, "term": "N months", "Mean": float(len(s)), "NW t-stat": np.nan})
    out = pd.DataFrame(rows).set_index(["spec", "term"])
    save_table(out, "table8")
    return out


def run(fake: bool = False, mu_col: str = "mu_ols") -> None:
    """Main model = mu_ols by default (say which model in the report); pass mu_col='mu_rf' when ready."""
    from lrrep.config import CFG

    mu, b, m = load("mu_hat", fake), load("betas_svd", fake), load("crsp_monthly", fake)
    k_main = CFG["hedge"]["k_main"]
    specs = {
        f"{mu_col}: mu only": 0,
        f"{mu_col}: mu + 5 betas": 5,
        f"{mu_col}: mu + {k_main} betas": k_main,
    }
    table8({name: monthly_slopes(mu, b, m, mu_col, k) for name, k in specs.items()})
