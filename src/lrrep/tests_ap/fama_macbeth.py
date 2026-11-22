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

import pandas as pd

from lrrep.io import load


def monthly_slopes(mu_hat, betas_svd, crsp_monthly, mu_col: str, k: int) -> pd.DataFrame:
    """One row per formation month: slopes of the cross-sectional OLS."""
    raise NotImplementedError("Member 4: cross-sectional regressions")


def table8(slopes_by_spec: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Average slopes and NW t-stats per specification; save_table(..., 'table8')."""
    raise NotImplementedError("Member 4: Table 8")


def run(fake: bool = False) -> None:
    mu, b, m = load("mu_hat", fake), load("betas_svd", fake), load("crsp_monthly", fake)
    raise NotImplementedError("Member 4: run the specifications and call table8")
    _ = (mu, b, m)
