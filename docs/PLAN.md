# 6-day plan

Shared doc version (with the schedule drawing): the team's Claude doc "6-Day Replication Plan".
This file is the repo copy; if they differ, the doc wins for dates and this file wins for code details.

## Goal

Reproduce the paper's core result: the beta-neutral portfolio earns a much higher Sharpe ratio than
the unhedged one, while the latent factors themselves earn almost nothing. For a master's project,
graders look for: the core result reproduced, a correct method with no look-ahead bias, and an honest
account of where we differ from the paper.

## Scope (what we simplify)

| Area | Paper | Ours | Why defensible |
| --- | --- | --- | --- |
| Return forecasts | Random forest retrained monthly, 207 characteristics | Retrain yearly; characteristics with good coverage (about 50-100) | Same model and out-of-sample logic, ~12x less compute |
| Beta forecasts | Lag regressions to forecast betas | Hedge with last month's SVD betas | Same 50-factor space hedged |
| Betas hedged | 50 SVD + 5 characteristic betas | 50 SVD betas | Core APT test is the latent factors |
| Sample | 1974-2021 | Keep if compute fits; else 1990-2021 | State it in the report |
| Outputs | Tables 1-11, Figures 1-10 | Figure 1, Table 2, Table 6, Figures 6-7 (8-9), Table 8, Table 10 | Covers the whole argument |
| Robustness | Many | OLS or LASSO instead of the random forest | Shows the result isn't model-specific |

## Schedule

End-of-day gates: **D1** contracts set · **D2** real data in · **D3** betas and first forecasts in · **D4** tables done · **D5** drafts in · **D6** submit.

| Member | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 Lead | Repo live, everyone set up, contracts confirmed | Review loaders, merge PRs | Look-ahead review; run 1990-94 slice end to end | Full real run; fix interfaces | Assemble report; methods section | Edit report; submit |
| 2 CRSP | WRDS pulls; universe filter | Deliver crsp_* and market; sample stats | Help Member 5 merge chars; data checks | Universe chart; data section | Data section; deviation rows | Slides; buffer |
| 3 Betas | SVD on fake data; missing-day rule | Betas on real data; eigenvalues | Betas complete; Figure 1 | Figure 3 (optional); betas section | Section; slides | Buffer; rehearse |
| 4 Table 2, FM | Factor-portfolio code and FM code on fake | Run on real slice | Table 2, Figure 4 | Table 8 | Section; slides | Buffer; rehearse |
| 5 Forecasts | Download chars; cleaning rules | Clean chars; deliver mu_ols, mu_lasso | Random forest runs overnight | Deliver mu_rf; forecast stats | Section; slides | Buffer; rehearse |
| 6 Portfolios | Hedged/unhedged code on fake | Test on real slice | Run with OLS forecasts | Table 6, Figures 6-9 with mu_rf | Results section; robustness | Slides; rehearse |
| 7 Alphas | Download FF5, momentum, q5, SY factors | Alpha code on fake | Comparison template | Table 10; paper-vs-ours | Slide deck; tests section | Final slides; rehearse |

## Risks

| Risk | Fallback | Owner |
| --- | --- | --- |
| WRDS access | Ask the library on day 1; everyone builds on fake data meanwhile | 2 |
| Random forest too slow | Start by day 3, run overnight, save per year; else LASSO is the main model (say so) | 5 |
| Look-ahead bias | `lrrep.timing` tests + Member 1 review on day 3 | 1 |
| Merge conflicts | File ownership + `contract-change` PRs only | 1 |
| Numbers differ from paper | Compare to Table 6, not in-text numbers; explain gaps | 7 |
