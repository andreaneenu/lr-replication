"""Member 7 (external factors, alphas, comparison)."""
import io
import zipfile

import numpy as np
import pandas as pd
import pytest

from lrrep.contracts import validate
from lrrep.data.external_factors import build_factors, parse_french
from lrrep.io import load
from lrrep.tests_ap.alphas import MODELS, alpha_regressions, table10, table10_post_publication
from tests.conftest import todo

FF5_TXT = """This file was created using the 202609 CRSP database.

,Mkt-RF,SMB,HML,RMW,CMA,RF
202001,   -0.11,   -3.13,   -6.25,   -1.38,   -2.38,    0.13
202002,   -8.13,    1.07,   -3.80,   -1.63,   -2.52,    0.12
202003,  -13.39,   -5.15,  -13.88,   -1.48,    1.23,    0.13

 Annual Factors: January-December
,Mkt-RF,SMB,HML,RMW,CMA,RF
  2020,   23.66,   12.71,  -46.56,   -2.59,  -10.29,    0.45
"""
MOM_TXT = """Missing data are indicated by -99.99 or -999.

,Mom
202001,   -99.99
202002,   -0.61
202003,    3.22

Annual Factors:
,Mom
  2020,   10.0
"""
Q5_TXT = "year,month,R_F,R_MKT,R_ME,R_IA,R_ROE,R_EG\n2020,2,0.1,-8.0,1.5,-2.0,3.0,0.5\n2020,3,0.1,-13.0,-4.0,1.0,2.0,4.0\n"
SY_TXT = "YYYYMM,MKTRF,SMB,MGMT,PERF,RF\n202001,-0.0011,-0.03,0.0123,-0.0045,0.0013\n"


@pytest.fixture
def raw_dir(tmp_path):
    for name, txt in [("F-F_Research_Data_5_Factors_2x3_CSV.zip", FF5_TXT), ("F-F_Momentum_Factor_CSV.zip", MOM_TXT)]:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr(name.replace("_CSV.zip", ".csv"), txt)
        (tmp_path / name).write_bytes(buf.getvalue())
    (tmp_path / "q5_factors_monthly_2025.csv").write_text(Q5_TXT)
    (tmp_path / "M4.csv").write_text(SY_TXT)
    return tmp_path


def test_parse_french_skips_annual_block():
    df = parse_french(FF5_TXT)
    assert len(df) == 3 and df["Mkt-RF"].iloc[2] == -13.39


def test_build_factors_units_dates_contract(raw_dir):
    f = build_factors(raw_dir)
    validate(f, "factors_ext")
    assert list(f["month"].dt.strftime("%Y-%m-%d")) == ["2020-01-31", "2020-02-29", "2020-03-31"]
    r = f.set_index(f["month"].dt.strftime("%Y-%m"))
    assert r.loc["2020-03", "mkt_rf"] == pytest.approx(-0.1339)    # percent -> decimal
    assert r.loc["2020-03", "umd"] == pytest.approx(0.0322)
    assert np.isnan(r.loc["2020-01", "umd"])                       # -99.99 -> NaN
    assert r.loc["2020-02", "q_roe"] == pytest.approx(0.03)        # q5 percent -> decimal
    assert np.isnan(r.loc["2020-01", "q_me"])                      # outer join: q5 starts later
    assert r.loc["2020-01", "sy_mgmt"] == pytest.approx(0.0123)    # SY already decimal
    assert r[["mkt_rf", "q_me", "sy_mgmt"]].abs().max().max() < 1


def test_alpha_regression_recovers_known_alpha():
    rng = np.random.default_rng(0)
    months = pd.date_range("1980-01-31", periods=400, freq="ME")
    fx = pd.DataFrame({"month": months, "mkt_rf": rng.normal(0.005, 0.045, 400)})
    for c in ("smb", "hml", "rmw", "cma", "umd", "q_me", "q_ia", "q_roe", "q_eg", "sy_mgmt", "sy_perf"):
        fx[c] = rng.normal(0, 0.03, 400)
    pf = pd.DataFrame({"month": months,
                       "bn_main": 0.008 + 0.1 * fx["mkt_rf"] + 0.5 * fx["umd"] + rng.normal(0, 0.002, 400)})
    t = alpha_regressions(pf, fx, "1980-01", "2020-12", cols=["bn_main"])
    a = t[(t.model == "FF5+UMD") & (t.term == "alpha")].iloc[0]
    assert a.coef == pytest.approx(0.8, abs=0.05)                  # % per month
    assert a.tstat > 10 and a.n_months == 400
    assert t[(t.model == "FF5+UMD") & (t.term == "umd")].coef.iloc[0] == pytest.approx(0.5, abs=0.02)
    # shifting the factors by one month must destroy the fit: checks month alignment
    lagged = fx.assign(month=fx["month"] + pd.offsets.MonthEnd(1))
    t2 = alpha_regressions(pf, lagged, "1980-01", "2020-12", cols=["bn_main"])
    assert t2[(t2.model == "FF5+UMD") & (t2.term == "umd")].coef.abs().iloc[0] < 0.2


def test_alpha_regression_no_overlap_gives_nan():
    months = pd.date_range("2018-01-31", periods=30, freq="ME")
    rng = np.random.default_rng(1)
    fx = pd.DataFrame({"month": months, **{c: rng.normal(0, 0.03, 30) for c in sum(MODELS.values(), [])}})
    fx.loc[:, ["sy_mgmt", "sy_perf"]] = np.nan                     # SY ends before the window
    pf = pd.DataFrame({"month": months, "ls_main": np.linspace(-0.01, 0.02, 30), "bn_main": 0.01})
    t = alpha_regressions(pf, fx, "2018-01", "2020-12")
    sy = t[t.model == "SY"]
    assert (sy.n_months == 0).all() and sy.coef.isna().all()


def test_table10_runs_on_fake(fake):
    with todo():
        t = table10(load("portfolios", fake=True), load("factors_ext", fake=True))
        assert len(t) > 0
        assert set(t.model) == set(MODELS) and set(t.portfolio) == {"ls_main", "bn_main"}
        assert t[t.term == "alpha"].coef.notna().all()


def test_table10_post_runs_on_fake(fake):
    t = table10_post_publication(load("portfolios", fake=True), load("factors_ext", fake=True))
    assert set(t.model) == set(MODELS)  # fake data ends in 2009: every model has n_months = 0


def test_comparison_table_has_paper_values(fake):
    from lrrep.report.comparison import comparison_table
    c = comparison_table(fake=True)
    assert {"paper", "ours", "difference", "note"} <= set(c.columns)
    assert c["paper"].notna().all()
    bn = c[(c.section == "Table 6 1974-2021") & (c.item.str.contains("Beta-neutral")) & (c.item.str.contains("Sharpe"))]
    assert bn.paper.iloc[0] == 2.31
