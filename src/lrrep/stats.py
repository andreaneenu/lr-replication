"""Shared statistics helpers: performance summaries, Newey-West, subperiods.

Owner: Member 1 (shared file). Used by Members 4, 6 and 7 so every table computes
Sharpe ratios and t-stats the same way.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from lrrep.config import CFG


def sharpe_annual(r: pd.Series) -> float:
    """Annualized Sharpe ratio of monthly EXCESS returns: mean/sd * sqrt(12)."""
    r = pd.Series(r).dropna()
    return float(r.mean() / r.std(ddof=1) * np.sqrt(12)) if len(r) > 1 else np.nan


def summarize(df: pd.DataFrame, cols: list[str] | None = None, pct: bool = True) -> pd.DataFrame:
    """Mean, Std. dev and annualized Sharpe ratio per column (paper Table 6 layout).

    Mean and Std. dev are monthly, in percent if pct=True.
    """
    cols = cols or [c for c in df.columns if c != "month"]
    scale = 100.0 if pct else 1.0
    out = {}
    for c in cols:
        r = df[c].dropna()
        out[c] = {"Mean": r.mean() * scale, "Std. dev": r.std(ddof=1) * scale, "Sharpe ratio": sharpe_annual(r), "N months": len(r)}
    return pd.DataFrame(out)


def subperiod(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    m = df["month"]
    return df[(m >= pd.Timestamp(start)) & (m <= pd.Timestamp(end) + pd.offsets.MonthEnd(0))]


def summarize_subperiods(df: pd.DataFrame, cols: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Table 6 panels: one summary per subperiod listed in config.yaml."""
    return {f"{s}..{e}": summarize(subperiod(df, s, e), cols) for s, e in CFG["tests"]["subperiods"]}


def nw_mean_test(x: pd.Series, lags: int | None = None) -> tuple[float, float]:
    """Mean of x and its Newey-West t-statistic."""
    lags = CFG["tests"]["newey_west_lags"] if lags is None else lags
    x = pd.Series(x).dropna()
    res = sm.OLS(x.to_numpy(), np.ones(len(x))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(res.params[0]), float(res.tvalues[0])


def time_series_regression(y: pd.Series, X: pd.DataFrame, lags: int | None = None):
    """OLS of y on a constant and X with Newey-West errors. Returns the statsmodels result."""
    lags = CFG["tests"]["newey_west_lags"] if lags is None else lags
    d = pd.concat([y.rename("y"), X], axis=1).dropna()
    return sm.OLS(d["y"], sm.add_constant(d.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
