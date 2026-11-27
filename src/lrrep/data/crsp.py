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


def pull_monthly(db, start: str, end: str) -> pd.DataFrame:
    """Monthly stock file joined to names (share code, exchange code) for [start, end].

    Return columns: permno, month (month-end), ret, prc, shrout, shrcd, exchcd, dlret.
    - Keep shrcd in CFG['universe']['shrcd'] and exchcd in CFG['universe']['exchcd'],
      using the names record valid on that date (namedt <= date <= nameendt).
    - Merge delisting returns (dlret) in the delisting month.
    """

    query = """
        SELECT
            m.permno,
            m.date AS month,
            m.ret,
            m.prc,
            m.shrout,
            n.shrcd,
            n.exchcd,
            d.dlret
        FROM crsp.msf AS m

        LEFT JOIN crsp.msenames AS n
            ON m.permno = n.permno
            AND m.date >= n.namedt
            AND m.date <= n.nameendt

        LEFT JOIN crsp.msedelist AS d
            ON m.permno = d.permno
            AND DATE_TRUNC('month', m.date)
                = DATE_TRUNC('month', d.dlstdt)

        WHERE m.date BETWEEN %(start)s AND %(end)s

        ORDER BY m.permno, m.date
    """

    df = db.raw_sql(
        query,
        params={
            "start": start,
            "end": end,
        },
        date_cols=["month"],
    )

    df["month"] = (
        pd.to_datetime(df["month"])
        + pd.offsets.MonthEnd(0)
    )

    if df.duplicated(["permno", "month"]).any():
        raise ValueError(
            "Duplicate legacy CRSP stock-month observations"
        )

    return df[
        [
            "permno", "month", "ret", "prc",
            "shrout", "shrcd", "exchcd", "dlret"
        ]
    ]



def pull_daily(db, permnos: list[int], start: str, end: str) -> pd.DataFrame:
    """Daily returns for the given permnos. Return columns: permno, date, ret.

    Tip: the daily file is large. Pull year by year and only for permnos that are ever
    in the universe. Expect roughly 15-25 million rows for 1965-2021 after filters.
    """

    if not permnos:
        return pd.DataFrame(
            columns=["permno", "date", "ret"]
        )

    query = """
        SELECT
            permno,
            dlycaldt AS date,
            dlyret AS ret
        FROM crsp.dsf_v2
        WHERE dlycaldt BETWEEN %(start)s AND %(end)s
          AND permno = ANY(%(permnos)s)
        ORDER BY permno, dlycaldt
    """

    df = db.raw_sql(
        query,
        params={
            "start": start,
            "end": end,
            "permnos": [int(p) for p in permnos],
        },
        date_cols=["date"],
    )

    if df.duplicated(["permno", "date"]).any():
        raise ValueError("Duplicate daily CRSP observations")

    return df



