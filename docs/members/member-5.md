# Member 5: characteristics and return forecasts

**Owns:** `src/lrrep/forecast/`, `tests/test_member_5.py`.
**Reads:** raw Chen-Zimmermann signals, `crsp_monthly`. **Writes:** `chars_clean`, `mu_hat`.
**Read by:** Members 4, 6, 7. The random forest is the project's slowest job: start it early.
**Paper:** Section 2.4 (p. 19), Section 3.1, Appendix (random forest).

## Start here

```bash
make fake && make test
python -m lrrep.pipeline --stage forecasts --fake
```
On fake data, `chars_clean` already exists, so build the models first; the download and cleaning
can run in parallel.

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Download the Chen-Zimmermann firm-level signals (openassetpricing.com) to the shared folder `raw/chars/`. Pick signals with good coverage from 1970 (aim for 50-100). Confirm the timing convention (see `characteristics.py` docstring) and write how you checked it in your status file.
- [ ] **Day 1** On fake data: `make_model`, `training_pairs`, `rolling_forecasts` for OLS and LASSO; both tests pass (alignment and no look-ahead).
- [ ] **Day 2** `clean` on real data; deliver `chars_clean`. Run OLS and LASSO forecasts; deliver `mu_hat` with `mu_ols`, `mu_lasso` (and `mu_rf` = NaN) so Members 4 and 6 can start.
- [ ] **Day 3** Start the random forest (yearly retraining, 500 trees, depth 5, `n_jobs=-1`). Save progress per year so a crash loses one year. Run overnight (lab machine, a cloud VM or the strongest laptop).
- [ ] **Day 4 (morning)** Deliver `mu_hat` with `mu_rf`. Forecast quality table: out-of-sample R² vs zero and the top-minus-bottom decile spread of realized returns per model → `results/tables/forecast_quality.csv`.
- [ ] **Day 5** `report/sections/05-forecasts.md`; deviation rows 1-2; 1-2 slides.

## Spec details

- Training at retrain month t0 uses pairs (chars at s, exret at s+1) for s = t0-60 .. t0-1, so the last target is exret at t0. Predict t0 .. t0+11.
- Random forest: `RandomForestRegressor(n_estimators=500, max_depth=5, n_jobs=-1, random_state=CFG['seed'])`. Consider `max_features="sqrt"` or `max_samples` if it's too slow, and record it.
- LASSO: `LassoCV` with a time-ordered split inside the training window, or a fixed alpha in `config.yaml`.
- Output keyed by formation month t; `mu_*` forecasts exret at t+1.

## Definition of done

`chars_clean` and `mu_hat` (all three models) in the shared folder; tests pass; forecast quality table; status updated.

## Pitfalls

- Look-ahead is easiest to introduce here: standardize each month using that month's cross-section only; fit only on targets ≤ t0.
- Don't shift Chen-Zimmermann dates again (they are already lagged).
- Estimated compute: about 48 yearly fits on ~150k rows x ~80 features. If one fit takes > 10 min, cut features or use `max_samples=0.5`.
