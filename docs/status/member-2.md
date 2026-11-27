# Member 2 status

Update at the end of every work session (newest entry on top). Only Member 2 edits this file.

## 2026-11-26

- **Done:**
  - Established WRDS access and identified CRSP CIZ (`msf_v2`, `dsf_v2`) and legacy CRSP (`msf`, `msenames`) data sources.
  - Implemented monthly and daily CRSP processing, Fama-French market and risk-free retrieval, CIZ extraction functions, and summary statistics.
  - Implemented `pull_monthly()` for legacy CRSP; live validation remains pending.
  - Constructed and validated the 1990–1994 monthly sample.
  - Generated the full 1965–2024 monthly CRSP dataset: 4,671,509 observations, including 1,349,751 eligible stock-months.
  - Generated the full 1965–2024 daily CRSP dataset: 47,897,659 observations.
  - Generated `market.parquet` containing 1,203 monthly observations (July 1926–September 2026).
  - Validated dataset schemas, monthly stock-month uniqueness, and daily excess-return calculations.
  - Generated `results/tables/summary_stats.csv` and `results/figures/universe.png`.
  - Drafted Section 5 of the report (data sources, sample construction, descriptive statistics, and limitations).
  - Added four offline CIZ tests. Latest full test run: 41 passed, 3 skipped.
  - Passed Ruff code-quality checks.
  - Separated offline validation (`check_local_data()`) from the planned extraction pipeline (`run()`).

- **Next:**
  - Complete and test the full `run()` extraction orchestration.
  - Complete remaining data-quality checks, including return-range diagnostics and daily-history gaps.
  - Finalize Section 5 and prepare the data/sample presentation slides.
  - Extend CRSP monthly and daily datasets through December 2025, using an approved CIZ classification methodology.
  - Complete the earnings-announcement dataset when historical CCM links become available.
  - Finalize documentation and submit the remaining Member 2 code through a GitHub Pull Request.

- **Blocked on:**
  - WRDS account currently disabled; administrator contacted to restore access.
  - CRSP–Compustat Merged linking tables (`ccmxpf_lnkhist`, `ccmxpf_linktable`) inaccessible under the available WRDS permissions.
  - Final 2025 investment-universe classification methodology requires coordination with Member 1.

- **Files delivered to the shared folder:**
  - `market.parquet`: 1,203 monthly observations, July 1926–September 2026.
  - `crsp_monthly.parquet`: 4,671,509 stock-month observations, January 1965–December 2024.
  - `crsp_daily.parquet`: 47,897,659 stock-day observations, January 1965–December 2024.
  - `earnings_dates.parquet`: not yet delivered (CCM access restriction).

- **Decisions / deviations:**
  - CIZ monthly total returns (`mthret`) are used without adding separate legacy delisting returns.
  - CIZ monthly market capitalization (`mthcap`) is converted into millions of dollars.
  - Historical legacy share codes 10/11 and exchange codes 1/2/3 are used through 2024.
  - NYSE 20th-percentile market capitalization is calculated separately for each month.
  - 25,746 stock-month observations without valid historical classifications are retained with temporary code `-1` and excluded from the eligible universe.
  - Of 1,349,751 eligible stock-months, 286 have missing returns; these are preserved rather than imputed.
  - The daily dataset retains available returns for securities that entered the universe at least once and excludes missing daily returns.
  - The 2025 extension requires a documented CIZ-native classification approach.
  - Large historical datasets are distributed through restricted OneDrive rather than committed to GitHub.
  - The current `run()` function remains an unimplemented orchestration entry point; `check_local_data()` provides offline validation.