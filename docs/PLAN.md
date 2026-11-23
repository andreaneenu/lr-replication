# 7-Day Plan: Lopez-Lira & Roussanov, replicated and extended

## Goal

In about 7 days, our 7-person group (1) reproduces the paper's core result and (2) extends it, with
results ready for the 12-minute presentation (12/1 or 12/3). The report (due 12/15) is then polished
from the same results. Course requirements and where each is covered: [REQUIREMENTS.md](REQUIREMENTS.md).

**Core result to reproduce:** stock characteristics predict returns, but not because of factor risk.
Exposure to the ~50 latent factors earns almost nothing (Table 2), while a forecast-based long-short
portfolio hedged against all of them earns a high Sharpe ratio (Table 6: 2.31 hedged vs 0.84
unhedged vs 0.52 market, 1974-2021). Under the Arbitrage Pricing Theory it should earn zero.

## Our extension

**"Does the factor-neutral anomaly survive publication and trading costs, and is it cash-flow news?"**

| Part | Question | How | Owner | Effort |
| --- | --- | --- | --- | --- |
| 1. Post-publication test | Does the hedged portfolio still earn money after the paper became public (first posted May 2020), including the COVID period? | Extend the sample from 2021 to the latest month with CRSP and characteristics; report June 2020 onward separately, with alphas | 2, 5 (data), 6, 7 | Low: mostly a date change |
| 2. Trading costs | Is the Sharpe ratio of ~2 achievable after costs? | Turnover, returns after costs at 5-50 bp, break-even cost | 6 | Low-medium |
| 3. Cash-flow news | Do the returns arrive when earnings news comes out (mispricing corrected) or evenly (risk)? | Share of the hedged return earned on earnings-announcement days | 4 (2 pulls dates) | Medium |
| 4. What drives it (optional) | Which kinds of characteristics drive the forecasts? | Feature importance by category | 5 | Medium |

Parts 1-2 are the headline. Part 3 is also a guideline robustness item. Part 4 is nice-to-have.
**Honest caveat:** the post-publication sample is short (about 4-5 years), so we report it as
evidence, not a definitive test.

## Scope: what we simplify versus the paper

Recorded in [DEVIATIONS.md](DEVIATIONS.md) for the report.

| Area | Paper | Ours | Why defensible |
| --- | --- | --- | --- |
| Return forecasts | Random forest retrained monthly, 207 characteristics | Retrain yearly; characteristics with good coverage (~50-100) | Same model and out-of-sample logic, ~12x less compute |
| Beta forecasts | Lag regressions to forecast betas | Hedge with last month's SVD betas | Same 50-factor space hedged |
| Betas hedged | 50 SVD + 5 characteristic betas | 50 SVD betas | Core APT test is the latent factors |
| Outputs | Tables 1-11, Figures 1-10 | Figure 1, Tables 2, 6, 8, 10, Figures 6-9, plus robustness and extension tables | Covers the argument and the guideline |

## Roles

Members are numbered alphabetically by first name (names in [TEAM.md](TEAM.md)). Briefs: [members/](members/).

| Member | Core replication | Extension and robustness | Report / presentation |
| --- | --- | --- | --- |
| 1 | Lead, integration, solver, full run | Final checks of all extension tables | Cover, intro, objectives, conclusion, code appendix, assembly |
| 2 | CRSP data through the latest year | Earnings announcement dates (Compustat) | Data section, summary statistics table |
| 3 | SVD betas, Figure 1 | Frequency robustness: weekly-return betas | Literature review, betas section |
| 4 | Table 2 (factor premia), Table 8 (Fama-MacBeth) | Cash-flow news test; Table 2 by subsample | Those results + robustness (c) |
| 5 | Characteristics, return forecasts | Characteristics end date for the extension; feature importance (optional) | Strategy section + flow chart, characteristics summary |
| 6 | Table 6, Figures 6-9 (headline) | Post-publication + event subsamples, trading costs, quarterly rebalancing | Main results, robustness (a), (d), extension results |
| 7 | External factors, Table 10, paper-vs-ours | FF3 added, post-publication alphas | Robustness (b), slide deck (lead) |

## Who waits on whom

```
Member 2 (CRSP, earnings dates) ──► Member 3 (betas) ──────► Members 4, 6
Member 2 (CRSP)                 ──► Member 5 (forecasts) ──► Members 4, 6
Member 6 (portfolios, weights)  ──► Member 4 (cash-flow news), Member 7 (alphas)
Member 7 (factors)              ──► Member 7 (alphas)
```

Nobody has to wait to start: fake versions of every file exist from day 1 (`python -m lrrep.fake`).
If you need someone's real file, keep building on fake data and message that member.

## Suggested schedule (7 days)

Hand-offs: **D2** real CRSP in · **D3** betas + first forecasts in · **D4** main tables done ·
**D5** results freeze for slides · **D6** slides drafted · **D7** rehearsal.
The day labels are a suggested pace; agents should let everyone move faster.

| Member | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 | Day 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Repo, setup help, claim paper | Review loaders, merge PRs | Look-ahead review; 1990-94 slice run | Full real run | Check extension tables; results freeze | Intro + objectives; slides with 7 | Rehearse; report assembly starts |
| 2 | WRDS: CRSP to latest year | Deliver CRSP files | Earnings dates; summary stats | Data checks; help others | Data section | Slides | Rehearse |
| 3 | SVD on fake | Betas on real | Betas done; Figure 1 | Weekly betas | Literature review | Slides | Rehearse |
| 4 | Table 2 + FM code on fake | Cash-flow code on fake | Table 2 | Table 8; Table 2 by event | Cash-flow news test | Slides | Rehearse |
| 5 | Download chars; check end date | Clean chars; OLS, LASSO forecasts | Random forest overnight | Deliver RF forecasts; quality table | Flow chart; chars summary; importance (opt.) | Slides | Rehearse |
| 6 | Portfolio code on fake | Costs + events code on fake | Table 6 with OLS | Table 6 final; events; costs | Weekly-beta and quarterly checks | Slides | Rehearse |
| 7 | Download factors | Alpha code on fake | Comparison template; slide skeleton | Table 10 (+FF3) | Post-publication alphas; comparison | Slide deck | Rehearse |

After the presentation: each member turns their results into their report section; Member 1 assembles
and edits by 12/12, leaving buffer before 12/15 noon.

## Risks and fallbacks

| Risk | Fallback | Owner |
| --- | --- | --- |
| WRDS access (CRSP, Compustat) | Check on day 1; others keep building on fake data | 2 |
| Characteristics end before CRSP's last year | The extension sample ends at the earlier of the two; say so | 5 |
| Random forest too slow | Start by day 3, run overnight, save per year; else LASSO is the main model | 5 |
| Post-publication sample too short to be significant | Report it honestly as suggestive; lean on costs and cash-flow news for the extension | 6, 7 |
| Look-ahead bias | Look-ahead tests + Member 1 review | 1 |
| Our numbers differ from the paper | Compare to Table 6 (not the in-text numbers); explain via DEVIATIONS.md | 7 |

## How we work together

Setup: [GETTING_STARTED.md](GETTING_STARTED.md). Branches, pull requests, reviews: [../CONTRIBUTING.md](../CONTRIBUTING.md).
Code lives in this public repo; data only in the team's shared folder (CRSP is licensed).
