"""Time-series alpha regressions (paper Tables 10-11).

Owner: Member 7. Reads: portfolios, factors_ext. Writes: results/tables/table10.csv.
Spec: docs/members/member-7.md

Guideline robustness item "Alternative stories: does the alpha go away under FF3, FF5, q?"
Regress ls_main and bn_main (monthly excess returns) on:
  CAPM: mkt_rf
  FF3: mkt_rf, smb, hml
  FF5 + momentum: mkt_rf, smb, hml, rmw, cma, umd
  q5: mkt_rf, q_me, q_ia, q_roe, q_eg
  Stambaugh-Yuan: mkt_rf, smb, sy_mgmt, sy_perf
Report alpha (% per month), its Newey-West t-stat, factor loadings and R^2
(use lrrep.stats.time_series_regression). Paper: both portfolios have significant alphas;
the hedged portfolio's alpha is about 85 bp/month against q5 and Stambaugh-Yuan.
"""
from __future__ import annotations

import pandas as pd

from lrrep.io import load

MODELS = {
    "CAPM": ["mkt_rf"],
    "FF3": ["mkt_rf", "smb", "hml"],
    "FF5+UMD": ["mkt_rf", "smb", "hml", "rmw", "cma", "umd"],
    "q5": ["mkt_rf", "q_me", "q_ia", "q_roe", "q_eg"],
    "SY": ["mkt_rf", "smb", "sy_mgmt", "sy_perf"],
}


def table10(portfolios: pd.DataFrame, factors_ext: pd.DataFrame) -> pd.DataFrame:
    """Alphas and loadings for ls_main and bn_main under each model; save_table(..., 'table10')."""
    raise NotImplementedError("Member 7: Table 10")


def table10_post_publication(portfolios: pd.DataFrame, factors_ext: pd.DataFrame) -> pd.DataFrame:
    """EXTENSION: the same alphas for bn_main over CFG tests.events.post_publication .. sample.end only.
    Save as table10_post. Short sample: report it, but say the t-stats have little power."""
    raise NotImplementedError("Member 7: post-publication alphas")


def run(fake: bool = False) -> None:
    pf, fx = load("portfolios", fake), load("factors_ext", fake)
    table10(pf, fx)
    table10_post_publication(pf, fx)
