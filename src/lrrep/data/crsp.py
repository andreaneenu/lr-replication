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

    # Work on copies so that the original inputs are not modified.
    df = msf.copy()
    rf = rf_monthly.copy()

    # Standardize month-end dates.
    df["month"] = (
        pd.to_datetime(df["month"]) + pd.offsets.MonthEnd(0)
    )
    rf["month"] = (
        pd.to_datetime(rf["month"]) + pd.offsets.MonthEnd(0)
    )

    # Check that each stock-month and risk-free month is unique.
    if df.duplicated(["permno", "month"]).any():
        raise ValueError("Duplicate CRSP stock-month observations")
    if rf.duplicated(["month"]).any():
        raise ValueError("Duplicate risk-free month observations")

    # Convert financial inputs to numeric values.
    for col in ["ret", "dlret", "prc", "shrout"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["shrcd", "exchcd"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    rf["rf"] = pd.to_numeric(rf["rf"], errors="coerce")

    # Delisting-adjusted returns.
    df["ret_total"] = (1 + df["ret"]) * (1 + df["dlret"]) - 1

    # If there is no delisting, use the ordinary return.
    df["ret_total"] = df["ret_total"].fillna(df["ret"])

    # If the ordinary return is missing, use the delisting return.
    df["ret_total"] = df["ret_total"].fillna(df["dlret"])

    # Market capitalization in millions of dollars.
    df["me"] = df["prc"].abs() * df["shrout"] / 1000

    # Join monthly risk-free rates.
    df = df.merge(
        rf[["month", "rf"]],
        on="month",
        how="left",
        validate="many_to_one",
    )

    if df["rf"].isna().any():
        raise ValueError("Missing risk-free rate for some months")

    df["exret"] = df["ret_total"] - df["rf"]

    # Eligible common stocks on NYSE, AMEX, and NASDAQ.
    eligible = (
        df["shrcd"].isin(CFG["universe"]["shrcd"])
        & df["exchcd"].isin(CFG["universe"]["exchcd"])
    )

    # NYSE common-stock universe for the size breakpoint.
    nyse = df.loc[
        (df["exchcd"] == 1)
        & df["shrcd"].isin(CFG["universe"]["shrcd"])
        & (df["me"] > 0)
    ]

    breakpoints = (
        nyse.groupby("month")["me"]
        .quantile(0.20)
        .rename("nyse_p20")
    )

    df = df.join(breakpoints, on="month")

    # Apply the NYSE breakpoint to all eligible exchanges.
    df["in_universe"] = (
        eligible
        & df["me"].notna()
        & df["nyse_p20"].notna()
        & (df["me"] >= df["nyse_p20"])
    ).astype(bool)

    # Return exactly the columns required by the contract.
    out = df[
        [
            "permno", "month", "ret_total", "exret",
            "me", "exchcd", "shrcd", "in_universe"
        ]
    ].rename(columns={"ret_total": "ret"})

    out["permno"] = out["permno"].astype("int64")

    return out.sort_values(["permno", "month"]).reset_index(drop=True)



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


# ---------------------------------------------------------------- extension and report additions

def pull_earnings_dates(db, start: str, end: str) -> pd.DataFrame:
    """EXTENSION (cash-flow news test, used by Member 4): quarterly earnings announcement dates.

    Compustat quarterly fundamentals (comp.fundq: gvkey, datadate, rdq) linked to CRSP permno with the
    CRSP-Compustat merged link table (crsp.ccmxpf_linktable or crsp.ccmxpf_lnkhist; keep linktype in
    ('LU','LC') and linkprim in ('P','C'), with rdq between linkdt and linkenddt).
    Return the earnings_dates contract: permno, rdq (datetime). Drop missing rdq and duplicates.
    """
    raise NotImplementedError("Member 2: earnings announcement dates")


def summary_stats(crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """REPORT (guideline: 'Table of summary statistics'): by decade or full sample, the number of
    universe stocks per month (mean, min, max), mean/median/sd of monthly exret, median market cap.
    Save with lrrep.io.save_table(df, 'summary_stats')."""
    raise NotImplementedError("Member 2: summary statistics table")
