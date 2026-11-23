# File contracts

Every file passed between members has a fixed format. The code version is
`src/lrrep/contracts.py`; `lrrep.io.save()` refuses a file that doesn't match.
Change these only by a `contract-change` PR (see CONTRIBUTING.md).

## Conventions for every file

- Parquet, one file per name: `<LRREP_DATA_DIR>/<name>.parquet` (fake: `data/fake/<name>.parquet`).
- `month` = calendar month-END timestamp (`2001-03-31`). Build it with `ts + pd.offsets.MonthEnd(0)`.
- `date` = trading day (daily file only).
- `permno` = CRSP permanent number, int64.
- Returns are decimals (0.01 = 1%). `exret` = return minus the risk-free rate.

## Timing rule

- **Predictive files** (`betas_svd`, `chars_clean`, `mu_hat`) are indexed by **formation month t**:
  everything in the row is known at the end of t, and it is used to predict/hedge `exret` in **t+1**.
- **Return files** (`crsp_monthly`, `market`, `factors_ext`, `factor_portfolios`, `portfolios`) are
  indexed by the month in which the return is **realized**.
- So a portfolio formed at t from `mu_hat[t]` and `betas_svd[t]` earns `crsp_monthly.exret[t+1]`,
  and its return is stored in `portfolios` at month t+1.

## Files

| File | Owner | Key | Columns | Read by |
| --- | --- | --- | --- | --- |
| `crsp_daily` | 2 | permno, date | ret, rf, exret | 3 |
| `crsp_monthly` | 2 | permno, month | ret (incl. delisting), exret, me ($ millions), exchcd, shrcd, in_universe (bool) | 4, 5, 6, 7 |
| `market` | 2 | month | mkt_exret, rf | 4, 6, 7 |
| `factors_ext` | 7 | month | mkt_rf, smb, hml, rmw, cma, umd, q_me, q_ia, q_roe, q_eg, sy_mgmt, sy_perf | 4, 6, 7 |
| `betas_svd` | 3 | permno, month | beta_1 ... beta_K (K = 100 on real data), largest factor first | 4, 6 |
| `betas_svd_weekly` | 3 | permno, month | beta_1 ... beta_K from weekly returns (frequency robustness) | 6 |
| `eigen` | 3 | month, k | eigenvalue, share_explained | 3 |
| `earnings_dates` | 2 | permno, rdq | rdq = earnings announcement date (Compustat), for the cash-flow news test | 4 |
| `chars_clean` | 5 | permno, month | c_* (standardized characteristics, float) | 5 |
| `mu_hat` | 5 | permno, month | mu_ols, mu_lasso, mu_rf (forecast of exret in t+1; mu_rf may be NaN until ready) | 4, 6, 7 |
| `factor_portfolios` | 4 | month | fexp_1 ... fexp_K (zero-cost factor-exposure returns) | 4, 7 |
| `portfolio_weights` | 6 | permno, month | w_ls, w_bn: main portfolio weights formed at month t, held in t+1 | 4 |
| `portfolios` | 6 | month | mkt, ls_main, bn_main, plus ls_<model>, bn_<model>_k<K>, bn_main_weekly, ls_main_q, bn_main_q | 7 |

## Universe

A stock-month is in the universe when `crsp_monthly.in_universe` is True at formation month t:
share code 10/11, exchange code 1/2/3, and market cap at least the NYSE 20th percentile at t.
Every portfolio and regression uses only these stock-months.

## Results (not contracts, but fixed names)

Replication: `results/tables/table2.csv`, `table6.csv`, `table8.csv`, `table10.csv`, `comparison.csv`;
`results/figures/figure1.png`, `figure4.png`, `figure6.png`, `figure7.png`, `figure8.png`, `figure9.png`.
Report: `summary_stats.csv`, `summary_chars.csv`, `forecast_quality.csv`, `results/figures/pipeline_flow.png`.
Robustness and extension: `table2_events.csv`, `table6_events.csv` (incl. post-publication), `table6_weekly.csv`,
`costs.csv`, `cashflow_news.csv`, `table10_post.csv`, `feature_importance.csv` (optional).

## Sample periods

- Replication tables use 1974-01 .. `sample.paper_end` (2021-12), like the paper.
- The extension runs everything through `sample.end` (latest month with both CRSP and characteristics).
- Event splits for robustness are in `config.yaml` `tests.events`: Volcker 1979-10, GFC 2008-09,
  COVID 2020-03, post-publication 2020-06.
