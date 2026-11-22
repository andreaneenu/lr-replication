# 6-Day Replication Plan: Lopez-Lira & Roussanov

## Goal

In 6 days, our 7-person group reproduces the paper's core result: a portfolio hedged against all
50 latent factors still earns a high Sharpe ratio (paper, Table 6: 2.31 hedged vs 0.84 unhedged vs
0.52 market, 1974-2021). We get there with a deliberately scoped-down replication.

For a master's project, graders mostly look for three things:

- the core result is reproduced
- the method is correct, with no look-ahead bias
- we are honest about where we differ from the paper

Everyone works at their own pace. The schedule below is a suggested pace, not a set of deadlines.

## Scope

We keep the paper's logic and cut the most expensive steps. Each cut goes in our report's
deviations section ([DEVIATIONS.md](DEVIATIONS.md)).

| Area | Paper | Our 6-day version | Why it's defensible |
| --- | --- | --- | --- |
| Return forecasts | Random forest retrained every month, 207 characteristics | Retrain once a year; keep characteristics with good coverage (about 50-100) | Same model and out-of-sample logic, roughly 12x less compute |
| Beta forecasts | Lag regressions to forecast each beta | Hedge with last month's SVD betas | Hedges the same 50-factor space, so the test still holds |
| Betas hedged | 50 SVD betas + 5 characteristic betas | 50 SVD betas only | The core APT test is about the latent factors |
| Sample | 1974-2021 | Keep it if compute fits; otherwise 1990-2021 | Stated clearly in the report |
| Outputs | Tables 1-11, Figures 1-10 | Figure 1, Table 2, Table 6, Figures 6-7, Table 8 (Fama-MacBeth), Table 10 (alphas) | Covers the whole argument |
| Robustness | Many checks | One: OLS or LASSO in place of the random forest | Shows the result doesn't depend on the model |

## Roles

Members are numbered alphabetically by first name (names in [TEAM.md](TEAM.md)). Each member owns
one stage of the pipeline, its output file and its section of the report. Full briefs: [members/](members/).

| Member | Owns | Outputs |
| --- | --- | --- |
| 1 | Lead, integration, portfolio solver, run script | Pipeline that reproduces everything in one command; report edit |
| 2 | CRSP data | Daily and monthly return files, stock universe, market return |
| 3 | SVD betas | Monthly betas, eigenvalues; Figure 1 |
| 4 | Factor-exposure portfolios, Fama-MacBeth | Table 2, Table 8 |
| 5 | Characteristics and return forecasts | Yearly random forest forecasts plus an OLS/LASSO check |
| 6 | Main portfolios | Table 6, Figures 6-9 |
| 7 | External factors, alphas, comparison, slides | Table 10, paper-vs-ours table, slide deck |

## Who waits on whom

```
Member 2 (CRSP) ──► Member 3 (betas) ──► Members 4 and 6
Member 2 (CRSP) ──► Member 5 (forecasts) ──► Members 4 and 6
Member 6 (portfolios) ──► Member 7 (alphas, comparison)
Member 7 (external factors) ──► Member 7 (alphas)
```

Nobody has to wait to start: fake versions of every file exist from day 1 (`python -m lrrep.fake`).
If your part needs someone's real file, keep building on fake data and message that member.

## Suggested schedule

Hand-off points: **Day 1** file formats agreed · **Day 2** real CRSP data in · **Day 3** betas and
first forecasts in · **Day 4** tables done · **Day 5** drafts in · **Day 6** submit.

| Member | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 Lead | Repo, setup help | Review loaders, merge PRs | Look-ahead check; run 1990-94 slice | Full real run; fix interfaces | Assemble report; methods | Edit report; submit |
| 2 CRSP | WRDS pulls; universe filter | Deliver CRSP files; sample stats | Help merge characteristics; data checks | Universe chart; data section | Data section; deviation rows | Slides; buffer |
| 3 Betas | SVD on fake data; missing-day rule | Betas on real data | Betas complete; Figure 1 | Figure 3 (optional); section | Section; slides | Buffer; rehearse |
| 4 Table 2, FM | Factor-portfolio and FM code on fake | Run on real slice | Table 2, Figure 4 | Table 8 | Section; slides | Buffer; rehearse |
| 5 Forecasts | Download characteristics; cleaning rules | Clean characteristics; OLS, LASSO forecasts | Random forest runs overnight | Deliver random forest forecasts; stats | Section; slides | Buffer; rehearse |
| 6 Portfolios | Hedged/unhedged code on fake | Test on real slice | Run with OLS forecasts | Table 6, Figures 6-9 | Results section; robustness | Slides; rehearse |
| 7 Alphas | Download FF5, momentum, q5, SY factors | Alpha code on fake | Comparison template | Table 10; paper vs ours | Slide deck; tests section | Final slides; rehearse |

## How we work together

Setup: [GETTING_STARTED.md](GETTING_STARTED.md). Branches, pull requests and reviews:
[../CONTRIBUTING.md](../CONTRIBUTING.md). Code lives in this public repo; data lives only in the
team's shared folder (CRSP is licensed and the repo is public).

## Risks and fallbacks

| Risk | Why it matters | Fallback | Owner |
| --- | --- | --- | --- |
| WRDS (CRSP) access | Everything real depends on it | Check access early; others keep building on fake data | 2 |
| Random forest compute | Forecasts feed the main portfolio results | Start yearly forecasts early and run overnight; if they won't finish, LASSO becomes the main model (say so) | 5 |
| Look-ahead bias | Results look better than they are | Look-ahead tests in the repo plus a review before the full run | 1 |
| Merge conflicts | Lost time at integration | Each member edits only their own files; shared files change only by agreed PR | 1 |
| Our numbers differ from the paper | Hard to explain | Compare to Table 6, not the in-text numbers (they disagree); explain gaps by sample and model choices | 7 |

## Deviations from the paper

Tracked in [DEVIATIONS.md](DEVIATIONS.md); it becomes a section of the report.
