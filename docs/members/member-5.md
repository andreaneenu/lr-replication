# Member 5: characteristics, return forecasts, strategy flow chart

**Owns:** `src/lrrep/forecast/`, `tests/test_member_5.py`.
**Reads:** raw Chen-Zimmermann signals, `crsp_monthly`. **Writes:** `chars_clean`, `mu_hat`;
`forecast_quality.csv`, `summary_chars.csv`, `results/figures/pipeline_flow.png`; optional `feature_importance.csv`.
**Read by:** Members 4, 6, 7. The random forest is the slowest job: start it early.
**Paper:** Section 2.4, Section 3.1, Appendix (random forest). **Report:** section 6 (strategy + flow chart), characteristics summary.

## Start here

```bash
python -m lrrep.fake && python -m pytest tests/test_member_5.py
python -m lrrep.pipeline --stage forecasts --fake
```
On fake data `chars_clean` already exists, so build the models first; download and cleaning can run in parallel.

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Download the Chen-Zimmermann firm-level signals (openassetpricing.com) to the shared folder `raw/chars/`. **Check the last month they cover** and tell Member 1 (it sets the extension's end date). Pick signals with good coverage from 1970 (~50-100). Confirm the timing convention (see `characteristics.py`).
- [ ] **Day 1** On fake data: `make_model`, `training_pairs`, `rolling_forecasts` for OLS and LASSO; tests pass.
- [ ] **Day 2** `clean` on real data → `chars_clean`. OLS and LASSO forecasts → `mu_hat` (`mu_rf` = NaN for now) so Members 4 and 6 can start.
- [ ] **Day 3** Random forest (yearly retraining, 500 trees, depth 5, `n_jobs=-1`), saving per year; run overnight.
- [ ] **Day 4** Deliver `mu_hat` with `mu_rf`. `forecast_quality.csv`: out-of-sample R² vs zero, top-minus-bottom decile spread, per model.
- [ ] **Day 5** Flow chart of the pipeline and the ML step (`results/figures/pipeline_flow.png`; the guideline asks for one). `characteristics_summary`. Optional: `importance.py` feature importance by category.
- [ ] **Day 6-7** Your 1-2 slides (how the forecasts work, flow chart); rehearsal.

## Spec details

- Training at retrain month t0: pairs (chars at s, exret at s+1) for s = t0-60 .. t0-1; predict t0 .. t0+11.
- Random forest: `RandomForestRegressor(n_estimators=500, max_depth=5, n_jobs=-1, random_state=CFG['seed'])`; use `max_features="sqrt"` or `max_samples` if too slow, and record it.
- Forecasts run through `sample.end` (the extension's latest month).

## Definition of done

`chars_clean` and `mu_hat` (all three models) delivered; tests pass; forecast quality table; flow chart; characteristics summary.

## Pitfalls

- Look-ahead is easiest to introduce here: standardize each month on that month only; fit only on targets ≤ t0.
- Don't shift Chen-Zimmermann dates again (they are already lagged).
- About 50 yearly fits on ~150k rows x ~80 features. If one fit takes > 10 min, cut features or use `max_samples=0.5`.
