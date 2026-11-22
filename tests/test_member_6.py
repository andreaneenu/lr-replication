"""Member 6 (main portfolios). On fake data, hedging should cut volatility a lot."""
from lrrep.io import load
from lrrep.portfolios.main_portfolios import portfolio_returns
from tests.conftest import todo


def test_hedging_cuts_volatility_on_fake(fake):
    mu, b, m = load("mu_hat", fake=True), load("betas_svd", fake=True), load("crsp_monthly", fake=True)
    with todo():
        ls = portfolio_returns(mu, b, m, "mu_rf", k=None)
        bn = portfolio_returns(mu, b, m, "mu_rf", k=10)
        assert bn.std() < 0.6 * ls.std()
        assert bn.mean() > 0
