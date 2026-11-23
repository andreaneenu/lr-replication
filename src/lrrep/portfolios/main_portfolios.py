"""Unhedged and beta-neutral portfolios: the paper's main result (Sections 2.5.1 and 3.4).

Owner: Member 6. Reads: mu_hat, betas_svd, crsp_monthly, market. Writes: portfolios.
Also writes: portfolio_weights (read by Member 4's cash-flow news test).
Outputs: Table 6 (three subperiods), Figure 6 (Sharpe vs number of factors hedged),
Figures 7-9 (cumulative returns), plus robustness/extension tables:
  table6_events  (before/after Volcker, GFC, COVID, and post-publication = the EXTENSION)
  table6_weekly  (beta-neutral portfolio hedged with weekly-return betas: frequency robustness)
Trading costs live in lrrep.portfolios.costs. Spec: docs/members/member-6.md

For each formation month t:
  stocks = in_universe at t with mu_hat, betas at t and exret at t+1 (drop NaN rows)
  w_ls = expected_return_portfolio(mu)                    # unhedged long-short
  w_bn = expected_return_portfolio(mu, betas[:, :K])      # beta-neutral, K = k_main
  returns realized in t+1: w' exret_{t+1}
Main forecast column: 'mu_rf' if available, else 'mu_ols' (record which in the table note).
Paper targets (Table 6, 1974-2021): market Sharpe 0.52, long-short 0.84, beta-neutral 2.31.
"""
from __future__ import annotations

import pandas as pd

from lrrep.io import load, save


def portfolio_returns(mu_hat: pd.DataFrame, betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame,
                      mu_col: str, k: int | None) -> pd.Series:
    """Monthly returns (indexed by realization month) of the unhedged (k=None) or beta-neutral portfolio."""
    raise NotImplementedError("Member 6: portfolio returns")


def main_weights(mu_hat: pd.DataFrame, betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame,
                 mu_col: str, k: int) -> pd.DataFrame:
    """portfolio_weights contract: permno, month (formation month t), w_ls, w_bn for the main portfolios."""
    raise NotImplementedError("Member 6: save the main portfolio weights")


def table6_events(pf: pd.DataFrame) -> pd.DataFrame:
    """lrrep.stats.summarize_events on [mkt, ls_main, bn_main] over the FULL extended sample
    (CFG sample.start..sample.end); stack with lrrep.stats.stack_panels; save as table6_events.
    The post_publication 'after' panel is the extension's headline out-of-sample result."""
    raise NotImplementedError("Member 6: event subsamples")


def build_portfolios(mu_hat, betas_svd, crsp_monthly, market) -> pd.DataFrame:
    """Return the portfolios contract frame: month, mkt, ls_main, bn_main, plus
    ls_<model> and bn_<model>_k<K> for each available model and K in CFG['hedge']['k_list'],
    bn_main_weekly (hedged with betas_svd_weekly, if that file exists), and, if
    CFG['extension']['quarterly_rebalance'], ls_main_q / bn_main_q (weights formed every 3rd month and
    held 3 months: frequency robustness). Runs over the full extended sample (sample.end)."""
    raise NotImplementedError("Member 6: build all portfolio series")


def table6(pf: pd.DataFrame) -> pd.DataFrame:
    """Replication: lrrep.stats.summarize_subperiods on [mkt, ls_main, bn_main] (paper's panels, ending
    at CFG sample.paper_end); stack_panels; save as table6."""
    raise NotImplementedError("Member 6: Table 6")


def figure6(pf: pd.DataFrame) -> None:
    """Annualized Sharpe of bn_<main model>_k<K> against K."""
    raise NotImplementedError("Member 6: Figure 6")


def figures7_9(pf: pd.DataFrame) -> None:
    """Cumulative returns of mkt, ls_main, bn_main: full sample (7), 1974-1999 (8), 2000-2021 (9)."""
    raise NotImplementedError("Member 6: Figures 7-9")


def run(fake: bool = False) -> None:
    from lrrep.config import CFG

    mu, b, m = load("mu_hat", fake), load("betas_svd", fake), load("crsp_monthly", fake)
    pf = build_portfolios(mu, b, m, load("market", fake))
    save(pf, "portfolios", fake)
    main_col = "mu_rf" if mu["mu_rf"].notna().any() else "mu_ols"
    save(main_weights(mu, b, m, main_col, CFG["hedge"]["k_main"]), "portfolio_weights", fake)
    table6(pf)
    table6_events(pf)
    figure6(pf)
    figures7_9(pf)
