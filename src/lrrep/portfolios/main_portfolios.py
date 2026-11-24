"""Unhedged and beta-neutral portfolios: the paper's main result (Sections 2.5.1 and 3.4).

Owner: Member 6. Reads: mu_hat, betas_svd, crsp_monthly, market. Writes: portfolios.
Also writes: portfolio_weights (read by Member 4's cash-flow news test).
Outputs: Table 6 (three subperiods), Figure 6 (Sharpe vs number of factors hedged),
Figures 7-9 (cumulative returns), plus robustness/extension tables:
  table6_events  (before/after Volcker, GFC, COVID, and post-publication = the EXTENSION)
  table6_weekly  (beta-neutral portfolio hedged with weekly-return betas: frequency robustness)
Trading costs live in lrrep.portfolios.costs. Spec: docs/members/member-6.md

For each formation month t:
  stocks = in_universe at t with mu_hat, betas at t and exret at t+1 (drop NaN rows)
  w_ls = expected_return_portfolio(mu)                    # unhedged long-short
  w_bn = expected_return_portfolio(mu, betas[:, :K])      # beta-neutral, K = k_main
  returns realized in t+1: w' exret_{t+1}
Main forecast column: 'mu_rf' if available, else 'mu_ols' (record which in the table note).
Paper targets (Table 6, 1974-2021): market Sharpe 0.52, long-short 0.84, beta-neutral 2.31.

Choices (see docs/DEVIATIONS.md):
 - Equal weighting in the solver (Omega = I), as in the paper's main specification.
 - Requiring exret at t+1 follows the spec; CRSP ret includes delisting returns, so a stock that
   delists in t+1 is still held and earns its delisting return.
 - Quarterly rebalancing: weights formed at calendar quarter-end months (Mar, Jun, Sep, Dec) and
   held buy-and-hold for 3 months (positions drift with ret; month P&L = sum_i x_i * exret_i).
   A stock with no return in a later holding month earns 0 from then on (delisting is in ret).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import figure_path, load, path_for, save, save_table
from lrrep.portfolios.solver import expected_return_portfolio
from lrrep.stats import sharpe_annual, stack_panels, subperiod, summarize, summarize_events, summarize_subperiods

MODELS = ("ols", "lasso", "rf")
MAIN_COLS = ["mkt", "ls_main", "bn_main"]


def _beta_cols(betas: pd.DataFrame, k: int | None) -> list[str]:
    if not k:
        return []
    avail = [f"beta_{i}" for i in range(1, k + 1) if f"beta_{i}" in betas.columns]
    if len(avail) < k:
        raise ValueError(f"asked to hedge {k} factors but betas only has {len(avail)} beta columns")
    return avail


def formation_panel(mu_hat: pd.DataFrame, betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame,
                    mu_col: str, k: int | None) -> pd.DataFrame:
    """One row per (permno, formation month t): mu, beta_1..beta_k at t and exret realized at t+1.
    Only in_universe stocks at t; rows with any NaN dropped."""
    bcols = _beta_cols(betas_svd, k)
    uni = crsp_monthly.loc[crsp_monthly["in_universe"].astype(bool), ["permno", "month"]]
    nxt = crsp_monthly[["permno", "month", "exret"]].rename(columns={"exret": "exret_next"})
    nxt["month"] = nxt["month"] - pd.offsets.MonthEnd(1)   # realized in t+1 -> keyed by t
    df = uni.merge(mu_hat[["permno", "month", mu_col]].rename(columns={mu_col: "mu"}), on=["permno", "month"])
    if bcols:
        df = df.merge(betas_svd[["permno", "month", *bcols]], on=["permno", "month"])
    df = df.merge(nxt, on=["permno", "month"])
    return df.dropna().sort_values(["month", "permno"]).reset_index(drop=True)


def panel_weights(panel: pd.DataFrame, k: int | None) -> pd.Series:
    """Solver weights for every formation month of a formation_panel (aligned to panel rows)."""
    bcols = [f"beta_{i}" for i in range(1, k + 1)] if k else []
    w = np.full(len(panel), np.nan)
    for _, idx in panel.groupby("month").indices.items():
        if len(idx) <= len(bcols) + 2:         # too few stocks to satisfy the constraints
            continue
        g = panel.iloc[idx]
        betas = g[bcols].to_numpy() if bcols else None
        w[idx] = expected_return_portfolio(g["mu"].to_numpy(), betas)
    return pd.Series(w, index=panel.index)


def _returns_from(panel: pd.DataFrame, w: pd.Series) -> pd.Series:
    r = (w * panel["exret_next"]).groupby(panel["month"]).sum(min_count=1)
    r.index = r.index + pd.offsets.MonthEnd(1)  # store at the realization month t+1
    r.index.name = "month"
    return r.dropna()


def portfolio_returns(mu_hat: pd.DataFrame, betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame,
                      mu_col: str, k: int | None) -> pd.Series:
    """Monthly returns (indexed by realization month) of the unhedged (k=None) or beta-neutral portfolio."""
    panel = formation_panel(mu_hat, betas_svd, crsp_monthly, mu_col, k)
    return _returns_from(panel, panel_weights(panel, k))


def main_weights(mu_hat: pd.DataFrame, betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame,
                 mu_col: str, k: int) -> pd.DataFrame:
    """portfolio_weights contract: permno, month (formation month t), w_ls, w_bn for the main portfolios.
    Both are solved on the same stocks (those with all k betas), so the two books are comparable."""
    panel = formation_panel(mu_hat, betas_svd, crsp_monthly, mu_col, k)
    out = panel[["permno", "month"]].copy()
    out["w_ls"] = panel_weights(panel, None).to_numpy()
    out["w_bn"] = panel_weights(panel, k).to_numpy()
    out = out.dropna().reset_index(drop=True)
    out["permno"] = out["permno"].astype("int64")
    return out


def is_quarter_end(month: pd.Series | pd.DatetimeIndex) -> np.ndarray:
    return np.asarray(pd.DatetimeIndex(month).month % 3 == 0)


def hold_returns(weights: pd.DataFrame, col: str, crsp_monthly: pd.DataFrame, horizon: int = 3) -> pd.Series:
    """Buy-and-hold returns of weights formed at each formation month in `weights` (permno, month, col),
    held for `horizon` months. Returns indexed by realization month."""
    ret = crsp_monthly.set_index(["permno", "month"])[["ret", "exret"]]
    out = {}
    for t, g in weights.groupby("month"):
        x = g.set_index("permno")[col].astype(float)
        for h in range(1, horizon + 1):
            m = t + pd.offsets.MonthEnd(h)
            try:
                rm = ret.xs(m, level="month").reindex(x.index)
            except KeyError:
                break
            out[m] = float((x * rm["exret"].fillna(0.0)).sum())
            x = x * (1.0 + rm["ret"].fillna(0.0))
            x[rm["ret"].isna()] = 0.0         # no return: position is gone (delisting already in ret)
    s = pd.Series(out, name=col).sort_index()
    s.index.name = "month"
    return s


def _quarterly(mu_hat, betas_svd, crsp_monthly, mu_col, k) -> tuple[pd.Series, pd.Series]:
    w = main_weights(mu_hat, betas_svd, crsp_monthly, mu_col, k)
    w = w[is_quarter_end(w["month"])]
    return hold_returns(w, "w_ls", crsp_monthly), hold_returns(w, "w_bn", crsp_monthly)


def available_models(mu_hat: pd.DataFrame) -> list[str]:
    return [m for m in MODELS if f"mu_{m}" in mu_hat.columns and mu_hat[f"mu_{m}"].notna().any()]


def main_model(mu_hat: pd.DataFrame) -> str:
    return "rf" if "rf" in available_models(mu_hat) else "ols"


def build_portfolios(mu_hat, betas_svd, crsp_monthly, market, betas_weekly: pd.DataFrame | None = None
                     ) -> pd.DataFrame:
    """Return the portfolios contract frame: month, mkt, ls_main, bn_main, plus
    ls_<model> and bn_<model>_k<K> for each available model and K in CFG['hedge']['k_list'],
    bn_main_weekly (hedged with betas_svd_weekly, if that file exists), and, if
    CFG['extension']['quarterly_rebalance'], ls_main_q / bn_main_q (weights formed every 3rd month and
    held 3 months: frequency robustness). Runs over the full extended sample (sample.end).
    K values larger than the number of beta columns are skipped (fake data has 50)."""
    k_main = CFG["hedge"]["k_main"]
    n_beta = sum(c.startswith("beta_") for c in betas_svd.columns)
    main = main_model(mu_hat)
    cols: dict[str, pd.Series] = {}
    for m in available_models(mu_hat):
        mu_col = f"mu_{m}"
        cols[f"ls_{m}"] = portfolio_returns(mu_hat, betas_svd, crsp_monthly, mu_col, None)
        for k in CFG["hedge"]["k_list"]:
            if k <= n_beta:
                cols[f"bn_{m}_k{k}"] = portfolio_returns(mu_hat, betas_svd, crsp_monthly, mu_col, k)
    cols["ls_main"] = cols[f"ls_{main}"]
    cols["bn_main"] = cols.get(f"bn_{main}_k{k_main}",
                               portfolio_returns(mu_hat, betas_svd, crsp_monthly, f"mu_{main}", k_main))
    if betas_weekly is not None:
        cols["bn_main_weekly"] = portfolio_returns(mu_hat, betas_weekly, crsp_monthly, f"mu_{main}", k_main)
    if CFG["extension"].get("quarterly_rebalance"):
        cols["ls_main_q"], cols["bn_main_q"] = _quarterly(mu_hat, betas_svd, crsp_monthly, f"mu_{main}", k_main)

    pf = pd.DataFrame(cols)
    pf.index.name = "month"
    pf = pf.join(market.set_index("month")["mkt_exret"].rename("mkt"), how="left").reset_index()
    pf = pf[pf["ls_main"].notna() & pf["bn_main"].notna()]
    end = pd.Timestamp(CFG["sample"]["end"]) + pd.offsets.MonthEnd(0)
    pf = pf[(pf["month"] >= pd.Timestamp(CFG["sample"]["start"])) & (pf["month"] <= end)]
    order = ["month", *MAIN_COLS] + [c for c in pf.columns if c not in ("month", *MAIN_COLS)]
    return pf[order].sort_values("month").reset_index(drop=True)


def table6(pf: pd.DataFrame) -> pd.DataFrame:
    """Replication: lrrep.stats.summarize_subperiods on [mkt, ls_main, bn_main] (paper's panels, ending
    at CFG sample.paper_end); stack_panels; save as table6."""
    t = stack_panels(summarize_subperiods(pf, MAIN_COLS))
    save_table(t, "table6")
    return t


def table6_events(pf: pd.DataFrame) -> pd.DataFrame:
    """lrrep.stats.summarize_events on [mkt, ls_main, bn_main] over the FULL extended sample
    (CFG sample.start..sample.end); stack with lrrep.stats.stack_panels; save as table6_events.
    The post_publication 'after' panel is the extension's headline out-of-sample result."""
    t = stack_panels(summarize_events(pf, MAIN_COLS))
    save_table(t, "table6_events")
    return t


