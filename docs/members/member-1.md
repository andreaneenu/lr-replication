# Member 1: lead, integration, portfolio solver

**Owns:** `src/lrrep/{config,contracts,io,fake,stats,timing,pipeline}.py`, `src/lrrep/portfolios/solver.py`,
`config.yaml`, `tests/test_shared.py`, root docs, `.github/`, `report/report.md` (final assembly).
**Reads:** everything. **Writes:** no data file of its own; the integrated real run and the report.
**Paper:** Section 2.5 (pure plays), and skim all of Sections 2-3.

The starter code for your modules is already written and tested (solver, contracts, fake data,
pipeline, stats, look-ahead helper). Your job is to keep it right, unblock everyone, and run the
real pipeline end to end.

## Start here

```bash
make setup && make fake && make test && make run-fake
```
Expect: shared tests pass, member tests skipped, `run-fake` shows `[todo]` for unbuilt stages.

## Day by day

- [ ] **Day 1** Create the private GitHub repo and push this scaffold (README "Repo setup"). Invite all 6, protect `main`, fill `docs/TEAM.md` and `.github/CODEOWNERS` handles. Create the shared data folder; share it in the chat.
- [ ] **Day 1** 30-minute kickoff: walk through `docs/CONTRACTS.md` and the timing rule; confirm every member ran `make test`. Any contract change requests: decide today.
- [ ] **Day 2** Review Member 2's loaders and the first real files (row counts, date ranges, `in_universe` share ~ top 70-80% of NYSE-size stocks). Merge PRs at the 21:00 cut.
- [ ] **Day 3** Look-ahead review: read every predictive function (betas, chars timing, forecasts) and check each has an `assert_no_lookahead` test. Run the 1990-1994 slice end to end on real data.
- [ ] **Day 4** Full real run: `python -m lrrep.pipeline --all`. Fix interface breaks; commit results tables and figures.
- [ ] **Day 5** Assemble `report/report.md` from `report/sections/`; write Introduction, Method overview, Conclusion.
- [ ] **Day 6** Edit to one voice, check every number against `results/tables/`, submit.

## Definition of done

`python -m lrrep.pipeline --all` on real data regenerates every table and figure listed in
`docs/CONTRACTS.md` → Results; `make test` green on `main`; report submitted.

## Pitfalls

- Don't let shared files drift: any change to `contracts.py` must update `docs/CONTRACTS.md` and `fake.py` in the same PR.
- The solver uses least squares on the small m x m system; if a month has fewer stocks than constraints, skip that month and log it.
- Keep `main` green: if a merge breaks `make run-fake`, revert first, debug second.
