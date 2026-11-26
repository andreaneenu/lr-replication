"""Firm characteristics: download, merge to CRSP, clean (paper Section 3.1).

Owner: Member 5. Reads: crsp_monthly, raw Chen-Zimmermann signals. Writes: chars_clean.
Spec: docs/members/member-5.md

Source: Open Source Asset Pricing (openassetpricing.com), Chen and Zimmermann. Download
the firm-level signals file (permno x yyyymm, one column per signal) into the shared data
folder under raw/chars/. Do not commit it.

Timing: Chen-Zimmermann signals at yyyymm are already lagged so they are known by the end of
that month and are used to predict the return in the NEXT month. Map yyyymm to the month-end
of that month as our formation month t. Do NOT shift again. Write one sentence in
docs/status/member-5.md confirming how you verified this.

Cleaning (paper Section 3.1, adapted):
 - Keep stock-months with in_universe == True at t.
 - Keep a characteristic in a training window only if it is non-missing for at least
   CFG['forecast']['min_coverage'] of rows in that window (the paper drops >10% missing).
 - Fill remaining missing values with that month's cross-sectional median.
 - Standardize each characteristic cross-sectionally each month (rank to [-1, 1] or z-score;
   pick one and document it). Name columns c_<signal>.
 - For the 6-day plan, start with signals that have good coverage from 1970 on (expect 50-100).
 - EXTENSION: check on day 1 the LAST month covered by the latest Chen-Zimmermann release; it sets
   CFG sample.end together with CRSP's last month. Tell Member 1 so config.yaml can be updated.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from lrrep.config import CFG
from lrrep.io import load, save, save_table

# Signed file: every signal is multiplied by its sign, so higher = higher expected return.
RAW_FILE = "signed_predictors_dl_wide.parquet"
COVERAGE_FROM = "1970-01"   # judge coverage from 1970 on (member brief)
# Best-known signals for the report table (Chen-Zimmermann names; Size comes from CRSP, see below)
KNOWN = ["Size", "BM", "Mom12m", "GP", "AssetGrowth", "OperProf", "Accruals", "EP", "ShareIss1Y", "IdioVol3F"]


def _month_from_yyyymm(x: pd.Series) -> pd.Series:
    return pd.to_datetime(x.astype(int).astype(str), format="%Y%m") + pd.offsets.MonthEnd(0)


def load_raw_signals(raw_dir, keep: pd.DataFrame | None = None, batch: int = 25) -> pd.DataFrame:
    """Read the Chen-Zimmermann firm-level signals. Return permno, month (month-end), <signals>.

    Months run from CFG sample.history_start to CFG sample.end (the file also has carried-forward
    rows into later years with half the stocks and ~50 signals; those are dropped).
    `keep` (permno, month) limits the rows read, e.g. to the universe; columns are read in batches
    as float32 so the 1.9 GB file fits in memory."""
    path = Path(raw_dir) / RAW_FILE
    pf = pq.ParquetFile(path)
    sig = [c for c in pf.schema_arrow.names if c not in ("permno", "yyyymm")]
    ids = pd.read_parquet(path, columns=["permno", "yyyymm"])
    ids["permno"] = ids["permno"].astype("int64")
    ids["month"] = _month_from_yyyymm(ids["yyyymm"])
    s = CFG["sample"]
    lo = pd.Timestamp(s["history_start"]) + pd.offsets.MonthEnd(0)
    hi = pd.Timestamp(s["end"]) + pd.offsets.MonthEnd(0)
    mask = ids["month"].between(lo, hi).to_numpy()
    if keep is not None:
        k = keep[["permno", "month"]].drop_duplicates().assign(_k=True)
        mask = mask & ids[["permno", "month"]].merge(k, on=["permno", "month"], how="left")["_k"].notna().to_numpy()
    parts = [ids.loc[mask, ["permno", "month"]].reset_index(drop=True)]
    for i in range(0, len(sig), batch):
        part = pd.read_parquet(path, columns=sig[i:i + batch])
        parts.append(part.loc[mask].astype("float32").replace([np.inf, -np.inf], np.nan).reset_index(drop=True))
        del part
    out = pd.concat(parts, axis=1)
    print(f"chars: read {len(out):,} stock-months x {len(sig)} signals, "
          f"{out.month.min():%Y-%m}..{out.month.max():%Y-%m}")
    return out


def add_crsp_signals(signals: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Size and STreversal are CRSP-based and missing from the public file; rebuild them from
    crsp_monthly with the same signs (both known at the end of month t):
    Size = -log(me) (small stocks earn more), STreversal = -ret_t (last month's losers rebound).
    Price is skipped: crsp_monthly has no price column."""
    c = crsp_monthly[["permno", "month", "me", "ret"]].copy()
    c["Size"] = (-np.log(c["me"].where(c["me"] > 0))).astype("float32")
    c["STreversal"] = (-c["ret"]).astype("float32")
    return signals.merge(c[["permno", "month", "Size", "STreversal"]], on=["permno", "month"], how="left")


