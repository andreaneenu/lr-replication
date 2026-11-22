# Member 3: SVD betas

**Owns:** `src/lrrep/betas/`, `tests/test_member_3.py`.
**Reads:** `crsp_daily`, `crsp_monthly`. **Writes:** `betas_svd`, `eigen`; Figure 1 (optional Figure 3).
**Read by:** Members 4 and 6 (they hedge with your betas).
**Paper:** Section 2.1 (pp. 11-14), Figure 1, Figure 3.

## Start here

```bash
make fake && make test     # tests/test_member_3.py skipped until betas_for_month exists
python -m lrrep.pipeline --stage betas --fake
```
The full method is in the docstring of `src/lrrep/betas/svd.py`. The fake world has 8 true factors,
so on fake data the first 8 eigenvalues should clearly dominate.

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Implement `betas_for_month` (SVD, grand-mean demeaning, winsorizing, normalization, sign flip) and `compute_betas`; make both tests pass on fake data, including the look-ahead test.
- [ ] **Day 1** Decide and document the missing-day rule (default in `config.yaml`: ≥ 240 of 252 days, missing set to 0 after demeaning) in `docs/DEVIATIONS.md` row 5.
- [ ] **Day 2** Run on the real 1990-1994 slice, then on the full sample. Expect ~2,000-3,000 stocks per month; one SVD of a 252 x 3,000 matrix takes well under a second, so ~600 months is minutes.
- [ ] **Day 3** Deliver `betas_svd` (K = 100) and `eigen` to the shared folder. Figure 1: average cumulative share explained vs k. Check against the paper: ~10% at k = 5, ~50% at k = 50.
- [ ] **Day 4** Optional Figure 3 (share explained over time). Write `report/sections/03-betas.md`.
- [ ] **Day 5** Section final; 1-2 slides (Figure 1 + one sentence).

## Spec details

- Window: the last `window_days` trading days ending on the last trading day of month t.
- Stocks: `in_universe` at t AND at least `min_obs` non-missing days in the window.
- `np.linalg.svd(R, full_matrices=False)` → `U, s, Vt`; betas are rows of `Vt.T` (N x T), keep first `k_max` columns.
- Normalization: `omega1 = 1 / V[:, 0].sum()`; `beta = V / omega1`; flip each column's sign so its mean is positive.
- `eigen`: eigenvalue `s**2 / T`, `share_explained = eigenvalue / eigenvalue.sum()` for k = 1..k_max.

## Definition of done

`betas_svd` and `eigen` saved for every month 1973-12 .. 2021-11 (or the fallback sample), tests pass,
Figure 1 in `results/figures/figure1.png`, chat message sent.

## Pitfalls

- Demean by the GRAND mean, not stock-by-stock (paper: individual daily means are estimated poorly).
- Only use days ≤ month-end t (the look-ahead test checks this).
- Factor order and signs can flip month to month; that is fine for hedging (the hedged space is the same).
