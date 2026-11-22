# Member 7: external factors, alphas, comparison, slides

**Owns:** `src/lrrep/data/external_factors.py`, `src/lrrep/tests_ap/alphas.py`, `src/lrrep/report/`,
`tests/test_member_7.py`, `slides/`.
**Reads:** `portfolios`, all `results/tables/`. **Writes:** `factors_ext`; Table 10; comparison table; slide deck.
**Paper:** Section 3.5 (Tables 10-11), Table 6 (for the comparison).

## Start here

```bash
make fake && make test
python -m lrrep.pipeline --stage alphas --fake
```

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Download FF5 and momentum (Ken French), q5 (global-q.org), Stambaugh-Yuan factors to the shared folder `raw/factors/`; implement `build_factors`; deliver `factors_ext` (decimals!).
- [ ] **Day 2** `table10` on fake `portfolios`: alpha (% per month), NW t-stat, loadings, R² for CAPM, FF5+UMD, q5, SY; for `ls_main` and `bn_main`.
- [ ] **Day 3** `comparison_table` template reading our `results/tables/*` against `PAPER_TABLE6` and `PAPER_FIGURE1`. Slide deck skeleton in `slides/` (title, question, method, results, deviations, conclusion).
- [ ] **Day 4** Table 10 on real `portfolios`; fill the comparison table.
- [ ] **Day 5** Collect 1-2 slides from each member; one consistent style; `report/sections/07-tests.md`.
- [ ] **Day 6** Final slides; rehearse timing with the group.

## Spec details

- Use `lrrep.stats.time_series_regression(y, X)` (NW lags from config).
- Paper findings to check: both portfolios have significant alphas under every model; momentum is the only standard factor with a significant loading; hedged alpha ≈ 85 bp/month vs q5 and SY.
- Comparison table: paper value, our value, difference, one-line note.

## Definition of done

`factors_ext` delivered; `results/tables/table10.csv` and `comparison.csv`; slide deck in `slides/`; tests pass.

## Pitfalls

- Ken French and q5 files are in percent: divide by 100. Check dates convert to month-end.
- Align on the realization month: `portfolios.month` vs factor `month`.
