"""Member 2 (CRSP data). Runs once build_monthly is implemented."""
import numpy as np
import pandas as pd

from lrrep.contracts import validate
from lrrep.data.crsp import build_monthly
from tests.conftest import todo


def test_build_monthly_delisting_size_and_universe():
    m = pd.Timestamp("2000-01-31")
    msf = pd.DataFrame({
        "permno": [1, 2, 3, 4], "month": [m] * 4,
        "ret": [0.10, np.nan, 0.02, 0.05], "dlret": [np.nan, -0.30, -0.50, np.nan],
        "prc": [-10.0, 5.0, 20.0, 50.0], "shrout": [1000.0, 2000.0, 3000.0, 4000.0],
        "shrcd": [10, 11, 10, 10], "exchcd": [1, 1, 3, 1],
    })
    rf = pd.DataFrame({"month": [m], "rf": [0.005]})
    with todo():
        out = build_monthly(msf, rf).set_index("permno")
        validate(out.reset_index(), "crsp_monthly")
        assert np.isclose(out.loc[1, "me"], 10.0)                      # |prc| * shrout / 1000
        assert np.isclose(out.loc[2, "ret"], -0.30)                    # missing ret -> dlret
        assert np.isclose(out.loc[3, "ret"], 1.02 * 0.5 - 1)           # compounded with dlret
        assert np.isclose(out.loc[1, "exret"], 0.10 - 0.005)
