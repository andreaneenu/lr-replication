"""Zero-cost factor-exposure portfolios: is exposure to the latent factors priced? (paper Section 2.3)

Owner: Member 4. Reads: betas_svd, crsp_monthly. Writes: factor_portfolios.
Outputs: Table 2 (mean, std. dev, Sharpe of each portfolio; paper: Sharpe ratios near 0),
Figure 4 (cumulative returns). Spec: docs/members/member-4.md

For each formation month t and each k = 1..K (K = CFG['hedge']['k_main']):
  stocks = in_universe at t with betas at t and exret at t+1
  w_k = factor_exposure_portfolio(B_t[:, :K], k-1)   # beta 1 on k, 0 on others, zero cost
  fexp_k realized in month t+1 = w_k' exret_{t+1}
Use lrrep.portfolios.solver (do not re-implement it). Equal weighting (omega = identity).
"""
from __future__ import annotations

import pandas as pd

from lrrep.io import load, save


def build_factor_portfolios(betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame, k: int) -> pd.DataFrame:
    """Return the factor_portfolios contract frame: month (realization month), fexp_1..fexp_k."""
    raise NotImplementedError("Member 4: factor-exposure portfolios")


def table2(fp: pd.DataFrame) -> pd.DataFrame:
    """Mean (% per month), Std. dev, annualized Sharpe for fexp_1..fexp_10 (use lrrep.stats.summarize).
    Save with lrrep.io.save_table(df, 'table2')."""
    raise NotImplementedError("Member 4: Table 2")


def figure4(fp: pd.DataFrame) -> None:
    """Cumulative returns of fexp_1..fexp_5 vs the market. Save to figure_path('figure4')."""
    raise NotImplementedError("Member 4: Figure 4")


def run(fake: bool = False) -> None:
    from lrrep.config import CFG

    fp = build_factor_portfolios(load("betas_svd", fake), load("crsp_monthly", fake), CFG["hedge"]["k_main"])
    save(fp, "factor_portfolios", fake)
    table2(fp)
    figure4(fp)
