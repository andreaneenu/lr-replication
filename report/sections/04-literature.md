# 4. Short literature review

_Owner: Member 3. Draft by day 6; final by 12/12._

Lopez-Lira and Roussanov (2023) combine three strands of the asset pricing literature: estimating
the latent factors that drive common variation in returns, predicting returns from firm
characteristics, and separating the roles of characteristics and factor exposures in expected returns.
Our extension adds a fourth: what happens to return predictability after publication, after trading
costs, and around news.

**Arbitrage pricing and latent factors.** The arbitrage pricing theory (Ross, 1976) states that if
returns follow a factor structure, only exposure to common, undiversifiable factors can earn a premium.
A well-diversified portfolio hedged against all of them should therefore earn approximately zero.
Chamberlain and Rothschild (1983) extend the argument to an "approximate" factor structure in which
idiosyncratic shocks may be weakly correlated, and show that the factors can be recovered from the
eigenvectors of the covariance matrix. Connor and Korajczyk (1986, 1988) make this practical with
asymptotic principal components for large cross-sections, and Pelger (2020) shows that high-frequency
data identify the factors more precisely. Lopez-Lira and Roussanov build on this line: the singular
value decomposition of a year of daily returns gives every stock's betas on all latent factors without
estimating the full covariance matrix. Following Lewellen and Nagel (2006), betas are re-estimated
over short windows so that they can vary over time. The key empirical point is that the cross-section
is high-dimensional: in the paper's Figure 1, about 50 factors are needed to explain half of the
variance of individual stock returns, so testing the APT requires hedging many factors, not three
or five.

**Characteristics versus covariances.** Daniel and Titman (1997) argue that characteristics, not
covariances with risk factors, explain the cross-section of average returns. Kozak, Nagel and Santosh
(2018) counter that, without near-arbitrage opportunities, a few principal components of
characteristic portfolios must explain expected returns. Kelly, Pruitt and Su (2019) and Lettau and
Pelger (2020) instead estimate factors whose loadings depend on characteristics or that are chosen to
price the cross-section as well as explain its variation. They find a trade-off between explaining the
time series and the cross-section of returns. Kim, Korajczyk and Neuhierl (2021) build arbitrage
portfolios from characteristics. Lopez-Lira and Roussanov use individual stocks, hedge exposure to
all latent factors at once, and find that the hedged portfolio keeps its average return while its
volatility roughly halves, which is evidence on the characteristics side of this debate.

**Return prediction with machine learning.** Gu, Kelly and Xiu (2020) show that flexible methods,
especially tree-based models and neural networks, predict stock returns out of sample better than
linear models, because they capture nonlinearities and interactions among predictors. Chen and
Zimmermann (2022) provide the open-source set of over 200 published characteristics that the paper
(and our replication) uses. The paper's random forest, trained on rolling windows, follows this
approach and keeps every forecast out of sample, which limits data snooping.

**Anomaly decay, news and trading costs (our extension).** McLean and Pontiff (2016) find that
anomaly returns are about 26% lower out of sample and about 58% lower after academic publication,
consistent with investors learning from published research. This motivates our test of whether the
factor-neutral portfolio still earns a premium after the paper was posted in May 2020. Engelberg,
McLean and Pontiff (2018) find that anomaly returns are concentrated on earnings announcement and
other news days. That pattern suggests mispricing that corrects when cash-flow news arrives, rather
than compensation for risk. We test whether the hedged portfolio's returns are similarly concentrated
around earnings announcements. Novy-Marx and Velikov (2016) show that trading costs eliminate the
profits of many high-turnover anomalies, so we report the hedged portfolio's returns net of costs.

## References

- Chamberlain, G., and M. Rothschild (1983). Arbitrage, factor structure, and mean-variance analysis on large asset markets. *Econometrica* 51(5), 1281-1304.
- Chen, A. Y., and T. Zimmermann (2022). Open source cross-sectional asset pricing. *Critical Finance Review* 11(2), 207-264.
- Connor, G., and R. A. Korajczyk (1986). Performance measurement with the arbitrage pricing theory: A new framework for analysis. *Journal of Financial Economics* 15(3), 373-394.
- Connor, G., and R. A. Korajczyk (1988). Risk and return in an equilibrium APT: Application of a new test methodology. *Journal of Financial Economics* 21(2), 255-289.
- Daniel, K., and S. Titman (1997). Evidence on the characteristics of cross sectional variation in stock returns. *Journal of Finance* 52(1), 1-33.
- Engelberg, J., R. D. McLean, and J. Pontiff (2018). Anomalies and news. *Journal of Finance* 73(5), 1971-2001.
- Gu, S., B. Kelly, and D. Xiu (2020). Empirical asset pricing via machine learning. *Review of Financial Studies* 33(5), 2223-2273.
- Kelly, B. T., S. Pruitt, and Y. Su (2019). Characteristics are covariances: A unified model of risk and return. *Journal of Financial Economics* 134(3), 501-524.
- Kim, S., R. A. Korajczyk, and A. Neuhierl (2021). Arbitrage portfolios. *Review of Financial Studies* 34(6), 2813-2856.
- Kozak, S., S. Nagel, and S. Santosh (2018). Interpreting factor models. *Journal of Finance* 73(3), 1183-1223.
- Lettau, M., and M. Pelger (2020). Factors that fit the time series and cross-section of stock returns. *Review of Financial Studies* 33(5), 2274-2325.
- Lewellen, J., and S. Nagel (2006). The conditional CAPM does not explain asset-pricing anomalies. *Journal of Financial Economics* 82(2), 289-314.
- Lopez-Lira, A., and N. Roussanov (2023). Do common factors really explain the cross-section of stock returns? Working paper, SSRN 3628120.
- McLean, R. D., and J. Pontiff (2016). Does academic research destroy stock return predictability? *Journal of Finance* 71(1), 5-32.
- Novy-Marx, R., and M. Velikov (2016). A taxonomy of anomalies and their trading costs. *Review of Financial Studies* 29(1), 104-153.
- Pelger, M. (2020). Understanding systematic risk: A high-frequency approach. *Journal of Finance* 75(4), 2179-2220.
- Ross, S. A. (1976). The arbitrage theory of capital asset pricing. *Journal of Economic Theory* 13(3), 341-360.
