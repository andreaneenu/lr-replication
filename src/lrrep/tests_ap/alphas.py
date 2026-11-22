"""Time-series alpha regressions (paper Tables 10-11).

Owner: Member 7. Reads: portfolios, factors_ext. Writes: results/tables/table10.csv.
Spec: docs/members/member-7.md

Regress ls_main and bn_main (monthly excess returns) on:
  CAPM: mkt_rf
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
    "FF5+UMD": ["mkt_rf", "smb", "hml", "rmw", "cma", "umd"],
    "q5": ["mkt_rf", "q_me", "q_ia", "q_roe", "q_eg"],
    "SY": ["mkt_rf", "smb", "sy_mgmt", "sy_perf"],
}


def table10(portfolios: pd.DataFrame, factors_ext: pd.DataFrame) -> pd.DataFrame:
    """Alphas and loadings for ls_main and bn_main under each model; save_table(..., 'table10')."""
    raise NotImplementedError("Member 7: Table 10")


def run(fake: bool = False) -> None:
    table10(load("portfolios", fake), load("factors_ext", fake))
