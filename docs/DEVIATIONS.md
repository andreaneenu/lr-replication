# Deviations from the paper

This becomes a section of our report. Each owner fills in their row and keeps it true.
"Effect" = how the choice could change our numbers versus the paper's.

| # | Deviation | Why | Likely effect | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Random forest retrained yearly instead of monthly | Compute (one-week project) | Slightly weaker forecasts; if anything a lower hedged Sharpe | 5 | planned |
| 2 | Subset of Chen-Zimmermann characteristics (good coverage only) | Coverage and compute | Slightly weaker forecasts | 5 | planned |
| 3 | Hedge with month-t SVD betas instead of forecast betas (paper Sec. 2.2) | Time; same hedged space up to rotation | Possibly a little leftover factor exposure, higher hedged volatility | 6 | planned |
| 4 | No characteristic-based betas (paper adds 5) | Time | Paper says hedging them raises the Sharpe; ours may be lower | 6 | planned |
| 5 | Missing daily returns set to 0 after demeaning in the SVD | Paper does not say how missing days are handled | Small effect on betas of thinly traded stocks | 3 | planned |
| 6 | Sample start (fill in only if shortened from 1974) | Compute | A shorter, post-2000-heavy sample lowers the Sharpe ratio | 2 | open |
| 7 | CRSP format used (legacy vs CIZ) and any filter mapping | Data access | Should be negligible; note it | 2 | open |

Note: running the sample past 2021 is our EXTENSION, not a deviation. Replication tables stop at
`sample.paper_end` (2021-12) so they are comparable with the paper.
