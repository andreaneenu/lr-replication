"""Member 4 (factor-exposure portfolios, Fama-MacBeth)."""
from lrrep.contracts import validate
from lrrep.io import load
from lrrep.portfolios.factor_exposure import build_factor_portfolios
from tests.conftest import todo


def test_factor_portfolios_on_fake(fake):
    with todo():
        fp = build_factor_portfolios(load("betas_svd", fake=True), load("crsp_monthly", fake=True), k=10)
        validate(fp, "factor_portfolios")
        # fake factors 2..8 have zero mean: their exposure portfolios should earn ~0
        assert fp[[f"fexp_{k}" for k in range(2, 9)]].mean().abs().max() < 0.01
