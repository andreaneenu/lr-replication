"""CRSP data: daily and monthly returns, stock universe, market return.

Owner: Member 2. Writes: crsp_daily, crsp_monthly, market (see docs/CONTRACTS.md).
Spec:  docs/members/member-2.md

Needs a WRDS account (`pip install wrds`; first connection asks for your username and
can save a ~/.pgpass). NEVER commit credentials or raw CRSP data: CRSP is licensed.

WRDS note: CRSP is served in two formats. The legacy tables are crsp.dsf / crsp.msf with
names in crsp.msenames and delistings in crsp.msedelist. Newer accounts may only have the
CIZ format (crsp.dsf_v2 / crsp.msf_v2, with share type and exchange fields instead of
shrcd/exchcd). Check which you have first and map the filters accordingly; record what you
used in docs/status/member-2.md.
"""
from __future__ import annotations

import pandas as pd

from lrrep.config import CFG
from lrrep.io import save


def pull_monthly(db, start: str, end: str) -> pd.DataFrame:
    """Monthly stock file joined to names (share code, exchange code) for [start, end].

    Return columns: permno, month (month-end), ret, prc, shrout, shrcd, exchcd, dlret.
    - Keep shrcd in CFG['universe']['shrcd'] and exchcd in CFG['universe']['exchcd'],
      using the names record valid on that date (namedt <= date <= nameendt).
    - Merge delisting returns (dlret) in the delisting month.
    """
    raise NotImplementedError("Member 2: pull CRSP monthly via WRDS")


def pull_daily(db, permnos: list[int], start: str, end: str) -> pd.DataFrame:
    """Daily returns for the given permnos. Return columns: permno, date, ret.

    Tip: the daily file is large. Pull year by year and only for permnos that are ever
    in the universe. Expect roughly 15-25 million rows for 1965-2021 after filters.
    """
    raise NotImplementedError("Member 2: pull CRSP daily via WRDS")


def pull_risk_free_and_market() -> pd.DataFrame:
    """Monthly and daily risk-free rate and market excess return from the Ken French library.

    Return a monthly frame: month, mkt_exret, rf (decimals, not percent) and keep the daily
    rf series for crsp_daily. Source: F-F_Research_Data_Factors (monthly and daily).
    """
    raise NotImplementedError("Member 2: risk-free rate and market return")


def build_monthly(msf: pd.DataFrame, rf_monthly: pd.DataFrame) -> pd.DataFrame:
    """Build the crsp_monthly contract file.

    - ret_total = (1 + ret) * (1 + dlret) - 1 when dlret exists (missing ret + dlret -> dlret).
    - exret = ret_total - rf.
    - me = |prc| * shrout / 1000  ($ millions; shrout is in thousands).
    - in_universe[t] = shrcd/exchcd filters pass AND me[t] >= NYSE 20th percentile of me at t
      (percentile over exchcd == 1 stocks only).
    Columns exactly as CONTRACTS['crsp_monthly'].
    """
    raise NotImplementedError("Member 2: build crsp_monthly")


def build_daily(dsf: pd.DataFrame, rf_daily: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    """Build the crsp_daily contract file: permno, date, ret, rf, exret.

    Keep a stock's daily rows for the 12 months after any month it is in_universe, so Member 3
    can form full 252-day windows. Drop rows with missing ret.
    """
    raise NotImplementedError("Member 2: build crsp_daily")


def run(fake: bool = False) -> None:
    if fake:
        print("crsp: fake files come from `make fake`; nothing to do")
        return
    import wrds  # noqa: F401  (pip install wrds)

    raise NotImplementedError("Member 2: wire pull_* and build_* together, then save() each file")
    # db = wrds.Connection()
    # ... save(monthly, "crsp_monthly"); save(daily, "crsp_daily"); save(market, "market")
    _ = (CFG, save)
