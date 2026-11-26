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


def _inputs():
    return load("mu_hat", fake=True), load("betas_svd", fake=True), load("crsp_monthly", fake=True)


def test_weights_satisfy_constraints(fake):
    import numpy as np

    from lrrep.portfolios.main_portfolios import formation_panel, main_weights
    mu, b, m = _inputs()
    with todo():
        w = main_weights(mu, b, m, "mu_rf", k=10)
        t = w["month"].iloc[len(w) // 2]
        g = w[w.month == t].merge(formation_panel(mu, b, m, "mu_rf", 10), on=["permno", "month"])
        for col in ["w_ls", "w_bn"]:
            assert abs(g[col].sum()) < 1e-8
            assert np.isclose(g[col].abs().sum(), 2.0)
            assert (g[col] @ g["mu"]) > 0
        B = g[[f"beta_{i}" for i in range(1, 11)]].to_numpy()
        assert np.abs(g["w_bn"].to_numpy() @ B).max() < 1e-8


def test_returns_stored_at_realization_month(fake):
    import numpy as np
    import pandas as pd

    from lrrep.portfolios.main_portfolios import main_weights
    mu, b, m = _inputs()
    with todo():
        r = portfolio_returns(mu, b, m, "mu_rf", k=10)
        w = main_weights(mu, b, m, "mu_rf", k=10)
        t = w["month"].iloc[len(w) // 2]
        nxt = t + pd.offsets.MonthEnd(1)
        g = w[w.month == t].merge(m[m.month == nxt][["permno", "exret"]], on="permno")
        assert np.isclose(r.loc[nxt], (g["w_bn"] * g["exret"]).sum())


def test_weights_no_lookahead(fake):
    """Weights formed at t may use mu and betas up to t, and only exret at t+1 (to pick held stocks,
    as in the spec). Removing everything later must not change them."""
    import pandas as pd

    from lrrep.portfolios.main_portfolios import main_weights
    from lrrep.timing import truncate
    mu, b, m = _inputs()
    t = pd.Timestamp("2006-06-30")
    with todo():
        full = main_weights(mu, b, m, "mu_rf", k=10)
        cut = main_weights(truncate(mu, t), truncate(b, t), truncate(m, t + pd.offsets.MonthEnd(1)), "mu_rf", k=10)
        a = full[full.month == t].reset_index(drop=True)
        c = cut[cut.month == t].reset_index(drop=True)
        assert len(a) > 0
        pd.testing.assert_frame_equal(a, c)


def test_turnover_bounds():
    import numpy as np
    import pandas as pd

    from lrrep.portfolios.costs import turnover
    t1, t2 = pd.Timestamp("2000-01-31"), pd.Timestamp("2000-02-29")
    same = pd.DataFrame({"permno": [1, 2, 1, 2], "month": [t1, t1, t2, t2], "w_ls": [1.0, -1.0, 1.0, -1.0]})
    swap = pd.DataFrame({"permno": [1, 2, 3, 4], "month": [t1, t1, t2, t2], "w_ls": [1.0, -1.0, 1.0, -1.0]})
    with todo():
        assert np.isclose(turnover(same, "w_ls").iloc[0], 0.0)
        assert np.isclose(turnover(swap, "w_ls").iloc[0], 2.0)    # full replacement of a $1/$1 book
        assert turnover(same, "w_ls").index[0] == pd.Timestamp("2000-03-31")   # realization month
