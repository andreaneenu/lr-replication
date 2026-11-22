"""Look-ahead bias checks. Every member who writes a predictive file adds a test using these.

Owner: Member 1 (shared file).

The idea: a function that builds month-t outputs must give the SAME month-t rows whether
or not data after month t exists. `assert_no_lookahead` runs your function twice, once on
data truncated at month t and once on the full data, and compares the month-t rows.
"""
from __future__ import annotations

from typing import Callable

import pandas as pd


def truncate(df: pd.DataFrame, t: pd.Timestamp) -> pd.DataFrame:
    """Keep rows known by the end of month t (works for 'month' or 'date' keyed frames)."""
    t = pd.Timestamp(t) + pd.offsets.MonthEnd(0)
    col = "month" if "month" in df.columns else "date"
    return df[df[col] <= t]


def assert_no_lookahead(build: Callable[..., pd.DataFrame], inputs: dict[str, pd.DataFrame],
                        t: pd.Timestamp, key: list[str], atol: float = 1e-10) -> None:
    """Fail if build(**inputs) at month t changes when data after t is removed.

    build:  your function, e.g. lambda crsp_daily: compute_betas(crsp_daily, months=[t])
    inputs: the full input frames, by argument name
    key:    columns identifying a row of the output, e.g. ["permno", "month"]
    """
    t = pd.Timestamp(t) + pd.offsets.MonthEnd(0)
    full = build(**inputs)
    cut = build(**{k: truncate(v, t) for k, v in inputs.items()})
    a = full[full["month"] == t].sort_values(key).reset_index(drop=True)
    b = cut[cut["month"] == t].sort_values(key).reset_index(drop=True)
    if len(a) == 0:
        raise AssertionError(f"no output rows at {t.date()}: choose a month inside the sample")
    pd.testing.assert_frame_equal(a, b, check_exact=False, atol=atol,
                                  obj=f"month-{t.date()} output (full data vs data truncated at t)")
