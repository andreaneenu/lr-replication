# Member 3: SVD betas, frequency robustness, literature review

**Owns:** `src/lrrep/betas/`, `tests/test_member_3.py`.
**Reads:** `crsp_daily`, `crsp_monthly`. **Writes:** `betas_svd`, `betas_svd_weekly`, `eigen`; Figure 1 (optional Figure 3).
**Read by:** Members 4 and 6 (they hedge with your betas).
**Paper:** Section 2.1 (pp. 11-14), Figures 1 and 3. **Report:** section 4 (literature review), the betas part of section 6.

## Start here

```bash
python -m lrrep.fake && python -m pytest tests/test_member_3.py
python -m lrrep.pipeline --stage betas --fake
```
The full method is in the docstring of `src/lrrep/betas/svd.py`. The fake world has 8 true factors,
so on fake data the first 8 eigenvalues should clearly dominate.

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** `betas_for_month` and `compute_betas` on fake data; both tests pass (including look-ahead). Document the missing-day rule in `docs/DEVIATIONS.md` row 5.
- [ ] **Day 2** Run on the real 1990-1994 slice, then the full sample (through `sample.end`). ~600 SVDs of 252 x ~3,000 matrices: minutes.
- [ ] **Day 3** Deliver `betas_svd` (K = 100) and `eigen`. Figure 1: average cumulative share explained vs k. Check: ~10% at k = 5, ~50% at k = 50.
- [ ] **Day 4** Frequency robustness: `compute_betas_weekly` (weekly returns, 104 weeks) → deliver `betas_svd_weekly`; Member 6 rebuilds the hedged portfolio with it.
- [ ] **Day 5** Literature review draft (report section 4, ~1 page; starting list in `docs/REQUIREMENTS.md`). Betas section draft.
- [ ] **Day 6-7** Your 1-2 slides (Figure 1: the factors explain a lot of variance); rehearsal.

## Spec details

- Window: last `window_days` trading days ending on the last trading day of month t; stocks `in_universe` at t with ≥ `min_obs` days.
- `np.linalg.svd(R, full_matrices=False)`; betas are columns of `Vt.T`; keep the first `k_max`.
- Normalization: `omega1 = 1 / V[:, 0].sum()`; `beta = V / omega1`; flip each column so its mean is positive.
- `eigen`: `s**2 / T`; share = eigenvalue / sum.

## Definition of done

`betas_svd`, `betas_svd_weekly`, `eigen` delivered; tests pass; `results/figures/figure1.png`; literature review drafted.

## Pitfalls

- Demean by the GRAND mean, not stock by stock.
- Only days ≤ month-end t (the look-ahead test checks this).
- Factor order and signs flip month to month; fine for hedging.
