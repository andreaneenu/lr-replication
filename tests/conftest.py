"""Shared test setup.

* `fake` fixture: makes sure data/fake/ exists (runs the generator once if needed).
* `todo()`: wrap a call to a member's function; if it still raises NotImplementedError the
  test is SKIPPED (shown as 's'), so CI stays green until that member implements it.
  Once implemented, the test runs for real and must pass.
"""
from contextlib import contextmanager

import pytest

from lrrep.io import path_for


@pytest.fixture(scope="session")
def fake():
    if not path_for("crsp_daily", fake=True).exists():
        from lrrep.fake import main
        main()
    return True


@contextmanager
def todo():
    try:
        yield
    except NotImplementedError as e:
        pytest.skip(f"not implemented yet: {e}")
