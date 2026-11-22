# Paper notes (Lopez-Lira & Roussanov, Feb 2023 version)

A working summary for the team and its agents. Page, section and equation numbers refer to the
February 2023 SSRN version (abstract id 3628120). Read the paper section for your stage too.

## The argument in one paragraph

APT (Ross 1976) says only exposure to common, undiversifiable factors earns a premium, so a
diversified portfolio hedged against all common factors should earn zero. The authors (1) measure
every stock's exposure to all latent factors with an SVD of daily returns, (2) show those exposures
earn almost no premium, (3) forecast returns out of sample from characteristics with a random forest,
and (4) build a zero-cost portfolio on the forecasts that is hedged against all latent factors. It
earns a Sharpe ratio above 2, which rejects APT's central prediction.

## Section 2.1: SVD betas (Member 3)

- Each month t: R = T x N demeaned matrix of past ~252 daily excess returns (grand mean, winsorized 1%).
- Compact SVD R = U S V'. Covariance C = R'R/T = V (S^2/T) V'. Columns of V are the betas on the
  principal components; eigenvalues lambda_k = s_k^2/T; share explained = lambda_k / sum lambda.
- Normalization: omega_1 = 1/sum(V_1); beta_k = V_k / omega_1; each beta column's cross-sectional
  mean made positive.
- Benchmarks (Figure 1): first 5 PCs explain ~10% of variance; ~50 factors explain ~50%.

## Section 2.2: forecasting betas (dropped in our scope)

Paper forecasts each beta with a pooled regression on its 12 lags (36-month window). We hedge with
month-t SVD betas instead (same hedged space up to rotation; record in DEVIATIONS.md).

## Section 2.3: factor-exposure portfolios (Member 4)

min 1/2 w'Ωw s.t. w'ι = 0, w'β_k = 1, w'β_j = 0 for j ≠ k (eqs 15-18). Ω = I (equal weight) or
diag(1/mktcap). Table 2: zero-cost exposure portfolios have Sharpe ratios near zero
(e.g. 0.08 for the first PC, 0.14 for the fourth).

## Section 2.4: return forecasts (Member 5)

E[r_{i,t+1} | c_{i,t}] = f(c_{i,t}). Random forest, 500 trees, max depth 5, 60-month rolling training
window; LASSO and OLS as checks. Characteristics: 207 from Chen & Zimmermann (2022). Within each window,
drop features >10% missing, fill with the monthly cross-sectional median.

## Section 2.5: pure-play portfolios (Members 1, 4, 6)

min 1/2 w'Ωw s.t. A'w = a0, with A = [ι, μ, B], a0 = [0, μ0, 0]  (eqs 27-28)
w = Ω⁻¹A(A'Ω⁻¹A)⁻¹a0  (eq 30); with Ω = I: w = A(A'A)⁻¹a0 (eq 31). Scale so Σ|w_i| = 2.
Unhedged long-short: drop the β constraints (eqs 33-35). Beta-neutral: β'w = 0 for K = 50 factors
(eqs 36-39). Implemented in `src/lrrep/portfolios/solver.py`.

## Data (Section 3.1)

CRSP US common stocks (share codes 10/11) on NYSE, AMEX, NASDAQ; drop stocks below the NYSE 20th
size percentile. Sample 1926-2021, but characteristics start ~1970, so results are 1974-2021.

## Main results to match (Table 6; monthly mean and SD in %, annualized Sharpe)

| Period | Market | Long-short (unhedged) | Beta-neutral (hedged) |
| --- | --- | --- | --- |
| 1974-2021 | 0.68 / 4.57 / 0.52 | 1.05 / 4.33 / 0.84 | 0.93 / 1.40 / 2.31 |
| 1974-1999 | 0.65 / 4.64 / 0.48 | 1.12 / 2.61 / 1.49 | 0.99 / 1.48 / 2.32 |
| 2000-2021 | 0.61 / 4.51 / 0.46 | 0.48 / 5.68 / 0.29 | 0.34 / 1.28 / 0.91 |

**Warning:** the text on pp. 31-32 quotes different subperiod numbers (1.81 / 3.01; "2000-2014",
0.06 / 0.84). They come from an older draft. Use Table 6.

## Other results

- Figure 6: Sharpe ratio of the hedged portfolio rises with the number of factors hedged.
- Table 8: in Fama-MacBeth regressions, the forecast's slope is positive, below 1, and becomes MORE
  significant when betas are added as controls.
- Table 10: both portfolios have significant alphas against CAPM, FF5 + momentum, q5 and Stambaugh-Yuan;
  the only standard factor they load on significantly is momentum; hedged alpha ≈ 85 bp/month vs q5 and SY.
- Predictability weakens after 2000 (consistent with McLean and Pontiff 2016), but the hedged Sharpe
  ratio stays above the market's.
