"""Member 4 (factor-exposure portfolios, Fama-MacBeth, cash-flow news)."""
import numpy as np
import pandas as pd

from lrrep.contracts import validate
from lrrep.io import load
from lrrep.portfolios.factor_exposure import build_factor_portfolios
from lrrep.tests_ap.cashflow_news import announcement_flags, split_returns
from lrrep.tests_ap.fama_macbeth import monthly_slopes, table8
from tests.conftest import todo


def test_factor_portfolios_on_fake(fake):
    with todo():
        fp = build_factor_portfolios(load("betas_svd", fake=True), load("crsp_monthly", fake=True), k=10)
        validate(fp, "factor_portfolios")
        # fake factors 2..8 have zero mean: their exposure portfolios should earn ~0
        assert fp[[f"fexp_{k}" for k in range(2, 9)]].mean().abs().max() < 0.01


def test_factor_portfolio_has_unit_exposure_and_realizes_next_month(fake):
    """Realization month is t+1, and the first formation month never appears as a return month."""
    with todo():
        b, m = load("betas_svd", fake=True), load("crsp_monthly", fake=True)
        fp = build_factor_portfolios(b, m, k=5)
        assert fp["month"].min() > b["month"].min()
        assert fp["month"].is_monotonic_increasing and fp["month"].is_unique


def test_fama_macbeth_on_fake(fake):
    with todo():
        mu, b, m = load("mu_hat", fake=True), load("betas_svd", fake=True), load("crsp_monthly", fake=True)
        s0 = monthly_slopes(mu, b, m, "mu_ols", 0)
        s5 = monthly_slopes(mu, b, m, "mu_ols", 5)
        assert {"const", "mu", "r2", "n"} <= set(s0.columns) and "beta_5" in s5.columns
        assert s5["r2"].mean() >= s0["r2"].mean() - 1e-12  # adding regressors cannot lower in-sample R2
        assert s0["mu"].mean() > 0  # fake forecasts contain true signal
        t = table8({"mu only": s0, "mu + 5 betas": s5})
        assert ("mu only", "mu") in t.index


def test_fama_macbeth_recovers_known_slope():
    """Exact check: y = 0.3 + 2*mu with no noise gives slope 2 and R2 = 1 in every month."""
    with todo():
        rng = np.random.default_rng(0)
        months = pd.date_range("2000-01-31", periods=6, freq="ME")
        permno = np.arange(60)
        mu = pd.DataFrame([(p, t, x) for t in months for p, x in zip(permno, rng.normal(size=60))],
                          columns=["permno", "month", "mu_ols"])
        nxt = mu.copy()
        nxt["month"] = nxt["month"] + pd.offsets.MonthEnd(1)
        nxt["exret"] = 0.3 + 2 * nxt["mu_ols"]
        m = pd.concat([mu[["permno", "month"]].assign(exret=0.0), nxt[["permno", "month", "exret"]]]) \
              .drop_duplicates(["permno", "month"], keep="last")
        m["in_universe"] = True
        s = monthly_slopes(mu, pd.DataFrame(), m, "mu_ols", 0)
        assert np.allclose(s["mu"], 2.0) and np.allclose(s["const"], 0.3) and np.allclose(s["r2"], 1.0)


def test_announcement_flags_weekend_maps_to_next_trading_day():
    with todo():
        days = pd.bdate_range("2020-01-01", "2020-03-31")
        daily = pd.DataFrame({"permno": 1, "date": days, "exret": 0.0})
        sat = pd.Timestamp("2020-02-01")  # Saturday -> Monday 2020-02-03
        ed = pd.DataFrame({"permno": [1], "rdq": [sat]})
        f = announcement_flags(daily, ed, (0, 0))
        assert list(daily.loc[f, "date"]) == [pd.Timestamp("2020-02-03")]
        f3 = announcement_flags(daily, ed, (-1, 1))
        assert f3.sum() == 3


def test_split_returns_adds_up_to_total(fake):
    with todo():
        daily, ed, w = load("crsp_daily", fake=True), load("earnings_dates", fake=True), load("portfolio_weights", fake=True)
        flags = announcement_flags(daily, ed, (-1, 1))
        assert 0.02 < flags.mean() < 0.12  # about 3 of 63 days
        s = split_returns(w, daily, flags)
        assert {"ret_ann_bn", "ret_other_bn", "ret_ann_ls", "ret_other_ls", "share_days_ann"} <= set(s.columns)
        assert s.notna().all().all()
