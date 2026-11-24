# 7. Comparison with the paper and the literature

_Owner: Member 7. Draft by day 6; final by 12/12. Source: `results/tables/comparison.csv`
(`python -m lrrep.pipeline --stage comparison`), which lines up each headline number of the paper
with ours and their difference._

**What we compare.** Table 6 (mean, standard deviation and Sharpe ratio of the market, unhedged and
hedged portfolios in 1974–2021, 1974–1999 and 2000–2021), Tables 10–11 (alphas, t-statistics, adjusted
R², and the momentum loading), and Figure 1 (variance share of the first 5 and 50 factors). Paper values
come from the tables of the February 2023 version, not the in-text numbers on pp. 31–32, which come from an
older draft.

**Headline.** TODO: hedged Sharpe ours vs 2.31; does the ranking market < unhedged < hedged hold?

**Where we differ and why.** TODO, linking each gap to a row in docs/DEVIATIONS.md (yearly random-forest
retraining, characteristic subset, SVD betas as the hedge, no characteristic betas).

**Literature.** TODO: post-2000 decline vs McLean and Pontiff (2016); alphas vs q5 and SY vs
Hou, Xue and Zhang (2015, 2021) and Stambaugh and Yuan (2017).
