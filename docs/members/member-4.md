# Member 4: factor premia, Fama-MacBeth, cash-flow news test

**Owns:** `src/lrrep/portfolios/factor_exposure.py`, `src/lrrep/tests_ap/fama_macbeth.py`,
`src/lrrep/tests_ap/cashflow_news.py`, `tests/test_member_4.py`.
**Reads:** `betas_svd`, `crsp_monthly`, `mu_hat`, `portfolio_weights`, `earnings_dates`, `crsp_daily`.
**Writes:** `factor_portfolios`; Table 2, Figure 4, `table2_events`, Table 8, `cashflow_news`.
**Paper:** Section 2.3, Section 3.3 (Tables 2-3, Figure 4), Table 8. **Report:** those results + robustness (c).

You answer two questions: **is exposure to the latent factors rewarded?** (the paper: almost not at all),
and **is the hedged portfolio's return cash-flow news?** (our extension, also a guideline robustness item).

## Start here

```bash
python -m lrrep.fake && python -m pytest tests/test_member_4.py
python -m lrrep.pipeline --stage factor_portfolios --fake
```
Use `lrrep.portfolios.solver.factor_exposure_portfolio` and `lrrep.stats` (summaries, Newey-West, events).

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** `build_factor_portfolios`, `table2`, `figure4`, `monthly_slopes`, `table8` on fake data; test passes.
- [ ] **Day 2** Cash-flow news code on fake data (`announcement_flags`, `split_returns` in `cashflow_news.py`); fake `earnings_dates` and `portfolio_weights` exist.
- [ ] **Day 3** With real `betas_svd`: Table 2 (factors 1-10, K = 50 constraints) and Figure 4. Compare: Sharpe ≈ 0.08 for factor 1, ≈ 0.14 for factor 4.
- [ ] **Day 4** Table 8 with real `mu_hat` (main model; say which): (1) mu only, (2) mu + 5 betas, (3) mu + 50 betas. `table2_events`: Table 2 before/after each event (`lrrep.stats.summarize_events`).
- [ ] **Day 5** Cash-flow news on real data (needs Member 6's `portfolio_weights` and Member 2's `earnings_dates`): share of the hedged return earned on announcement days vs the share of days.
- [ ] **Day 6-7** Your 1-2 slides (Table 2: factors aren't priced; cash-flow news result); rehearsal.

## Spec details

- Formation month t: universe stocks with all K betas and `exret` at t+1; return stored at t+1.
- Table 8: each month regress `exret(t+1)` on a constant, `mu_hat(t)` [and betas(t)]; time-series means of slopes with NW(12) t-stats; average R².
- Cash-flow news: method in the `cashflow_news.py` docstring. Expect ~5% of days to be announcement days; the finding is how much more than 5% of the return lands on them.

## Definition of done

`factor_portfolios` delivered; `table2.csv`, `table2_events.csv`, `table8.csv`, `cashflow_news.csv`, `figure4.png`; tests pass.

## Pitfalls

- A factor-exposure portfolio has beta 1 on factor k and 0 on all others: include all K betas as constraints.
- Announcement on a weekend or holiday → map to the next trading day.
