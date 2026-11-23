# Course requirements (MGT 6078 project guideline) and where each is covered

Graded on: **technical ability, creativity, presentation, and style**.
Deadlines: **12-minute team presentation** (12/1 or 12/3; the professor wants real results) and the
**written report, due Tuesday December 15 at noon**.

## Must-haves

| Requirement | Where we cover it | Owner |
| --- | --- | --- |
| Collect and use data | CRSP, Compustat earnings dates, Chen-Zimmermann characteristics, factor libraries | 2, 5, 7 |
| The introduction clearly spells out how we EXTEND the paper | Intro states the extension (PLAN.md "Our extension") | 1 |
| Report ≈ 15 pages; extra material in the appendix | `report/` structure below | 1 assembles |
| Code printed in the appendix | `python -m lrrep.report.code_appendix` → `report/appendix_code.md` | 1 |
| 12-minute presentation with results | `slides/` (outline in slides/README.md) | 7 leads, all contribute |

## Report organization (the guideline's order) and owners

| # | Section | Content | Owner |
| --- | --- | --- | --- |
| 1 | Cover page | Title; member names in ALPHABETICAL order | 1 |
| 2 | Introductory comments | Question, APT, the paper's finding, our extension and findings | 1 |
| 3 | Research objectives: what's new or interesting | The extension: post-publication, after costs, cash-flow news | 1 |
| 4 | Short literature review | APT (Ross 1976; Chamberlain-Rothschild 1983), characteristics vs covariances (Daniel-Titman 1997), ML return prediction (Gu-Kelly-Xiu 2020), anomaly decay (McLean-Pontiff 2016), anomalies and news (Engelberg-McLean-Pontiff 2018), costs (Novy-Marx-Velikov 2016) | 3 |
| 5 | Data sources | CRSP, Compustat, Chen-Zimmermann, Ken French, q5, Stambaugh-Yuan; filters; **summary statistics table** | 2 (+5 chars summary) |
| 6 | Empirical strategy | SVD betas, ML forecasts, pure-play portfolios, tests; **flow chart** of the pipeline and the ML step | 5 (flow chart), 3, 6 |
| 7 | Results | Figure 1, Table 2, Table 6, Figures 6-9, Table 8, Table 10, comparison with the paper, **significance**, **surprises**; extension results | 3, 4, 6, 7 |
| 8 | Robustness checks | (a) subsamples: Volcker, GFC, COVID, post-publication; (b) alternative stories: CAPM, FF3, FF5+UMD, q5, SY alphas; (c) discount rate vs cash-flow news: earnings announcements; (d) frequency: weekly-return betas, quarterly rebalancing | 6, 7, 4, 3+6 |
| 9 | Concluding remarks | What we learned, what we'd do differently, contribution to asset pricing | 1 (input from all) |
| A | Appendix | Code, extra tables, deviations from the paper | 1 |

## Other rules to respect

- Each paper may be picked by only one group: make sure ours is claimed (Member 1).
- Results must come from our own data and code; fake data is never reported.
