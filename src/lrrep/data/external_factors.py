"""External factors for the alpha regressions: FF5 + momentum, q5, Stambaugh-Yuan.

Owner: Member 7. Writes: factors_ext. Spec: docs/members/member-7.md

Sources (download the CSVs by hand if a script can't reach the site, and put the raw files
in the shared data folder under raw/factors/, never in git):
- Fama-French 5 factors and momentum, monthly: Ken French data library
  (F-F_Research_Data_5_Factors_2x3, F-F_Momentum_Factor). Values are in PERCENT: divide by 100.
- q5 factors, monthly: global-q.org (R_ME, R_IA, R_ROE, R_EG). Check units on download.
- Stambaugh-Yuan mispricing factors (MGMT, PERF): Robert Stambaugh's website (finance.wharton.upenn.edu).
"""
from __future__ import annotations

import pandas as pd

from lrrep.io import save


def load_ff(raw_dir) -> pd.DataFrame:
    """Return month, mkt_rf, smb, hml, rmw, cma, umd in decimals."""
    raise NotImplementedError("Member 7: parse Fama-French CSVs")


def load_q5(raw_dir) -> pd.DataFrame:
    """Return month, q_me, q_ia, q_roe, q_eg in decimals."""
    raise NotImplementedError("Member 7: parse q5 CSV")


def load_sy(raw_dir) -> pd.DataFrame:
    """Return month, sy_mgmt, sy_perf in decimals."""
    raise NotImplementedError("Member 7: parse Stambaugh-Yuan CSV")


def build_factors(raw_dir) -> pd.DataFrame:
    """Outer-join the three sources on month (month-end), columns as CONTRACTS['factors_ext']."""
    raise NotImplementedError("Member 7: merge external factors")


def run(fake: bool = False) -> None:
    if fake:
        print("external factors: fake file comes from `make fake`; nothing to do")
        return
    from lrrep.config import data_dir

    save(build_factors(data_dir() / "raw" / "factors"), "factors_ext")
