# Member 1: lead, integration, report

**Owns:** `src/lrrep/{config,contracts,io,fake,stats,timing,pipeline}.py`, `src/lrrep/portfolios/solver.py`,
`src/lrrep/report/code_appendix.py`, `config.yaml`, `tests/test_shared.py`, root docs, `.github/`, `report/report.md`.
**Reads:** everything. **Writes:** the integrated real run; report sections 1-3, 9 and the appendix.
**Paper:** Section 2.5 (pure plays); skim Sections 2-3. **Course rules:** [../REQUIREMENTS.md](../REQUIREMENTS.md).

The shared code is already written and tested (solver, contracts, fake data, pipeline, stats,
look-ahead helper, event subsamples, code appendix). Your job: keep it right, unblock people, run the
real pipeline, and make the report and presentation hang together.

## Start here

```bash
pip install -e ".[dev]" && python -m lrrep.fake && python -m pytest && python -m lrrep.pipeline --all --fake --keep-going
```

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Make sure our paper is claimed with the professor and our presentation slot is booked (12/3 if still possible). Fill `docs/TEAM.md`. Help anyone stuck on setup.
- [ ] **Day 1** When Members 2 and 5 report the last month of CRSP and of the characteristics, set `sample.end` in `config.yaml` to the earlier one (contract-change PR).
- [ ] **Day 2** Review Member 2's loaders and the first real files (row counts, date ranges, `in_universe` share). Merge approved PRs.
- [ ] **Day 3** Look-ahead review of every predictive function (betas, characteristic timing, forecasts); each needs an `assert_no_lookahead` test. Run the 1990-1994 slice end to end on real data.
- [ ] **Day 4** Full real run: `python -m lrrep.pipeline --all`. Fix interface breaks; commit result tables and figures.
- [ ] **Day 5** Results freeze for the slides: check every extension table exists and makes sense (`table6_events`, `costs`, `cashflow_news`, `table10_post`).
- [ ] **Day 6** Draft report sections 2 (introduction: must state the extension clearly) and 3 (objectives); help Member 7 with slides.
- [ ] **Day 7** Rehearsal (12 minutes, timed). Start `report/report.md` from the section files.
- [ ] **After the presentation** Conclusion, cover page (names alphabetical), code appendix (`python -m lrrep.report.code_appendix`), assemble and edit to ~15 pages by 12/12.

## Definition of done

`python -m lrrep.pipeline --all` regenerates every table and figure in `docs/CONTRACTS.md` → Results;
`main` passes tests; report submitted by 12/15 noon with the extension spelled out in the introduction.

## Pitfalls

- Any change to `contracts.py` must update `docs/CONTRACTS.md` and `fake.py` in the same PR.
- The solver uses least squares on the small m x m system; if a month has fewer stocks than constraints, skip it and log it.
- Keep `main` green: if a merge breaks the fake run, revert first, debug second.
