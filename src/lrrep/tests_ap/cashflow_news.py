"""Cash-flow news vs discount-rate news: do the hedged portfolio's returns arrive at earnings announcements?

Owner: Member 4. Reads: portfolio_weights (Member 6), earnings_dates (Member 2), crsp_daily.
Writes: results/tables/cashflow_news.csv. Spec: docs/members/member-4.md

Guideline robustness item: "Discount rate vs. cash flow news. What drives the returns in your study?"
Approach (in the spirit of Engelberg, McLean and Pontiff 2018, "Anomalies and News"):
 - For each formation month t, take the weights w_bn (and w_ls) from portfolio_weights.
 - Over the holding month t+1, split each stock's daily returns into announcement days (within
   CFG['extension']['announcement_window'] trading days of an rdq) and other days.
 - Portfolio return from announcement days = sum_i w_i * (sum of exret of stock i on its
   announcement days); same for non-announcement days. (Using a sum of daily returns is fine.)
 - Report: average monthly return from announcement days vs other days, the share of the total that
   comes from announcement days, and the share of trading days that are announcement days
   (about 3 of 63 per quarter, ~5%). Newey-West t-stats with lrrep.stats.nw_mean_test.
Interpretation: if far more than ~5% of the hedged return arrives on ~5% of days, the return is
concentrated in cash-flow news (earnings surprises the market didn't expect): evidence for mispricing
corrected when news arrives, rather than compensation for risk (discount rates).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.io import load, save_table
from lrrep.stats import nw_mean_test


def announcement_flags(crsp_daily: pd.DataFrame, earnings_dates: pd.DataFrame, window: tuple[int, int]) -> pd.Series:
    """Boolean Series aligned with crsp_daily: True if the day is within `window` trading days of an rdq
    for that permno (rdq on a non-trading day maps to the next trading day)."""
    lo, hi = window
    cal = np.sort(crsp_daily["date"].unique())  # trading calendar
    pos_of_row = np.searchsorted(cal, crsp_daily["date"].to_numpy())

    ed = earnings_dates.dropna(subset=["rdq"])
    e_pos = np.searchsorted(cal, ed["rdq"].to_numpy(), side="left")  # first trading day on/after rdq
    ok = e_pos < len(cal)  # drop announcements after the last trading day
    permno = ed["permno"].to_numpy()[ok]
    e_pos = e_pos[ok]

    ev = [pd.MultiIndex.from_arrays([permno, e_pos + off]) for off in range(lo, hi + 1)]
    event_days = ev[0].append(ev[1:]).unique() if len(ev) > 1 else ev[0]
    rows = pd.MultiIndex.from_arrays([crsp_daily["permno"].to_numpy(), pos_of_row])
    return pd.Series(rows.isin(event_days), index=crsp_daily.index, name="is_announcement_day")


def split_returns(weights: pd.DataFrame, crsp_daily: pd.DataFrame, flags: pd.Series) -> pd.DataFrame:
    """Per holding month: columns ret_ann_bn, ret_other_bn, ret_ann_ls, ret_other_ls, share_days_ann."""
    d = crsp_daily[["permno", "date", "exret"]].copy()
    d["is_ann"] = flags.reindex(d.index).fillna(False).astype(bool).to_numpy()
    d["hold"] = d["date"] + pd.offsets.MonthEnd(0)             # month the return is realized
    d["month"] = d["hold"] - pd.offsets.MonthEnd(1)             # formation month t whose weights apply
    d["ann"] = d["exret"].where(d["is_ann"], 0.0)
    d["oth"] = d["exret"].where(~d["is_ann"], 0.0)
    g = (d.groupby(["permno", "month", "hold"])
          .agg(ann=("ann", "sum"), oth=("oth", "sum"), n_ann=("is_ann", "sum"), n_days=("is_ann", "size"))
          .reset_index())
    m = weights[["permno", "month", "w_ls", "w_bn"]].merge(g, on=["permno", "month"])
    out = pd.DataFrame(index=sorted(m["hold"].unique()))
    out.index.name = "month"
    for tag in ("bn", "ls"):
        w = m[f"w_{tag}"]
        out[f"ret_ann_{tag}"] = (w * m["ann"]).groupby(m["hold"]).sum()
        out[f"ret_other_{tag}"] = (w * m["oth"]).groupby(m["hold"]).sum()
    grp = m.groupby("hold")
    out["share_days_ann"] = grp["n_ann"].sum() / grp["n_days"].sum()
    return out


def summarize_split(split: pd.DataFrame) -> pd.DataFrame:
    """Table: for the beta-neutral (bn) and unhedged (ls) portfolios, average monthly return (% ) from
    announcement days vs other days with NW t-stats, and the share of the return on announcement days."""
    rows = {}
    for tag, label in (("bn", "Hedged (beta-neutral)"), ("ls", "Unhedged long-short")):
        a, o = split[f"ret_ann_{tag}"], split[f"ret_other_{tag}"]
        ma, ta = nw_mean_test(a)
        mo, to = nw_mean_test(o)
        mt, tt = nw_mean_test(a + o)
        rows[label] = {
            "Announcement days: mean % / month": ma * 100, "NW t (ann.)": ta,
            "Other days: mean % / month": mo * 100, "NW t (other)": to,
            "Total: mean % / month": mt * 100, "NW t (total)": tt,
            "Share of return on announcement days": ma / mt if mt else np.nan,
            "Share of trading days that are announcement days": split["share_days_ann"].mean(),
            "N months": len(split),
        }
    return pd.DataFrame(rows).T


def run(fake: bool = False) -> None:
    from lrrep.config import CFG

    daily, ed, w = load("crsp_daily", fake), load("earnings_dates", fake), load("portfolio_weights", fake)
    split = split_returns(w, daily, announcement_flags(daily, ed, tuple(CFG["extension"]["announcement_window"])))
    save_table(summarize_split(split), "cashflow_news")
