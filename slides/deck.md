# Slide deck skeleton (owner: Member 7)

Target: 11 slides, 12 minutes, ~1 minute each. One style: white background, figures from
`results/figures/` (real-data runs only), at most 2 bullets per slide, paper numbers next to ours.
Each owner sends: one figure or table + 2 bullets + the one sentence they would say. Placeholders
below say what is missing (TODO) and who sends it.

---

## 1. Do common factors really explain the cross-section of stock returns?
- Replication and extension of Lopez-Lira & Roussanov (2023)
- Team (alphabetical): TODO (names from docs/TEAM.md)

Speaker: Member 7 · 0:30

---

## 2. The question
- APT: only exposure to undiversifiable common factors should earn a premium
- So a diversified portfolio hedged against *all* common factors should earn ~0. Does it?

Speaker: Member 7 · 1:00

---

## 3. Method in one picture
- Figure: `results/figures/pipeline_flow.png` (TODO Member 5)
- Data → SVD betas (K = 100) → ML return forecasts → long-short, then beta-neutral (K = 50)

Speaker: Member 5 · 1:00

---

## 4. Data and sample
- Table: `summary_stats.csv` (TODO Member 2)
- CRSP 1974–2021 (replication) and through 2024 (extension); NYSE 20th-percentile size filter

Speaker: Member 2 · 1:00

---

## 5. Factors explain the variance...
- Figure 1: cumulative variance share (TODO Member 3). Paper: 5 PCs ≈ 10%, 50 ≈ 50%

Speaker: Member 3 · 1:00

---

## 6. ...but earn almost nothing
- Table 2: factor-exposure portfolio returns (TODO Member 4)

Speaker: Member 4 · 1:00

---

## 7. Headline: hedged vs unhedged vs market
- Table 6 + Figure 7 (TODO Member 6), with the paper's numbers alongside
- Paper 1974–2021 Sharpe: market 0.52, long-short 0.84, beta-neutral 2.31

Speaker: Member 6 · 1:30

---

## 8. Alternative stories: does the alpha go away under FF3, FF5, q5, SY?
- Figure: `results/figures/table10_alphas.png` (Member 7, real run pending `portfolios`)
- Paper: alphas significant under every model; hedged ≈ 85 bp/month vs q5 and SY; momentum is
  the only standard factor with a significant loading. Ours: TODO

Speaker: Member 7 · 1:00

---

## 9. Extension 1: after publication and through COVID
- `table6_events.csv` (Member 6) + `table10_post.csv` (Member 7), from June 2020
- Caveat: ~4–5 years of data, low power; SY factors end 2016, so no SY row

Speaker: Members 6, 7 · 1:00

---

## 10. Extension 2: after trading costs; cash-flow news
- `costs.csv` (TODO Member 6), `cashflow_news.csv` (TODO Member 4)

Speaker: Members 6, 4 · 1:00

---

## 11. Conclusion
- What holds, what doesn't, why it matters (fill in after slides 7–10)

Speaker: Member 7 · 1:00
