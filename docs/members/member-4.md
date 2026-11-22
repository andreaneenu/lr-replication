# Member 4: factor-exposure portfolios and Fama-MacBeth

**Owns:** `src/lrrep/portfolios/factor_exposure.py`, `src/lrrep/tests_ap/fama_macbeth.py`, `tests/test_member_4.py`.
**Reads:** `betas_svd`, `crsp_monthly`, `mu_hat`. **Writes:** `factor_portfolios`; Table 2, Figure 4, Table 8.
**Paper:** Section 2.3 (pp. 17-18), Section 3.3 (Tables 2-3, Figure 4), Section 3.4 end (Table 8).

The question you answer: **is exposure to the latent factors rewarded?** The paper says almost not at
all (Sharpe ratios near zero). That is half of the paper's argument.

## Start here

```bash
make fake && make test
python -m lrrep.pipeline --stage factor_portfolios --fake
```
Use `lrrep.portfolios.solver.factor_exposure_portfolio` for weights and `lrrep.stats` for summaries
and Newey-West t-stats. Don't re-implement either.

## Day by day

- [ ] **Day 1** `build_factor_portfolios` on fake data (test passes: fake factors 2-8 have zero mean, so their portfolios earn ~0). `table2`, `figure4`.
- [ ] **Day 1** `monthly_slopes` and `table8` on fake data (cross-sectional OLS each month; average slopes; NW t-stats).
- [ ] **Day 2** Run both on the real 1990-1994 slice (with fake or slice betas if Member 3's aren't in yet).
- [ ] **Day 3** With real `betas_svd`: Table 2 (first 10 factors, K = 50 hedged in the constraints) and Figure 4. Compare to the paper (Sharpe ≈ 0.08 for factor 1, ≈ 0.14 for factor 4).
- [ ] **Day 4** Table 8 with real `mu_hat` (use `mu_rf` if delivered, else `mu_ols`; say which): specs (1) mu only, (2) mu + 5 betas, (3) mu + 50 betas.
- [ ] **Day 5** `report/sections/04-factor-premia.md` and 1-2 slides.

## Spec details

- Formation month t: stocks `in_universe` at t with all K betas and `exret` at t+1. Weights from betas at t; return = w' exret(t+1), stored at month t+1.
- Table 2 rows: Mean (% per month), Std. dev (%), annualized Sharpe; columns fexp_1..fexp_10.
- Table 8: each month regress `exret(t+1)` on a constant, `mu_hat(t)` [and betas(t)]; report time-series means of slopes with NW(12) t-stats and the average R².

## Definition of done

`factor_portfolios` in the shared folder; `results/tables/table2.csv`, `table8.csv`, `results/figures/figure4.png`; tests pass.

## Pitfalls

- A factor-exposure portfolio has beta 1 on factor k AND 0 on all others: include all K betas as constraints.
- Standardize nothing yourself before the solver: the normalization is in the betas already.
