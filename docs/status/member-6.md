# Member 6 status

Update at the end of every work session (newest entry on top). Only Member 6 edits this file.

## 2026-11-24

- **Done:** On fake data: `portfolio_returns`, `main_weights`, `build_portfolios` (ls/bn per model and K, weekly-beta and
  quarterly books), `table6`, `table6_events`, `table6_weekly`, Figures 6-9; `costs.py` (drift-adjusted turnover,
  returns after 5-50 bp, break-even cost, monthly and quarterly). Tests: constraints, realization-month timing,
  look-ahead, turnover bounds. On fake data hedging cuts volatility ~60% (3.96% -> 1.57%/month) and roughly triples the Sharpe.
- **Next:** Run on the real 1990-1994 slice once crsp_monthly, betas_svd and mu_hat (OLS) are in the shared folder;
  then full sample, deliver `portfolios` and `portfolio_weights` to Members 4 and 7.
- **Blocked on:** real `crsp_monthly`/`market` (Member 2), `betas_svd` (Member 3), `mu_hat` (Member 5). Fake data meanwhile.
- **Files delivered to the shared folder:** none yet.
- **Decisions / deviations:** equal weighting (Omega = I); turnover indexed by realization month, first month excluded;
  quarterly books formed at calendar quarter-ends and held buy-and-hold 3 months. K > available betas is skipped.

## YYYY-MM-DD

- **Done:**
- **Next:**
- **Blocked on:**
- **Files delivered to the shared folder:** (name, rows, first-last month)
- **Decisions / deviations:** (also add them to docs/DEVIATIONS.md)
