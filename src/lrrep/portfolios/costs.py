"""EXTENSION: is the beta-neutral portfolio tradeable after costs?

Owner: Member 6. Reads: portfolio_weights, portfolios, crsp_monthly.
Writes: results/tables/costs.csv (and an optional figure). Spec: docs/members/member-6.md

 - Turnover in month t+1 = 1/2 * sum_i |w_{i,t} - w_{i,t-1} * (1 + r_{i,t}) / (1 + r_p,t)|  (drifted
   weights; a simpler version without drift is fine, say which). Stocks entering/leaving count fully.
 - Return after costs = gross return - 2 * turnover * c, for one-way cost c in CFG['extension']['cost_bps']
   (2x because each $ of turnover is a sell and a buy). Report mean, Sharpe after costs for each c,
   and the break-even c at which the mean return after costs is zero.
 - Do it for ls_main and bn_main. The hedged portfolio may trade a lot (betas change every month):
   that is the interesting finding either way.
 - With CFG['extension']['quarterly_rebalance'], also report the quarterly-rebalanced version
   (lower turnover; frequency robustness).
"""
from __future__ import annotations

import pandas as pd

from lrrep.io import load, save_table


def turnover(weights: pd.DataFrame, col: str, crsp_monthly: pd.DataFrame | None = None) -> pd.Series:
    """Monthly one-way turnover of the portfolio in column `col` ('w_ls' or 'w_bn'), indexed by month."""
    raise NotImplementedError("Member 6: turnover")


def cost_table(portfolios: pd.DataFrame, weights: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Rows: portfolio x cost level; columns: mean turnover, mean return after costs, Sharpe after costs;
    plus a break-even cost row per portfolio."""
    raise NotImplementedError("Member 6: cost table")


def run(fake: bool = False) -> None:
    pf, w, m = load("portfolios", fake), load("portfolio_weights", fake), load("crsp_monthly", fake)
    save_table(cost_table(pf, w, m), "costs")
