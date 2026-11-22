"""Member 7 (alphas, comparison)."""
from lrrep.io import load
from lrrep.tests_ap.alphas import table10
from tests.conftest import todo


def test_table10_runs_on_fake(fake):
    with todo():
        t = table10(load("portfolios", fake=True), load("factors_ext", fake=True))
        assert len(t) > 0
