# 8. Alphas vs CAPM, FF3, FF5+UMD, q5, SY

_Owner: Member 7. Draft by day 6; final by 12/12. Numbers marked TODO come from `results/tables/table10.csv`
once the real `portfolios` file exists; quote nothing from fake runs._

**Question.** Is the hedged portfolio's return just compensation for known risk factors or anomalies?
If it were, its alpha would shrink toward zero once those factors are controlled for.

**Method.** We regress the monthly excess returns of the long-short (unhedged) and beta-neutral (hedged)
portfolios on five factor models over 1974–2021: CAPM; Fama-French three factors (FF3, not in the paper,
added because the course guideline asks for it); Fama-French five factors plus momentum (FF5+UMD);
the q5 model of Hou, Mo, Xue and Zhang (2021); and the mispricing model of Stambaugh and Yuan (2017).
Standard errors are Newey-West with 12 lags. Factors come from Ken French's library, global-q.org and
Robert Stambaugh's website; portfolio and factor returns are aligned on the month in which they are realized.
The Stambaugh-Yuan factors end in December 2016, so that regression covers 1974–2016 (516 months, as in the paper).

**Paper's result (Tables 10–11).** Hedged alphas are 0.92 (CAPM), 0.82 (FF5+UMD), 0.72 (q5) and 0.84 (SY)
percent per month, all with t-statistics above 10. The unhedged alpha is significant against CAPM and FF5+UMD
but not against q5 or SY. Momentum is the only standard factor with a significant loading.

**Our result.** TODO: hedged alpha range across models, t-stats; does any model drive it to zero?
Unhedged: which models absorb it? UMD loading vs paper (0.58 unhedged, 0.07 hedged). See
`../results/figures/table10_alphas.png`.

**Extension: after publication (June 2020 on).** TODO from `table10_post.csv`. About four to five years of
data, so the t-statistics have little power; no SY row because the SY factors end in 2016.

**Caveats.** We use the Fama-French SMB in the SY model (the paper uses SY's own size factor). All factors are
in decimals, and the paper's SY loadings (≈0.01) suggest it mixed percent returns with decimal factors, so
our SY loadings are about 100 times larger; alphas and t-statistics are unaffected (docs/DEVIATIONS.md, row 8).
