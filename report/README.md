# Report (~15 pages, due Tuesday 12/15 at noon)

Structure follows the course guideline ([docs/REQUIREMENTS.md](../docs/REQUIREMENTS.md)). Each member
drafts their file(s) in `report/sections/` on their own branch; Member 1 assembles `report/report.md`
and edits it into one voice. Link figures as `../results/figures/<name>.png`; quote numbers only from
`results/tables/`. The code appendix is generated: `python -m lrrep.report.code_appendix`.

| File | Guideline section | Owner |
| --- | --- | --- |
| `sections/01-cover.md` | 1. Cover page: title, names in ALPHABETICAL order | 1 |
| `sections/02-introduction.md` | 2. Introductory comments, incl. a clear statement of our extension | 1 |
| `sections/03-objectives.md` | 3. Research objectives: what's new or interesting | 1 |
| `sections/04-literature.md` | 4. Short literature review | 3 |
| `sections/05-data.md` | 5. Data sources + summary statistics table | 2 (5 adds characteristics summary) |
| `sections/06-strategy.md` | 6. Empirical strategy + flow chart | 5 (3 betas, 6 portfolios paragraphs) |
| `sections/07a-results-factors.md` | 7. Results: Figure 1, Table 2, Table 8 | 3, 4 |
| `sections/07b-results-main.md` | 7. Results: Table 6, Figures 6-9, significance, surprises | 6 |
| `sections/07c-results-extension.md` | 7. Results: post-publication, trading costs (+ feature importance) | 6, 7 (5) |
| `sections/07d-comparison.md` | 7. Comparison with the paper and the literature | 7 |
| `sections/08a-robustness-subsamples.md` | 8. Subsamples: Volcker, GFC, COVID, post-publication | 6, 4 |
| `sections/08b-robustness-alternative-stories.md` | 8. Alphas vs CAPM, FF3, FF5+UMD, q5, SY | 7 |
| `sections/08c-robustness-cashflow-news.md` | 8. Discount rate vs cash-flow news | 4 |
| `sections/08d-robustness-frequency.md` | 8. Weekly-return betas, quarterly rebalancing | 3, 6 |
| `sections/09-conclusion.md` | 9. What we learned, what we'd do differently, contribution | 1 (input from all) |
| `sections/10-appendix.md` | Appendix: deviations from the paper, extra tables, code | 1 |
