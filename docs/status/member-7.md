# Member 7 status

Update at the end of every work session (newest entry on top). Only Member 7 edits this file.

## 2026-11-23

- **Done:**
  - `external_factors.py`: `download_raw`, `load_ff`, `load_q5`, `load_sy`, `build_factors`. Real
    `factors_ext` built locally from public downloads (checked: mkt_rf 1974–2021 mean 0.678%/mo vs paper 0.68).
  - `alphas.py`: `table10` (CAPM, FF3, FF5+UMD, q5, SY; alpha %/mo, NW t, loadings, R², adj. R²),
    `table10_post_publication`, `figure_alphas` (slide figure with the paper's alphas as markers).
  - `comparison.py`: `comparison_table` with paper Table 6, Tables 10–11 and Figure 1 values; missing
    inputs show NaN and a note naming the owner.
  - Tests (8) in `tests/test_member_7.py`; slide skeleton `slides/deck.md`; report drafts 07d and 08b;
    DEVIATIONS row 8.
- **Next:** upload raw factor files and `factors_ext.parquet` to the shared folder; when Member 6 delivers
  real `portfolios`, run `--stage alphas --stage comparison` on real data and commit `table10.csv`,
  `table10_post.csv`, `comparison.csv`, `table10_alphas.png`; fill the TODOs in 07d/08b; collect slide
  content from each member; timed rehearsal.
- **Blocked on:** real `portfolios` (Member 6) for Table 10; `table6.csv` (Member 6) and `eigen` (Member 3)
  for the comparison table.
- **Files delivered to the shared folder:** `factors_ext` built locally (765 rows, 1963-01..2026-09;
  FF to 2026-09, q5 to 2025-12, SY to 2016-12), not yet uploaded.
- **Decisions / deviations:** SY model uses FF SMB (DEVIATIONS row 8). SY ends 2016-12, as in the paper.
  `table10_post` includes ls_main as well as bn_main for contrast.
