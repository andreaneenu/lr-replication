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

import pandas as pd

from lrrep.io import load, save


def load_raw_signals(raw_dir) -> pd.DataFrame:
    """Read the Chen-Zimmermann firm-level signals. Return permno, month (month-end), <signals>."""
    raise NotImplementedError("Member 5: read raw signals")


def clean(signals: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Merge to the universe, drop low-coverage signals, fill medians, standardize per month.
    Return the chars_clean contract frame (permno, month, c_* float columns)."""
    raise NotImplementedError("Member 5: clean characteristics")


def characteristics_summary(chars_raw: pd.DataFrame) -> pd.DataFrame:
    """REPORT: number of characteristics used, coverage over time, and for the 10 best-known ones
    (size, book-to-market, momentum, profitability, investment, ...) mean/sd/percentiles of the raw
    values. Save as summary_chars."""
    raise NotImplementedError("Member 5: characteristics summary table")


def run(fake: bool = False) -> None:
    if fake:
        print("chars: fake chars_clean comes from `make fake`; nothing to do")
        return
    from lrrep.config import data_dir

    save(clean(load_raw_signals(data_dir() / "raw" / "chars"), load("crsp_monthly")), "chars_clean")
