## What
<!-- One or two sentences. Title format: m<N>: <what> -->

## Member and stage
Member N, stage `<stage>`.

## How I tested
- [ ] `make test` passes (my member tests run, not skipped)
- [ ] `make lint` clean
- [ ] `python -m lrrep.pipeline --stage <stage> --fake` runs
- [ ] Ran on real data (slice or full)? Rows / date range:

## Contract impact
- [ ] No shared file changed (contracts, config, io, solver, stats)
- [ ] OR this is a `contract-change` PR: affected readers tagged:

## Timing / look-ahead
- [ ] Every predictive function has an `assert_no_lookahead` test, or this PR has none

## Deviations
- [ ] None, or added to `docs/DEVIATIONS.md`

## Status file
- [ ] `docs/status/member-N.md` updated