def signal_coverage(signals: pd.DataFrame) -> pd.Series:
    """Share of (universe) stock-months from COVERAGE_FROM on where each signal is non-missing."""
    sig = [c for c in signals.columns if c not in ("permno", "month")]
    recent = signals[signals["month"] >= pd.Timestamp(COVERAGE_FROM)]
    return recent[sig].notna().mean().sort_values(ascending=False)


def select_signals(signals: pd.DataFrame) -> list[str]:
    """Keep every signal that could pass the paper's per-window rule somewhere: non-missing for at
    least min_coverage of stock-months in some 5-year (60-month) window since 1970. The rule itself
    is applied window by window in models.rolling_forecasts, so e.g. book-to-market enters once its
    coverage is good enough, as in the paper."""
    sig = [c for c in signals.columns if c not in ("permno", "month")]
    recent = signals[signals["month"] >= pd.Timestamp(COVERAGE_FROM)]
    w = CFG["forecast"]["train_months"]
    by_month = recent.groupby("month")[sig].apply(lambda g: g.notna().sum()).astype(float)
    n = recent.groupby("month").size().astype(float)
    best = (by_month.rolling(w).sum().div(n.rolling(w).sum(), axis=0)).max()
    keep = best[best >= CFG["forecast"]["min_coverage"]].sort_values(ascending=False).index.tolist()
    always = signal_coverage(signals[["permno", "month", *keep]])
    print(f"chars: {len(keep)} of {len(sig)} signals reach {CFG['forecast']['min_coverage']:.0%} coverage in some "
          f"{w}-month window; {int((always >= CFG['forecast']['min_coverage']).sum())} of them over all of 1970+")
    return keep


def rank_standardize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Each month, map each signal to [-1, 1] by cross-sectional rank: 2*(rank-1)/(n-1) - 1.
    Uses only that month's stocks (no look-ahead). Missing values stay NaN here: the forecasting
    step drops low-coverage signals per training window and fills the rest with 0, the median rank."""
    g = df.groupby("month")[cols]
    r = g.rank(method="average")
    n = g.transform("count")
    z = 2.0 * (r - 1.0) / (n - 1.0).where(n > 1) - 1.0   # NaN where the value is missing
    z = z.mask(r.notna() & (n <= 1), 0.0).astype("float32")  # a lone stock in a month gets the middle
    z.columns = [f"c_{c}" for c in cols]
    return z


def clean(signals: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Merge to the universe, drop low-coverage signals, fill medians, standardize per month.
    Return the chars_clean contract frame (permno, month, c_* float columns)."""
    uni = crsp_monthly.loc[crsp_monthly["in_universe"], ["permno", "month"]]
    df = signals.merge(uni, on=["permno", "month"], how="inner")
    if "Size" not in df.columns:
        df = add_crsp_signals(df, crsp_monthly)
    keep = select_signals(df)
    df = df.sort_values(["month", "permno"]).reset_index(drop=True)
    out = pd.concat([df[["permno", "month"]], rank_standardize(df, keep)], axis=1)
    print(f"chars_clean: {len(out):,} rows, {len(keep)} characteristics, "
          f"{out.month.min():%Y-%m}..{out.month.max():%Y-%m}")
    return out


def characteristics_summary(chars_raw: pd.DataFrame) -> pd.DataFrame:
    """REPORT: number of characteristics used, coverage over time, and for the 10 best-known ones
    (size, book-to-market, momentum, profitability, investment, ...) mean/sd/percentiles of the raw
    values. Save as summary_chars."""
    known = [k for k in KNOWN if k in chars_raw.columns]
    q = [0.01, 0.25, 0.5, 0.75, 0.99]
    rows = []
    for k in known:
        x = chars_raw[k].astype("float64")
        r = {"signal": k, "coverage": x.notna().mean(), "mean": x.mean(), "sd": x.std()}
        r.update({f"p{int(p * 100)}": v for p, v in zip(q, x.quantile(q), strict=True)})
        rows.append(r)
    stats = pd.DataFrame(rows).set_index("signal")
    save_table(stats, "summary_chars")
    # coverage over time: stocks per month and share of signals present, by decade
    sig = [c for c in chars_raw.columns if c not in ("permno", "month")]
    d = chars_raw[["month"]].copy()
    d["signals_present"] = chars_raw[sig].notna().mean(axis=1)
    d["decade"] = (d["month"].dt.year // 10) * 10
    per_month = d.groupby(["decade", "month"]).agg(stocks=("signals_present", "size"),
                                                   share=("signals_present", "mean"))
    cov = per_month.groupby("decade").agg(avg_stocks_per_month=("stocks", "mean"),
                                          avg_share_of_signals_present=("share", "mean"))
    save_table(cov, "summary_chars_coverage")
    return stats


def run(fake: bool = False) -> None:
    if fake:
        print("chars: fake chars_clean comes from `make fake`; nothing to do")
        return
    from lrrep.config import data_dir

    crsp = load("crsp_monthly", columns=["permno", "month", "me", "ret", "in_universe"])
    uni = crsp.loc[crsp["in_universe"], ["permno", "month"]]
    raw = add_crsp_signals(load_raw_signals(data_dir() / "raw" / "chars", keep=uni), crsp)
    characteristics_summary(raw)
    save(clean(raw, crsp), "chars_clean")