def pull_risk_free_and_market() -> pd.DataFrame:
    """Monthly and daily risk-free rate and market excess return from the Ken French library.

    Return a monthly frame: month, mkt_exret, rf (decimals, not percent) and keep the daily
    rf series for crsp_daily. Source: F-F_Research_Data_Factors (monthly and daily).
    """

    from io import BytesIO
    from urllib.request import urlopen
    from zipfile import ZipFile

    url = (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/"
        "ftp/F-F_Research_Data_Factors_CSV.zip"
    )

    # Download the official Fama-French factor archive.
    with urlopen(url, timeout=60) as response:
        archive = response.read()

    with ZipFile(BytesIO(archive)) as z:
        csv_name = next(
            name for name in z.namelist()
            if name.lower().endswith(".csv")
        )
        content = z.read(csv_name).decode("utf-8-sig")

    # Identify the monthly section of the file.
    # Monthly observations have a six-digit YYYYMM identifier.
    records = []
    started = False

    for line in content.splitlines():
        fields = [part.strip() for part in line.split(",")]
        period = fields[0]

        if len(period) == 6 and period.isdigit():
            started = True
            if len(fields) >= 5:
                records.append(
                    (period, fields[1], fields[4])
                )
        elif started:
            # The monthly section has ended.
            break

    if not records:
        raise ValueError("No monthly Fama-French observations found")

    market = pd.DataFrame(
        records, columns=["period", "mkt_exret", "rf"]
    )

    # Convert YYYYMM into calendar month-end timestamps.
    market["month"] = (
        pd.to_datetime(market["period"], format="%Y%m")
        + pd.offsets.MonthEnd(0)
    )

    # French Library returns are percentages, not decimals.
    for col in ["mkt_exret", "rf"]:
        market[col] = pd.to_numeric(
            market[col], errors="raise"
        ) / 100

    market = market[
        ["month", "mkt_exret", "rf"]
    ].sort_values("month").reset_index(drop=True)

    # Basic data-integrity checks.
    if market["month"].duplicated().any():
        raise ValueError("Duplicate months in market data")

    if market[["mkt_exret", "rf"]].isna().any().any():
        raise ValueError("Missing market or risk-free returns")

    return market



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

    # Avoid modifying the original datasets.
    daily = dsf.copy()
    rf = rf_daily.copy()

    # Standardize dates.
    daily["date"] = pd.to_datetime(daily["date"])
    rf["date"] = pd.to_datetime(rf["date"])

    # Validate observation keys.
    if daily.duplicated(["permno", "date"]).any():
        raise ValueError("Duplicate daily CRSP observations")

    if rf.duplicated(["date"]).any():
        raise ValueError("Duplicate daily risk-free observations")

    # Identify stocks that enter the universe at least once.
    eligible_permnos = monthly.loc[
        monthly["in_universe"].fillna(False), "permno"
    ].unique()

    # Preserve all available historical returns for these stocks.
    daily = daily[
        daily["permno"].isin(eligible_permnos)
    ].copy()

    # Convert returns to numeric values.
    daily["ret"] = pd.to_numeric(
        daily["ret"], errors="coerce"
    )

    rf["rf"] = pd.to_numeric(
        rf["rf"], errors="coerce"
    )

    # Missing daily returns cannot be used for factor estimation.
    daily = daily.dropna(subset=["ret"])

    # Merge daily risk-free rates.
    daily = daily.merge(
        rf[["date", "rf"]],
        on="date",
        how="left",
        validate="many_to_one"
    )

    if daily["rf"].isna().any():
        raise ValueError(
            "Missing risk-free rates for some trading days"
        )

    # Daily excess returns.
    daily["exret"] = daily["ret"] - daily["rf"]

    # Match the required contract.
    out = daily[
        ["permno", "date", "ret", "rf", "exret"]
    ].copy()

    out["permno"] = out["permno"].astype("int64")

    return out.sort_values(
        ["permno", "date"]
    ).reset_index(drop=True)




def check_local_data(fake: bool = False) -> None:
    """Validate locally available Member 2 datasets.

    Fake datasets are generated separately by `make fake`.
    Real datasets must already exist locally or be synced
    from the team's restricted OneDrive folder.

    This function does not connect to WRDS or overwrite data.
    """
    import pyarrow.parquet as pq

    from lrrep.contracts import validate
    from lrrep.io import load

    if fake:
        print("crsp: fake files come from `make fake`; nothing to do")
        return

    print("Checking locally available Member 2 datasets...")

    # Validate the smaller monthly datasets.
    for name in ["market", "crsp_monthly"]:
        df = load(name, fake=False)
        validate(df, name)

        print(
            f"{name}: VALIDATED "
            f"({len(df):,} observations)"
        )

    # Inspect daily file metadata without loading 48 million
    # observations into memory.
    from lrrep.io import path_for

    daily_path = path_for("crsp_daily", fake=False)

    if not daily_path.exists():
        raise FileNotFoundError(
            f"Missing daily CRSP dataset: {daily_path}"
        )

    daily_file = pq.ParquetFile(daily_path)

    expected = ["permno", "date", "ret", "rf", "exret"]

    if daily_file.schema_arrow.names != expected:
        raise ValueError(
            "Daily CRSP dataset has incorrect columns"
        )

    print(
        f"crsp_daily: SCHEMA CHECK PASSED "
        f"({daily_file.metadata.num_rows:,} observations)"
    )

    print("\nMember 2 local dataset checks completed.")




