"""Zero-cost factor-exposure portfolios: is exposure to the latent factors priced? (paper Section 2.3)

Owner: Member 4. Reads: betas_svd, crsp_monthly. Writes: factor_portfolios.
Outputs: Table 2 (mean, std. dev, Sharpe of each portfolio; paper: Sharpe ratios near 0),
Figure 4 (cumulative returns), table2_events (Table 2 before/after each event).
Spec: docs/members/member-4.md

For each formation month t and each k = 1..K (K = CFG['hedge']['k_main']):
  stocks = in_universe at t with betas at t and exret at t+1
  w_k = factor_exposure_portfolio(B_t[:, :K], k-1)   # beta 1 on k, 0 on others, zero cost
  fexp_k realized in month t+1 = w_k' exret_{t+1}
Use lrrep.portfolios.solver (do not re-implement it). Equal weighting (omega = identity).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from lrrep.io import figure_path, load, save, save_table
from lrrep.portfolios.solver import factor_exposure_portfolio
from lrrep.stats import stack_panels, summarize, summarize_events


def _next_month_panel(crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """One row per (permno, formation month t): in_universe at t and exret realized at t+1."""
    cur = crsp_monthly[["permno", "month", "in_universe"]]
    nxt = crsp_monthly[["permno", "month", "exret"]].copy()
    nxt["month"] = nxt["month"] - pd.offsets.MonthEnd(1)  # re-index the t+1 return to formation month t
    nxt = nxt.rename(columns={"exret": "exret_next"})
    return cur.merge(nxt, on=["permno", "month"], how="inner")


def build_factor_portfolios(betas_svd: pd.DataFrame, crsp_monthly: pd.DataFrame, k: int) -> pd.DataFrame:
    """Return the factor_portfolios contract frame: month (realization month), fexp_1..fexp_k."""
    bcols = [f"beta_{j}" for j in range(1, k + 1)]
    missing = [c for c in bcols if c not in betas_svd.columns]
    if missing:
        raise ValueError(f"betas_svd has no {missing[0]}: need at least K={k} betas")
    d = betas_svd[["permno", "month", *bcols]].merge(_next_month_panel(crsp_monthly), on=["permno", "month"])
    d = d[d["in_universe"].astype(bool)].dropna(subset=[*bcols, "exret_next"])

    rows = []
    for t, g in d.groupby("month", sort=True):
        if len(g) < k + 2:  # need more stocks than constraints (constant + K betas)
            continue
        B = g[bcols].to_numpy(float)
        r = g["exret_next"].to_numpy(float)
        row = {"month": t + pd.offsets.MonthEnd(1)}  # realized in t+1
        for j in range(k):
            row[f"fexp_{j + 1}"] = float(factor_exposure_portfolio(B, j) @ r)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("month").reset_index(drop=True)


def _fexp_cols(fp: pd.DataFrame, n: int = 10) -> list[str]:
    return [f"fexp_{j}" for j in range(1, n + 1) if f"fexp_{j}" in fp.columns]


def table2(fp: pd.DataFrame) -> pd.DataFrame:
    """Mean (% per month), Std. dev, annualized Sharpe for fexp_1..fexp_10 (use lrrep.stats.summarize).
    Save with lrrep.io.save_table(df, 'table2')."""
    out = summarize(fp, _fexp_cols(fp, 10))
    save_table(out, "table2")
    return out


def table2_events(fp: pd.DataFrame) -> pd.DataFrame:
    """Table 2 before / after each event in config.yaml tests.events (robustness c; extension)."""
    out = stack_panels(summarize_events(fp, _fexp_cols(fp, 10)))
    save_table(out, "table2_events")
    return out


def figure4(fp: pd.DataFrame, fake: bool = False) -> None:
    """Cumulative returns of fexp_1..fexp_5 vs the market. Save to figure_path('figure4')."""
    d = fp.sort_values("month").set_index("month")
    mkt = load("market", fake).set_index("month")["mkt_exret"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for c in _fexp_cols(fp, 5):
        r = d[c].dropna()
        ax.plot(r.index, (1 + r).cumprod(), lw=1.2, label=f"Factor {c.split('_')[1]} exposure")
    m = mkt.reindex(d.index).dropna()
    ax.plot(m.index, (1 + m).cumprod(), color="black", lw=1.6, ls="--", label="Market")
    ax.set_yscale("log")
    ax.set_ylabel("Cumulative return of $1 (log scale)")
    ax.set_title("Factor-exposure portfolios vs the market")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    p = figure_path("figure4")
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=200)
    plt.close(fig)


def run(fake: bool = False) -> None:
    from lrrep.config import CFG

    fp = build_factor_portfolios(load("betas_svd", fake), load("crsp_monthly", fake), CFG["hedge"]["k_main"])
    save(fp, "factor_portfolios", fake)
    table2(fp)
    table2_events(fp)
    figure4(fp, fake)
