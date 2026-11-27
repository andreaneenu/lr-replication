
"""Offline tests for Member 2 CRSP CIZ processing."""

import numpy as np
import pandas as pd
import pytest

from lrrep.contracts import validate
from lrrep.data.crsp import build_monthly_ciz


def sample_inputs():
    """Create small synthetic CIZ and legacy classification data."""
    raw = pd.DataFrame({
        "permno": [101, 102, 103, 104, 105, 106],
        "mthcaldt": pd.to_datetime(["2020-01-31"] * 6),
        "mthret": [0.10, -0.05, 0.03, 0.08, np.nan, 0.04],
        "mthcap": [10000, 20000, 30000, 40000, 50000, 60000],
    })

    names = pd.DataFrame({
        "permno": [101, 102, 103, 104, 105],
        "namedt": pd.to_datetime(["2019-01-01"] * 5),
        "nameendt": pd.to_datetime(["2020-12-31"] * 5),
        "shrcd": [10, 11, 10, 12, 11],
        "exchcd": [1, 1, 3, 1, 3],
    })

    market = pd.DataFrame({
        "month": pd.to_datetime(["2020-01-31"]),
        "rf": [0.005],
    })

    return raw, names, market


def test_ciz_contract_and_financial_calculations():
    raw, names, market = sample_inputs()

    out = build_monthly_ciz(raw, names, market)
    validate(out, "crsp_monthly")

    assert len(out) == 6
    assert not out.duplicated(["permno", "month"]).any()

    stocks = out.set_index("permno")

    # Market capitalization is in millions of dollars.
    assert np.isclose(stocks.loc[101, "me"], 10.0)

    # Excess return = total return - risk-free rate.
    assert np.isclose(stocks.loc[101, "exret"], 0.095)

    # Missing returns remain missing.
    assert pd.isna(stocks.loc[105, "ret"])

    # Missing classifications are marked with -1.
    assert stocks.loc[106, "shrcd"] == -1
    assert stocks.loc[106, "exchcd"] == -1

    # Invalid share code and unmatched securities are excluded.
    assert not stocks.loc[104, "in_universe"]
    assert not stocks.loc[106, "in_universe"]

    # NYSE market caps are 10 and 20 million for eligible
    # common stocks, so the 20th percentile is 12 million.
    assert not stocks.loc[101, "in_universe"]
    assert stocks.loc[102, "in_universe"]
    assert stocks.loc[103, "in_universe"]

    # Eligibility is independent of return availability.
    assert stocks.loc[105, "in_universe"]


def test_ciz_duplicate_stock_month_rejected():
    raw, names, market = sample_inputs()

    raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate"):
        build_monthly_ciz(raw, names, market)


def test_ciz_missing_risk_free_rejected():
    raw, names, market = sample_inputs()

    market = market.iloc[0:0].copy()

    with pytest.raises(ValueError, match="Missing monthly risk-free"):
        build_monthly_ciz(raw, names, market)


def test_ciz_multiple_classifications_rejected():
    raw, names, market = sample_inputs()

    duplicate = names.iloc[[0]].copy()
    names = pd.concat([names, duplicate], ignore_index=True)

    with pytest.raises(ValueError, match="Multiple historical classifications"):
        build_monthly_ciz(raw, names, market)