def run(fake: bool = False) -> None:
    """Run available Member 2 extraction workflows safely.

    Existing datasets are never overwritten. Monthly data
    must be available before daily extraction can begin.

    Earnings dates remain pending authorized CCM access.
    """
    if fake:
        print("crsp: fake files come from `make fake`; nothing to do")
        return

    from lrrep.contracts import validate
    from lrrep.io import load, path_for, save

    market_path = path_for("market", fake=False)
    monthly_path = path_for("crsp_monthly", fake=False)
    daily_path = path_for("crsp_daily", fake=False)
    earnings_path = path_for("earnings_dates", fake=False)

    # Market data are public and do not require WRDS.
    if market_path.exists():
        validate(load("market"), "market")
        print("market: existing dataset validated")
    else:
        market = pull_risk_free_and_market()
        save(market, "market")
        print("market: downloaded and saved")

    # Import extraction scripts only when needed.
    if monthly_path.exists():
        validate(load("crsp_monthly"), "crsp_monthly")
        print("crsp_monthly: existing dataset validated")
    else:
        from scripts.download_crsp_monthly import download_monthly
        download_monthly()
        print("crsp_monthly: extraction complete")

    if daily_path.exists():
        print(
            "crsp_daily: existing file found; "
            "run check_local_data() for schema validation"
        )
    else:
        from scripts.download_crsp_daily import download_daily
        download_daily()
        print("crsp_daily: extraction complete")

    if earnings_path.exists():
        validate(load("earnings_dates"), "earnings_dates")
        print("earnings_dates: existing dataset validated")
    else:
        print(
            "earnings_dates: unavailable. "
            "Requires authorized WRDS CCM access."
        )

    print("Member 2 pipeline finished.")


# ---------------------------------------------------------------- extension and report additions

def pull_earnings_dates(db, start: str, end: str) -> pd.DataFrame:
    """EXTENSION (cash-flow news test, used by Member 4): quarterly earnings announcement dates.

    Compustat quarterly fundamentals (comp.fundq: gvkey, datadate, rdq) linked to CRSP permno with the
    CRSP-Compustat merged link table (crsp.ccmxpf_linktable or crsp.ccmxpf_lnkhist; keep linktype in
    ('LU','LC') and linkprim in ('P','C'), with rdq between linkdt and linkenddt).
    Return the earnings_dates contract: permno, rdq (datetime). Drop missing rdq and duplicates.
    """

    query = """
        SELECT DISTINCT
            l.lpermno AS permno,
            f.rdq
        FROM comp.fundq AS f
        INNER JOIN crsp.ccmxpf_lnkhist AS l
            ON TRIM(f.gvkey) = TRIM(l.gvkey)
            AND f.rdq >= l.linkdt
            AND (
                l.linkenddt IS NULL
                OR f.rdq <= l.linkenddt
            )
        WHERE f.rdq BETWEEN %(start)s AND %(end)s
          AND f.rdq IS NOT NULL
          AND l.lpermno IS NOT NULL
          AND l.linktype IN ('LU', 'LC')
          AND l.linkprim IN ('P', 'C')
        ORDER BY permno, rdq
    """

    df = db.raw_sql(
        query,
        params={
            "start": start,
            "end": end,
        },
        date_cols=["rdq"],
    )

    # Standardize data types.
    df["permno"] = pd.to_numeric(
        df["permno"], errors="coerce"
    )

    df["rdq"] = pd.to_datetime(
        df["rdq"], errors="coerce"
    )

    # Remove missing identifiers and dates.
    df = df.dropna(
        subset=["permno", "rdq"]
    ).copy()

    # A security can have multiple Compustat records
    # referring to the same earnings announcement.
    df = df.drop_duplicates(
        subset=["permno", "rdq"]
    )

    # Match the required contract types.
    df["permno"] = df["permno"].astype("int64")

    df = df.sort_values(
        ["permno", "rdq"]
    ).reset_index(drop=True)

    return df[["permno", "rdq"]]



