# Member 7: factors, alphas ("alternative stories"), comparison, slides

**Owns:** `src/lrrep/data/external_factors.py`, `src/lrrep/tests_ap/alphas.py`, `src/lrrep/report/comparison.py`,
`tests/test_member_7.py`, `slides/`.
**Reads:** `portfolios`, all `results/tables/`. **Writes:** `factors_ext`; Table 10, `table10_post`, `comparison.csv`; the slide deck.
**Paper:** Section 3.5 (Tables 10-11), Table 6. **Report:** robustness (b), comparison with the paper. **Presentation:** you lead it.

## Start here

```bash
python -m lrrep.fake && python -m pytest tests/test_member_7.py
python -m lrrep.pipeline --stage alphas --fake
```

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Download FF5 and momentum (Ken French), q5 (global-q.org), Stambaugh-Yuan factors to the shared folder `raw/factors/`, through the latest month available; `build_factors` → `factors_ext` (decimals!).
- [ ] **Day 2** `table10` on fake `portfolios`: CAPM, FF3, FF5+UMD, q5, SY; alpha (% per month), NW t-stat, loadings, R², for `ls_main` and `bn_main`.
- [ ] **Day 3** `comparison_table` template (paper vs ours, using `PAPER_TABLE6`); slide skeleton in `slides/` (outline in `slides/README.md`).
- [ ] **Day 4** Table 10 on real `portfolios` (guideline: "does the alpha go away under FF3, FF5, q?").
- [ ] **Day 5** `table10_post_publication` (extension: alphas from June 2020 on); fill the comparison table.
- [ ] **Day 6** Full slide deck: collect 1-2 slides from each member, one style, 12 minutes. Robustness (b) report draft.
- [ ] **Day 7** Run the timed rehearsal.

## Spec details

- `lrrep.stats.time_series_regression(y, X)` (NW lags from config).
- Paper findings to check: significant alphas under every model; momentum is the only standard factor with a significant loading; hedged alpha ≈ 85 bp/month vs q5 and SY.

## Definition of done

`factors_ext` delivered; `table10.csv`, `table10_post.csv`, `comparison.csv`; slide deck rehearsed at 12 minutes; tests pass.

## Pitfalls

- Ken French and q5 files are in percent: divide by 100; dates to month-end.
- Align on the realization month (`portfolios.month` = factor `month`).
- Q5 and SY factors may end earlier than CRSP; the post-publication alphas use whatever overlaps (say so).
