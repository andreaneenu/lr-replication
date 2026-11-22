# Member 6: main portfolios (the headline result)

**Owns:** `src/lrrep/portfolios/main_portfolios.py`, `tests/test_member_6.py`.
**Reads:** `mu_hat`, `betas_svd`, `crsp_monthly`, `market`. **Writes:** `portfolios`; Table 6, Figures 6-9.
**Read by:** Member 7 (alphas, comparison).
**Paper:** Section 2.5.1 (pp. 22-24), Section 3.4 (Table 6, Figures 6-9).

## Start here

```bash
make fake && make test
python -m lrrep.pipeline --stage portfolios --fake
```
On fake data, hedging should cut volatility by more than 40% and roughly double the Sharpe ratio
(that is what `tests/test_member_6.py` checks). Use `lrrep.portfolios.solver.expected_return_portfolio`.

## Day by day

- [ ] **Day 1** `portfolio_returns` and `build_portfolios` on fake data; test passes. `table6` with `lrrep.stats.summarize_subperiods`.
- [ ] **Day 2** Run on the real 1990-1994 slice. Add `figure6` (Sharpe vs K for K in `config.yaml` `hedge.k_list`) and `figures7_9`.
- [ ] **Day 3** Full sample with `mu_ols` (real betas): a complete first Table 6.
- [ ] **Day 4** Rerun with `mu_rf` as the main model; final Table 6 and Figures 6-9. Robustness: same table with `mu_lasso` / `mu_ols`.
- [ ] **Day 5** `report/sections/06-results.md` (main results section); deviation rows 3-4; 1-2 slides.

## Spec details

- Formation month t: stocks `in_universe` at t with `mu` and all K betas at t and `exret` at t+1.
- `ls`: constraints sum(w) = 0, w'mu = 1; `bn`: also w'beta_k = 0, k = 1..50. Weights scaled so sum|w| = 2.
- Store returns at the realization month t+1. `mkt` = `market.mkt_exret`.
- Table 6 layout: rows Mean (% per month), Std. dev, Sharpe ratio (annualized); columns Market, Long-short, Beta-neutral; panels 1974-2021, 1974-1999, 2000-2021.
- Paper targets: Sharpe 0.52 / 0.84 / 2.31 (full sample).

## Definition of done

`portfolios` in the shared folder; `results/tables/table6.csv`; `figure6.png`, `figure7.png` (+8, 9); tests pass.

## Pitfalls

- Drop stock-months with any NaN among mu, betas, next-month return BEFORE building A, or the solver returns NaN.
- Compare our Table 6 to the paper's TABLE values, not the in-text numbers (they disagree).
- If our hedged Sharpe is lower than the paper's, the likely reasons are in `docs/DEVIATIONS.md` (yearly forest, no characteristic betas).
