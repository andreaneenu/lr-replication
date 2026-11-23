"""Cash-flow news vs discount-rate news: do the hedged portfolio's returns arrive at earnings announcements?

Owner: Member 4. Reads: portfolio_weights (Member 6), earnings_dates (Member 2), crsp_daily.
Writes: results/tables/cashflow_news.csv. Spec: docs/members/member-4.md

Guideline robustness item: "Discount rate vs. cash flow news. What drives the returns in your study?"
Approach (in the spirit of Engelberg, McLean and Pontiff 2018, "Anomalies and News"):
 - For each formation month t, take the weights w_bn (and w_ls) from portfolio_weights.
 - Over the holding month t+1, split each stock's daily returns into announcement days (within
   CFG['extension']['announcement_window'] trading days of an rdq) and other days.
 - Portfolio return from announcement days = sum_i w_i * (compounded exret of stock i on its
   announcement days); same for non-announcement days. (Using a sum of daily returns is fine.)
 - Report: average monthly return from announcement days vs other days, the share of the total that
   comes from announcement days, and the share of trading days that are announcement days
   (about 3 of 63 per quarter, ~5%). Newey-West t-stats with lrrep.stats.nw_mean_test.
Interpretation: if far more than ~5% of the hedged return arrives on ~5% of days, the return is
concentrated in cash-flow news (earnings surprises the market didn't expect): evidence for mispricing
corrected when news arrives, rather than compensation for risk (discount rates).
"""
from __future__ import annotations

import pandas as pd

from lrrep.io import load, save_table


def announcement_flags(crsp_daily: pd.DataFrame, earnings_dates: pd.DataFrame, window: tuple[int, int]) -> pd.Series:
    """Boolean Series aligned with crsp_daily: True if the day is within `window` trading days of an rdq
    for that permno (rdq on a non-trading day maps to the next trading day)."""
    raise NotImplementedError("Member 4: announcement-day flags")


def split_returns(weights: pd.DataFrame, crsp_daily: pd.DataFrame, flags: pd.Series) -> pd.DataFrame:
    """Per holding month: columns ret_ann_bn, ret_other_bn, ret_ann_ls, ret_other_ls, share_days_ann."""
    raise NotImplementedError("Member 4: split portfolio returns into announcement / other days")


def run(fake: bool = False) -> None:
    from lrrep.config import CFG

    daily, ed, w = load("crsp_daily", fake), load("earnings_dates", fake), load("portfolio_weights", fake)
    split = split_returns(w, daily, announcement_flags(daily, ed, tuple(CFG["extension"]["announcement_window"])))
    save_table(split.describe().T, "cashflow_news")