def summary_stats(crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """REPORT (guideline: 'Table of summary statistics'): by decade or full sample, the number of
    universe stocks per month (mean, min, max), mean/median/sd of monthly exret, median market cap.
    Save with lrrep.io.save_table(df, 'summary_stats')."""

    df = crsp_monthly.copy()

    # Restrict statistics to the eligible investment universe.
    df = df.loc[df["in_universe"].fillna(False)].copy()

    if df.empty:
        raise ValueError("No eligible stock-month observations")

    df["month"] = pd.to_datetime(df["month"])
    df["decade"] = (df["month"].dt.year // 10) * 10

    # Ensure one observation per stock and month.
    if df.duplicated(["permno", "month"]).any():
        raise ValueError("Duplicate stock-month observations")

    # Count eligible stocks in each month.
    monthly_counts = (
        df.groupby(["decade", "month"])["permno"]
        .nunique()
        .reset_index(name="n_stocks")
    )

    count_stats = (
        monthly_counts.groupby("decade")["n_stocks"]
        .agg(
            mean_stocks="mean",
            min_stocks="min",
            max_stocks="max"
        )
    )

    # Cross-sectional stock-month statistics by decade.
    return_stats = (
        df.groupby("decade")
        .agg(
            mean_exret=("exret", "mean"),
            median_exret=("exret", "median"),
            sd_exret=("exret", "std"),
            median_me_millions=("me", "median"),
            n_stock_months=("permno", "size")
        )
    )

    summary = count_stats.join(return_stats).reset_index()

    return summary.sort_values("decade").reset_index(drop=True)


def pull_daily_risk_free() -> pd.DataFrame:
    """Download daily Fama-French risk-free rates.

    Returns
    -------
    pd.DataFrame
        Columns: date, rf.
        Dates are trading days and returns are decimals.
    """
    from io import BytesIO
    from urllib.request import urlopen
    from zipfile import ZipFile

    url = (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/"
        "ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    )

    # Download the official Fama-French daily factor archive.
    with urlopen(url, timeout=60) as response:
        archive = response.read()

    with ZipFile(BytesIO(archive)) as z:
        csv_name = next(
            name for name in z.namelist()
            if name.lower().endswith(".csv")
        )
        content = z.read(csv_name).decode("utf-8-sig")

    # Daily observations use an eight-digit YYYYMMDD identifier.
    records = []
    started = False

    for line in content.splitlines():
        fields = [part.strip() for part in line.split(",")]
        period = fields[0]

        if len(period) == 8 and period.isdigit():
            started = True

            if len(fields) < 5:
                raise ValueError(
                    f"Invalid Fama-French daily row: {line}"
                )

            records.append((period, fields[4]))

        elif started:
            break

    if not records:
        raise ValueError("No daily Fama-French observations found")

    daily_rf = pd.DataFrame(
        records, columns=["date", "rf"]
    )

    # Convert dates and percentage returns.
    daily_rf["date"] = pd.to_datetime(
        daily_rf["date"], format="%Y%m%d"
    )

    daily_rf["rf"] = (
        pd.to_numeric(daily_rf["rf"], errors="raise") / 100
    )

    daily_rf = daily_rf.sort_values(
        "date"
    ).reset_index(drop=True)

    # Validate the resulting daily series.
    if daily_rf["date"].duplicated().any():
        raise ValueError("Duplicate daily risk-free dates")

    if daily_rf["rf"].isna().any():
        raise ValueError("Missing daily risk-free observations")

    return daily_rf



def pull_monthly_ciz(db, start: str, end: str) -> pd.DataFrame:
    """Download raw CRSP CIZ monthly stock observations.

    Parameters
    ----------
    db : wrds.Connection
        Active WRDS connection.
    start, end : str
        Inclusive dates in YYYY-MM-DD format.

    Returns
    -------
    pd.DataFrame
        Raw CIZ observations, without universe filters.
    """
    query = """
        SELECT
            permno,
            mthcaldt,
            mthret,
            mthprc,
            shrout,
            mthcap,
            securitytype,
            securitysubtype,
            sharetype,
            primaryexch,
            mthdelflg
        FROM crsp.msf_v2
        WHERE mthcaldt BETWEEN %(start)s AND %(end)s
        ORDER BY permno, mthcaldt
    """

    df = db.raw_sql(
        query,
        params={"start": start, "end": end},
        date_cols=["mthcaldt"],
    )

    if df.duplicated(["permno", "mthcaldt"]).any():
        raise ValueError("Duplicate CIZ stock-month observations")

    return df


def build_monthly_ciz(
    raw: pd.DataFrame,
    names: pd.DataFrame,
    market: pd.DataFrame,
) -> pd.DataFrame:
    """Convert CIZ monthly data to the crsp_monthly contract.

    Uses historical legacy share/exchange codes where available.
    Unmatched classifications receive -1 and are ineligible.
    This implementation is intended for periods with legacy
    names coverage; 2025 requires a separate documented rule.
    """
    from lrrep.contracts import validate

    raw = raw.copy()
    names = names.copy()
    market = market.copy()

    # Standardize dates.
    raw["mthcaldt"] = pd.to_datetime(raw["mthcaldt"])
    raw["month"] = (
        raw["mthcaldt"] + pd.offsets.MonthEnd(0)
    )

    names["namedt"] = pd.to_datetime(names["namedt"])
    names["nameendt"] = pd.to_datetime(names["nameendt"])

    market["month"] = (
        pd.to_datetime(market["month"])
        + pd.offsets.MonthEnd(0)
    )

    # Validate input keys.
    if raw.duplicated(["permno", "month"]).any():
        raise ValueError("Duplicate CIZ stock-month observations")

    if market.duplicated(["month"]).any():
        raise ValueError("Duplicate market months")

    # Match historical classifications.
    joined = raw.merge(
        names[
            ["permno", "namedt", "nameendt", "shrcd", "exchcd"]
        ],
        on="permno",
        how="left",
    )

    valid = (
        (joined["mthcaldt"] >= joined["namedt"])
        & (joined["mthcaldt"] <= joined["nameendt"])
    )

    matched = joined.loc[valid].copy()

    if matched.duplicated(["permno", "month"]).any():
        raise ValueError(
            "Multiple historical classifications for a stock-month"
        )

    # Preserve observations without historical classifications.
    matched_keys = matched[["permno", "month"]]

    unmatched = raw.merge(
        matched_keys,
        on=["permno", "month"],
        how="left",
        indicator=True,
    )

    unmatched = unmatched.loc[
        unmatched["_merge"] == "left_only"
    ].copy()

    unmatched["shrcd"] = -1
    unmatched["exchcd"] = -1

    df = pd.concat(
        [matched, unmatched],
        ignore_index=True,
    )

    # Financial variables.
    df["ret"] = pd.to_numeric(
        df["mthret"], errors="coerce"
    ).astype("float64")

    df["me"] = (
        pd.to_numeric(df["mthcap"], errors="coerce")
        / 1000
    ).astype("float64")

    # Merge monthly risk-free rates.
    df = df.merge(
        market[["month", "rf"]],
        on="month",
        how="left",
        validate="many_to_one",
    )

    if df["rf"].isna().any():
        raise ValueError("Missing monthly risk-free rates")

    df["exret"] = (
        df["ret"] - df["rf"]
    ).astype("float64")

    # Investment eligibility.
    eligible = (
        df["shrcd"].isin([10, 11])
        & df["exchcd"].isin([1, 2, 3])
    )

    # NYSE 20th-percentile market capitalization.
    nyse = df.loc[
        df["shrcd"].isin([10, 11])
        & (df["exchcd"] == 1)
        & (df["me"] > 0)
    ]

    breakpoints = (
        nyse.groupby("month")["me"]
        .quantile(0.20)
        .rename("nyse_p20")
    )

    df = df.join(breakpoints, on="month")

    df["in_universe"] = (
        eligible
        & (df["me"] > 0)
        & df["nyse_p20"].notna()
        & (df["me"] >= df["nyse_p20"])
    ).fillna(False).astype(bool)

    # Exact contract columns and types.
    out = df[
        [
            "permno", "month", "ret", "exret",
            "me", "exchcd", "shrcd", "in_universe"
        ]
    ].copy()

    out["permno"] = out["permno"].astype("int64")
    out["shrcd"] = out["shrcd"].fillna(-1).astype("int64")
    out["exchcd"] = out["exchcd"].fillna(-1).astype("int64")

    for col in ["ret", "exret", "me"]:
        out[col] = out[col].astype("float64")

    out = out.sort_values(
        ["permno", "month"]
    ).reset_index(drop=True)

    if len(out) != len(raw):
        raise ValueError(
            "Stock-month observations were lost or duplicated"
        )

    validate(out, "crsp_monthly")
    return out