def table6_weekly(pf: pd.DataFrame) -> pd.DataFrame | None:
    """Frequency robustness: Table 6 panels for bn_main vs bn_main_weekly and the quarterly books."""
    cols = [c for c in ["bn_main", "bn_main_weekly", "ls_main", "ls_main_q", "bn_main_q"] if c in pf.columns]
    if len(cols) <= 2:
        return None
    t = stack_panels(summarize_subperiods(pf, cols))
    save_table(t, "table6_weekly")
    return t


def figure6(pf: pd.DataFrame) -> None:
    """Annualized Sharpe of bn_<main model>_k<K> against K (K = 0 is the unhedged ls_<model>),
    over the replication sample, one line per available model."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rep = subperiod(pf, CFG["sample"]["start"], CFG["sample"]["paper_end"])
    fig, ax = plt.subplots(figsize=(6, 4))
    for m in MODELS:
        if f"ls_{m}" not in rep.columns:
            continue
        ks = [0] + [k for k in CFG["hedge"]["k_list"] if f"bn_{m}_k{k}" in rep.columns]
        sr = [sharpe_annual(rep[f"ls_{m}"] if k == 0 else rep[f"bn_{m}_k{k}"]) for k in ks]
        ax.plot(ks, sr, marker="o", label=m.upper())
    ax.set_xlabel("Number of factors hedged (K)")
    ax.set_ylabel("Annualized Sharpe ratio")
    ax.set_title("Figure 6: Sharpe ratio vs factors hedged")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(figure_path("figure6"), dpi=150)
    plt.close(fig)


def figures7_9(pf: pd.DataFrame) -> None:
    """Cumulative returns of mkt, ls_main, bn_main: full sample (7), 1974-1999 (8), 2000-2021 (9)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = {"mkt": "Market", "ls_main": "Long-short", "bn_main": "Beta-neutral"}
    for n, (s, e) in zip((7, 8, 9), CFG["tests"]["subperiods"], strict=True):
        d = subperiod(pf, s, e).set_index("month")[MAIN_COLS]
        fig, ax = plt.subplots(figsize=(7, 4))
        if len(d):
            for c in MAIN_COLS:
                ax.plot(d.index, (1 + d[c].fillna(0.0)).cumprod(), label=labels[c])
            ax.set_yscale("log")
            ax.legend()
        else:
            ax.text(0.5, 0.5, "no months in this period", ha="center", transform=ax.transAxes)
        ax.set_ylabel("Growth of $1 (log scale)")
        ax.set_title(f"Figure {n}: cumulative excess returns, {s} to {e}")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(figure_path(f"figure{n}"), dpi=150)
        plt.close(fig)


def run(fake: bool = False) -> None:
    mu, b, m = load("mu_hat", fake), load("betas_svd", fake), load("crsp_monthly", fake)
    bw = load("betas_svd_weekly", fake) if path_for("betas_svd_weekly", fake).exists() else None
    pf = build_portfolios(mu, b, m, load("market", fake), betas_weekly=bw)
    save(pf, "portfolios", fake)
    main = main_model(mu)
    print(f"  main forecast: mu_{main}; columns: {', '.join(pf.columns[1:])}")
    save(main_weights(mu, b, m, f"mu_{main}", CFG["hedge"]["k_main"]), "portfolio_weights", fake)
    print(summarize(subperiod(pf, CFG["sample"]["start"], CFG["sample"]["paper_end"]), MAIN_COLS).round(3))
    table6(pf)
    table6_events(pf)
    table6_weekly(pf)
    figure6(pf)
    figures7_9(pf)
