"""EXTENSION: is the beta-neutral portfolio tradeable after costs?

Owner: Member 6. Reads: portfolio_weights, portfolios, crsp_monthly.
Writes: results/tables/costs.csv (and an optional figure). Spec: docs/members/member-6.md

 - Turnover in month t+1 = 1/2 * sum_i |w_{i,t} - w_{i,t-1} * (1 + r_{i,t}) / (1 + r_p,t)|  (drifted
   weights; a simpler version without drift is fine, say which). Stocks entering/leaving count fully.
 - Return after costs = gross return - 2 * turnover * c, for one-way cost c in CFG['extension']['cost_bps']
   (2x because each $ of turnover is a sell and a buy). Report mean, Sharpe after costs for each c,
   and the break-even c at which the mean return after costs is zero.
 - Do it for ls_main and bn_main. The hedged portfolio may trade a lot (betas change every month):
   that is the interesting finding either way.
 - With CFG['extension']['quarterly_rebalance'], also report the quarterly-rebalanced version
   (lower turnover; frequency robustness).

Implementation: drifted weights (the formula above, r = CRSP ret incl. delisting, r_p = sum_i w_{i,t-1} r_{i,t}).
Turnover is indexed by the REALIZATION month t+1, so it lines up with `portfolios` and the cost is
charged to the return it pays for. The first formation month (building the book from cash) is
excluded. Quarterly books: trades only at quarter-end formation months (buy-and-hold in between,
as in main_portfolios.hold_returns); turnover is 0 in the other months.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import load, save_table
from lrrep.portfolios.main_portfolios import is_quarter_end
from lrrep.stats import sharpe_annual


def _drift(prev: pd.Series, ret: pd.Series) -> pd.Series:
    """Drift a weight vector (index permno) through one month of returns (index permno)."""
    r = ret.reindex(prev.index)
    gone = r.isna()
    r = r.fillna(0.0)
    rp = float((prev * r).sum())
    x = prev * (1.0 + r) / (1.0 + rp)
    x[gone] = 0.0
    return x


def turnover(weights: pd.DataFrame, col: str, crsp_monthly: pd.DataFrame | None = None,
             hold: int = 1) -> pd.Series:
    """Monthly one-way turnover of the portfolio in column `col` ('w_ls' or 'w_bn'), indexed by the
    realization month t+1 of the book formed at t. crsp_monthly=None: no drift (simpler version).
    hold=3: rebalance only at quarter-end formation months; positions drift in between."""
    rets = None if crsp_monthly is None else crsp_monthly.set_index("month")[["permno", "ret"]]
    w_by_t = {t: g.set_index("permno")[col].astype(float) for t, g in weights.groupby("month")}
    months = sorted(w_by_t)
    if hold > 1:
        months = [t for t in months if is_quarter_end([t])[0]]
    out: dict[pd.Timestamp, float] = {}
    prev: pd.Series | None = None
    prev_t = None
    for t in months:
        new = w_by_t[t]
        if prev is not None:
            held = prev
            if rets is not None:   # drift the old book month by month from prev_t+1 to t
                m = prev_t + pd.offsets.MonthEnd(1)
                while m <= t:
                    r = rets.loc[[m]].set_index("permno")["ret"] if m in rets.index else pd.Series(dtype=float)
                    held = _drift(held, r)
                    m = m + pd.offsets.MonthEnd(1)
            idx = new.index.union(held.index)
            out[t + pd.offsets.MonthEnd(1)] = 0.5 * float(
                (new.reindex(idx, fill_value=0.0) - held.reindex(idx, fill_value=0.0)).abs().sum())
        prev, prev_t = new, t
    s = pd.Series(out, name=col).sort_index()
    s.index.name = "month"
    if hold > 1 and len(s):   # months between rebalances trade nothing
        full = pd.date_range(s.index.min(), s.index.max() + pd.offsets.MonthEnd(hold - 1), freq="ME")
        s = s.reindex(full, fill_value=0.0)
        s.index.name = "month"
    return s


def _rows(name: str, r: pd.Series, to: pd.Series) -> list[dict]:
    d = pd.concat([r.rename("r"), to.rename("to")], axis=1, join="inner").dropna()
    rows = []
    for c in [0, *CFG["extension"]["cost_bps"]]:
        net = d["r"] - 2.0 * d["to"] * c / 1e4
        rows.append({"portfolio": name, "cost_bps": c, "mean_turnover": d["to"].mean(),
                     "mean_pct": 100 * net.mean(), "sharpe": sharpe_annual(net), "n_months": len(d)})
    be = d["r"].mean() / (2.0 * d["to"].mean()) * 1e4 if d["to"].mean() > 0 else np.nan
    rows.append({"portfolio": name, "cost_bps": "break_even", "mean_turnover": d["to"].mean(),
                 "mean_pct": 0.0, "sharpe": np.nan, "n_months": len(d), "break_even_bps": be})
    return rows


def cost_table(portfolios: pd.DataFrame, weights: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Rows: portfolio x cost level; columns: mean turnover, mean return after costs, Sharpe after costs;
    plus a break-even cost row per portfolio (break_even_bps = one-way cost at which the mean is 0)."""
    pf = portfolios.set_index("month")
    books = [("ls_main", "w_ls", 1), ("bn_main", "w_bn", 1)]
    if CFG["extension"].get("quarterly_rebalance"):
        books += [(c, w, 3) for c, w in (("ls_main_q", "w_ls"), ("bn_main_q", "w_bn")) if c in pf.columns]
    rows = []
    for name, wcol, hold in books:
        rows += _rows(name, pf[name], turnover(weights, wcol, crsp_monthly, hold=hold))
    return pd.DataFrame(rows).set_index(["portfolio", "cost_bps"])


def run(fake: bool = False) -> None:
    pf, w, m = load("portfolios", fake), load("portfolio_weights", fake), load("crsp_monthly", fake)
    t = cost_table(pf, w, m)
    print(t.round(3))
    save_table(t, "costs")
