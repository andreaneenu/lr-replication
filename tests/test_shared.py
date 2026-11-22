"""Tests for shared code (Member 1). These must always pass."""
import numpy as np
import pandas as pd
import pytest

from lrrep.contracts import CONTRACTS, ContractError, validate
from lrrep.io import load
from lrrep.portfolios.solver import expected_return_portfolio, factor_exposure_portfolio, solve_pure_play
from lrrep.stats import sharpe_annual, summarize


@pytest.mark.parametrize("name", sorted(CONTRACTS))
def test_fake_files_match_contracts(fake, name):
    validate(load(name, fake=True), name)


def test_contract_rejects_bad_frames():
    df = pd.DataFrame({"month": pd.to_datetime(["2001-03-15"]), "mkt_exret": [0.01], "rf": [0.001]})
    with pytest.raises(ContractError, match="month-end"):
        validate(df, "market")
    with pytest.raises(ContractError, match="missing column"):
        validate(df.drop(columns="rf"), "market")


def test_solver_meets_constraints():
    rng = np.random.default_rng(0)
    n, k = 500, 20
    mu, B = rng.normal(size=n), rng.normal(size=(n, k))
    w = expected_return_portfolio(mu, B)
    assert abs(w.sum()) < 1e-8
    assert np.allclose(B.T @ w, 0, atol=1e-8)
    assert w @ mu > 0
    assert np.isclose(np.abs(w).sum(), 2.0)
    wf = factor_exposure_portfolio(B, 3)
    expo = B.T @ wf
    assert abs(wf.sum()) < 1e-8 and expo[3] > 0 and np.allclose(np.delete(expo, 3), 0, atol=1e-8)


def test_solver_weighted_matches_closed_form():
    rng = np.random.default_rng(1)
    A, a0, om = rng.normal(size=(50, 3)), np.array([0.0, 1.0, 0.0]), rng.uniform(0.5, 2, 50)
    w = solve_pure_play(A, a0, om)
    Oi = np.diag(1 / om)
    assert np.allclose(w, Oi @ A @ np.linalg.solve(A.T @ Oi @ A, a0))


def test_stats():
    r = pd.Series([0.01, 0.02, -0.01, 0.03])
    assert np.isclose(sharpe_annual(r), r.mean() / r.std() * np.sqrt(12))
    s = summarize(pd.DataFrame({"month": pd.date_range("2000-01-31", periods=4, freq="ME"), "x": r}))
    assert np.isclose(s.loc["Mean", "x"], 1.25)
