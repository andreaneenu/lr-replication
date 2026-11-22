"""Member 5 (characteristics and forecasts)."""
import numpy as np
import pandas as pd

from lrrep.forecast.models import rolling_forecasts, training_pairs
from lrrep.io import load
from tests.conftest import todo


def test_pairs_use_next_month_return(fake):
    chars, monthly = load("chars_clean", fake=True), load("crsp_monthly", fake=True)
    with todo():
        pairs = training_pairs(chars, monthly)
        row = pairs.dropna(subset=["y"]).iloc[100]
        nxt = row["month"] + pd.offsets.MonthEnd(1)
        y = monthly[(monthly.permno == row["permno"]) & (monthly.month == nxt)]["exret"].item()
        assert np.isclose(row["y"], y)


def test_forecasts_ignore_the_future(fake):
    chars, monthly = load("chars_clean", fake=True), load("crsp_monthly", fake=True)
    t = pd.Timestamp("2005-06-30")
    with todo():
        full = rolling_forecasts(training_pairs(chars, monthly), chars, "ols")
        cut_m = monthly[monthly.month <= t]   # remove every return after t
        cut = rolling_forecasts(training_pairs(chars, cut_m), chars, "ols")
        at_t = (chars["month"] == t).to_numpy()
        assert np.allclose(full.to_numpy()[at_t], cut.to_numpy()[at_t], equal_nan=True)
