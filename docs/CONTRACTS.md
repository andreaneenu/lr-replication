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
| `eigen` | 3 | month, k | eigenvalue, share_explained | 3 |
| `chars_clean` | 5 | permno, month | c_* (standardized characteristics, float) | 5 |
| `mu_hat` | 5 | permno, month | mu_ols, mu_lasso, mu_rf (forecast of exret in t+1; mu_rf may be NaN until ready) | 4, 6, 7 |
| `factor_portfolios` | 4 | month | fexp_1 ... fexp_K (zero-cost factor-exposure returns) | 4, 7 |
| `portfolios` | 6 | month | mkt, ls_main, bn_main, plus ls_<model>, bn_<model>_k<K> | 7 |

## Universe

A stock-month is in the universe when `crsp_monthly.in_universe` is True at formation month t:
share code 10/11, exchange code 1/2/3, and market cap at least the NYSE 20th percentile at t.
Every portfolio and regression uses only these stock-months.

## Results (not contracts, but fixed names)

`results/tables/table2.csv`, `table6.csv`, `table8.csv`, `table10.csv`, `comparison.csv`;
`results/figures/figure1.png`, `figure4.png`, `figure6.png`, `figure7.png` (`figure8.png`, `figure9.png`).
