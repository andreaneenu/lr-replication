"""Member 3 (SVD betas). Runs once betas_for_month / compute_betas are implemented."""
import numpy as np
import pandas as pd

from lrrep.betas.svd import betas_for_month, compute_betas
from lrrep.contracts import validate
from lrrep.io import load
from lrrep.timing import assert_no_lookahead
from tests.conftest import todo


def _window(daily, end):
    end = pd.Timestamp(end)
    days = np.sort(daily["date"].unique())
    days = days[days <= end][-252:]
    return daily[daily["date"].isin(days)]


def test_betas_for_month_shapes_and_signs(fake):
    daily = load("crsp_daily", fake=True)
    with todo():
        betas, eig = betas_for_month(_window(daily, "2005-06-30"), k_max=20)
        assert {"permno", "beta_1", "beta_20"} <= set(betas.columns)
        assert (betas.filter(like="beta_").mean() > 0).all()          # sign normalization
        assert eig["share_explained"].sum() <= 1 + 1e-9
        assert eig["eigenvalue"].is_monotonic_decreasing
        # the fake world has 8 real factors: they should dominate the next 8
        top = eig.sort_values("k")["share_explained"].to_numpy()
        assert top[:8].sum() > 2 * top[8:16].sum()


def test_compute_betas_contract_and_no_lookahead(fake):
    daily, monthly = load("crsp_daily", fake=True), load("crsp_monthly", fake=True)
    daily = daily[daily["date"] < "2002-07-01"]
    monthly = monthly[monthly["month"] < "2002-07-01"]
    t = pd.Timestamp("2001-12-31")
    with todo():
        betas, eig = compute_betas(daily, monthly, months=[t])
        validate(betas, "betas_svd")
        validate(eig, "eigen")
        assert_no_lookahead(lambda crsp_daily, crsp_monthly: compute_betas(crsp_daily, crsp_monthly, months=[t])[0],
                            {"crsp_daily": daily, "crsp_monthly": monthly}, t, key=["permno", "month"])
