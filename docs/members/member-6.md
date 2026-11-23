# Member 6: main portfolios (headline result), post-publication test, trading costs

**Owns:** `src/lrrep/portfolios/main_portfolios.py`, `src/lrrep/portfolios/costs.py`, `tests/test_member_6.py`.
**Reads:** `mu_hat`, `betas_svd`, `betas_svd_weekly`, `crsp_monthly`, `market`.
**Writes:** `portfolios`, `portfolio_weights`; Table 6, Figures 6-9, `table6_events`, `costs`, weekly/quarterly robustness.
**Read by:** Members 4 (weights) and 7 (alphas, comparison).
**Paper:** Section 2.5.1, Section 3.4 (Table 6, Figures 6-9). **Report:** main results, robustness (a) and (d), extension results.

You own the headline result AND the two headline extension parts: does the hedged portfolio still
work after the paper became public, and after trading costs?

## Start here

```bash
python -m lrrep.fake && python -m pytest tests/test_member_6.py
python -m lrrep.pipeline --stage portfolios --fake
```
On fake data, hedging cuts volatility by more than 40% and roughly doubles the Sharpe ratio. Use
`lrrep.portfolios.solver.expected_return_portfolio` and `lrrep.stats` (`summarize_subperiods`, `summarize_events`).

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** `portfolio_returns`, `build_portfolios`, `main_weights`, `table6` on fake data; test passes.
- [ ] **Day 2** On fake data: `table6_events` (Volcker, GFC, COVID, post-publication) and `costs.py` (turnover, returns after costs, break-even). Run on the real 1990-1994 slice.
- [ ] **Day 3** Full sample with `mu_ols`: complete first Table 6; deliver `portfolios` and `portfolio_weights` so Members 4 and 7 can run on real data.
- [ ] **Day 4** Rerun with `mu_rf` as main model: final Table 6 (replication sample to 2021) and `table6_events` (full extended sample; the post-publication panel is the extension's headline). Costs table. Figures 6-9.
- [ ] **Day 5** Frequency robustness: hedged portfolio with `betas_svd_weekly` (`bn_main_weekly`) and quarterly rebalancing (`ls_main_q`, `bn_main_q`). Model robustness: Table 6 with `mu_lasso`/`mu_ols`.
- [ ] **Day 6-7** Your slides (the headline: Table 6 and Figure 7; post-publication and costs); rehearsal.

## Spec details

- Formation month t: universe stocks with `mu` and all K betas at t and `exret` at t+1; drop NaN rows first.
- `ls`: sum(w) = 0, w'mu = 1; `bn`: also w'beta_k = 0 for k = 1..50. Scale to sum|w| = 2. Returns stored at t+1.
- Table 6: rows Mean (% per month), Std. dev, Sharpe (annualized); columns Market, Long-short, Beta-neutral; panels 1974-2021, 1974-1999, 2000-2021. Paper: 0.52 / 0.84 / 2.31.
- Costs: see `costs.py` docstring (turnover, 2 x turnover x cost, break-even).

## Definition of done

`portfolios`, `portfolio_weights` delivered; `table6.csv`, `table6_events.csv`, `table6_weekly.csv`, `costs.csv`; `figure6.png`-`figure9.png`; tests pass.

## Pitfalls

- Compare to the paper's TABLE values, not the in-text numbers.
- The post-publication sample is short (~4-5 years): report it with that caveat.
- If our hedged Sharpe is lower than the paper's, see `docs/DEVIATIONS.md` (yearly forest, no characteristic betas).
