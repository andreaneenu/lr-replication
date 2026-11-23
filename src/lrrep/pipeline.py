"""Run pipeline stages in order. Owner: Member 1.

    python -m lrrep.pipeline --list
    python -m lrrep.pipeline --stage betas --fake      # one stage on fake data
    python -m lrrep.pipeline --all --fake --keep-going # everything; skip stages not built yet
    python -m lrrep.pipeline --all                     # the final real run (Member 1, day 4)
"""
from __future__ import annotations

import argparse
import importlib
import time

# (stage, module, owner) in dependency order
STAGES: list[tuple[str, str, int]] = [
    ("crsp", "lrrep.data.crsp", 2),
    ("factors", "lrrep.data.external_factors", 7),
    ("betas", "lrrep.betas.svd", 3),
    ("chars", "lrrep.forecast.characteristics", 5),
    ("forecasts", "lrrep.forecast.models", 5),
    ("importance", "lrrep.forecast.importance", 5),
    ("factor_portfolios", "lrrep.portfolios.factor_exposure", 4),
    ("portfolios", "lrrep.portfolios.main_portfolios", 6),
    ("costs", "lrrep.portfolios.costs", 6),
    ("cashflow_news", "lrrep.tests_ap.cashflow_news", 4),
    ("fama_macbeth", "lrrep.tests_ap.fama_macbeth", 4),
    ("alphas", "lrrep.tests_ap.alphas", 7),
    ("comparison", "lrrep.report.comparison", 7),
    ("code_appendix", "lrrep.report.code_appendix", 1),
]


def run_stage(name: str, fake: bool) -> None:
    mod = dict((s, m) for s, m, _ in STAGES)[name]
    importlib.import_module(mod).run(fake=fake)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stage", action="append", help="stage name (repeatable)")
    p.add_argument("--all", action="store_true")
    p.add_argument("--fake", action="store_true", help="use data/fake instead of the real data folder")
    p.add_argument("--keep-going", action="store_true", help="skip stages that raise NotImplementedError")
    p.add_argument("--list", action="store_true")
    a = p.parse_args(argv)
    if a.list or not (a.stage or a.all):
        for s, m, o in STAGES:
            print(f"{s:18s} Member {o}  {m}")
        return 0
    names = [s for s, _, _ in STAGES] if a.all else a.stage
    failed = 0
    for s in names:
        owner = dict((x, o) for x, _, o in STAGES)[s]
        t0 = time.time()
        try:
            run_stage(s, a.fake)
            print(f"[ok]   {s} ({time.time() - t0:.1f}s)")
        except NotImplementedError as e:
            print(f"[todo] {s}: not implemented yet (Member {owner}): {e}")
            failed += 1
            if not a.keep_going:
                return 1
    return 1 if failed and not a.keep_going else 0


if __name__ == "__main__":
    raise SystemExit(main())
