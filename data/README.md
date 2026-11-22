# Data (never committed)

Real data lives in the team's shared folder, a Georgia Tech OneDrive folder shared with the team
(students get 50 GB; our files total well under 10 GB). Sync it with the OneDrive app, or use
"Add shortcut to My files" on a folder someone shared with you. Set `LRREP_DATA_DIR` to your synced copy of it.
Fake data is generated locally into `data/fake/` by `make fake`.

```
<LRREP_DATA_DIR>/
  crsp_daily.parquet      Member 2
  crsp_monthly.parquet    Member 2
  market.parquet          Member 2
  factors_ext.parquet     Member 7
  betas_svd.parquet       Member 3
  eigen.parquet           Member 3
  chars_clean.parquet     Member 5
  mu_hat.parquet          Member 5
  factor_portfolios.parquet  Member 4
  portfolios.parquet      Member 6
  raw/
    chars/                Member 5: Chen-Zimmermann downloads
    factors/              Member 7: Ken French, q5, Stambaugh-Yuan downloads
  slice_1990_1994/        Member 2: day-2 test slice (same file names)
```

CRSP data is licensed through WRDS: share it only inside the team folder, never in git or public links.
