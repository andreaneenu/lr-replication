# Member 3 status

Update at the end of every work session (newest entry on top). Only Member 3 edits this file.

## 2026-11-23

- **Done:** `betas_for_month`, `compute_betas`, `figure1`, `compute_betas_weekly` implemented in
  `src/lrrep/betas/svd.py`. `python -m lrrep.pipeline --stage betas --fake` runs (~4 s) and writes
  `betas_svd`, `eigen`, `betas_svd_weekly`, Figure 1. 4 tests pass (shapes/signs, contract + no look-ahead
  for daily and weekly betas, missing-row vs NaN invariance). DEVIATIONS row 5 filled in.
- **Next:** run on the real 1990-1994 slice once `crsp_daily` / `crsp_monthly` are in the shared folder,
  check Figure 1 against the paper (~10% at k = 5, ~50% at k = 50), then the full sample.
- **Blocked on:** real `crsp_daily` and `crsp_monthly` from Member 2 (Elisabetta). Fake data meanwhile.
- **Files delivered to the shared folder:** none yet.
- **Decisions / deviations:** missing days -> 0 after demeaning (row 5). Weekly betas use Thu-Wed weeks,
  the last week cut at month-end t, min 99 of 104 weeks (row 5).
