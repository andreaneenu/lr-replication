"""Time-series alpha regressions (paper Tables 10-11).

Owner: Member 7. Reads: portfolios, factors_ext. Writes: results/tables/table10.csv, table10_post.csv.
Spec: docs/members/member-7.md

Guideline robustness item "Alternative stories: does the alpha go away under FF3, FF5, q?"
Regress ls_main and bn_main (monthly excess returns) on:
  CAPM: mkt_rf
  FF3: mkt_rf, smb, hml                         (not in the paper; guideline item)
  FF5 + momentum: mkt_rf, smb, hml, rmw, cma, umd
  q5: mkt_rf, q_me, q_ia, q_roe, q_eg
  Stambaugh-Yuan: mkt_rf, smb, sy_mgmt, sy_perf (smb = Fama-French SMB, see DEVIATIONS)
Report alpha (% per month), its Newey-West t-stat, factor loadings and R^2
(use lrrep.stats.time_series_regression). Paper: both portfolios have significant alphas;
the hedged portfolio's alpha is about 85 bp/month against q5 and Stambaugh-Yuan.

Output (long format, one row per portfolio x model x term):
  portfolio, model, term, coef, tstat, r2, adj_r2, n_months, first_month, last_month
term = "alpha" (coef in % per month) or a factor name (loading, unitless). Portfolio and factor
returns are both realized in `month`, so they are merged on month with no shift.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import load, save_table
from lrrep.stats import subperiod, time_series_regression

MODELS = {
    "CAPM": ["mkt_rf"],
    "FF3": ["mkt_rf", "smb", "hml"],
    "FF5+UMD": ["mkt_rf", "smb", "hml", "rmw", "cma", "umd"],
    "q5": ["mkt_rf", "q_me", "q_ia", "q_roe", "q_eg"],
    "SY": ["mkt_rf", "smb", "sy_mgmt", "sy_perf"],
}
PORTFOLIOS = ["ls_main", "bn_main"]
OUT_COLS = ["portfolio", "model", "term", "coef", "tstat", "r2", "adj_r2", "n_months", "first_month", "last_month"]


def alpha_regressions(portfolios: pd.DataFrame, factors_ext: pd.DataFrame, start: str, end: str,
                      cols: list[str] | None = None, models: dict[str, list[str]] | None = None) -> pd.DataFrame:
    """Each portfolio in `cols` on each model over [start, end], using the months where the
    portfolio and all of the model's factors are available. A model with fewer usable months
    than regressors + 2 gets one 'alpha' row with NaN and n_months = what overlapped."""
    cols = cols or PORTFOLIOS
    models = models or MODELS
    d = subperiod(portfolios[["month", *cols]].merge(factors_ext, on="month", how="inner"), start, end)
    rows = []
    for p in cols:
        for name, X in models.items():
            s = d[["month", p, *X]].dropna()
            base = {"portfolio": p, "model": name, "n_months": len(s),
                    "first_month": s["month"].min() if len(s) else pd.NaT,
                    "last_month": s["month"].max() if len(s) else pd.NaT}
            if len(s) < len(X) + 2:
                rows.append({**base, "term": "alpha", "coef": np.nan, "tstat": np.nan, "r2": np.nan, "adj_r2": np.nan})
                continue
            res = time_series_regression(s[p].reset_index(drop=True), s[X].reset_index(drop=True))
            for term in ["const", *X]:
                rows.append({**base, "term": "alpha" if term == "const" else term,
                             "coef": res.params[term] * (100.0 if term == "const" else 1.0),
                             "tstat": res.tvalues[term], "r2": res.rsquared, "adj_r2": res.rsquared_adj})
    out = pd.DataFrame(rows, columns=OUT_COLS)
    out["n_months"] = out["n_months"].astype(int)
    for c in ("first_month", "last_month"):
        out[c] = pd.to_datetime(out[c]).dt.strftime("%Y-%m")
    return out


def table10(portfolios: pd.DataFrame, factors_ext: pd.DataFrame) -> pd.DataFrame:
    """Alphas and loadings for ls_main and bn_main under each model; save_table(..., 'table10').
    Replication sample: CFG sample.start .. sample.paper_end."""
    out = alpha_regressions(portfolios, factors_ext, CFG["sample"]["start"], CFG["sample"]["paper_end"])
    save_table(out, "table10")
    return out


def table10_post_publication(portfolios: pd.DataFrame, factors_ext: pd.DataFrame) -> pd.DataFrame:
    """EXTENSION: the same alphas over CFG tests.events.post_publication .. sample.end only.
    Save as table10_post. Short sample: report it, but say the t-stats have little power.
    bn_main is the spec; ls_main is included for contrast. A model whose factors end before the
    post-publication period (SY ends 2016-12) shows n_months = 0 and NaN."""
    out = alpha_regressions(portfolios, factors_ext, CFG["tests"]["events"]["post_publication"], CFG["sample"]["end"])
    save_table(out, "table10_post")
    return out


def alpha_summary(t: pd.DataFrame) -> pd.DataFrame:
    """Wide view for slides/report: alpha (t) per model x portfolio."""
    a = t[t["term"] == "alpha"]
    return a.pivot_table(index="model", columns="portfolio", values=["coef", "tstat", "n_months"]).reindex(list(MODELS))


def figure_alphas(t: pd.DataFrame, name: str = "table10_alphas") -> None:
    """Slide figure: alpha (% per month) with 95% NW intervals per model, unhedged vs hedged,
    with the paper's Tables 10-11 alphas as hollow markers. Saved to results/figures/<name>.png."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from lrrep.io import figure_path
    from lrrep.report.comparison import PAPER_TABLE10

    a = t[t["term"] == "alpha"].set_index(["model", "portfolio"])
    models = list(MODELS)[::-1]
    series = [("ls_main", "Long-short (unhedged)", "#2a78d6"), ("bn_main", "Beta-neutral (hedged)", "#eb6834")]
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=200)
    h = 0.36
    for j, (p, label, color) in enumerate(series):
        y = np.arange(len(models)) + (0.5 - j) * h
        coef = np.array([a.coef.get((m, p), np.nan) for m in models])
        se = np.abs(coef / np.array([a.tstat.get((m, p), np.nan) for m in models]))
        ax.barh(y, coef, height=h - 0.04, color=color, label=label, zorder=2)
        ax.errorbar(coef, y, xerr=1.96 * se, fmt="none", ecolor="#52514c", elinewidth=1, capsize=2, zorder=3)
        paper = [PAPER_TABLE10.get(m, {}).get(p, (np.nan,))[0] for m in models]
        ax.scatter(paper, y, marker="D", s=28, facecolors="white", edgecolors="#1f1f1d", linewidths=1.2, zorder=4,
                   label="Paper (Tables 10-11)" if j == 0 else None)
    ax.set_yticks(np.arange(len(models)), models)
    ax.axvline(0, color="#52514c", linewidth=0.8)
    ax.set_xlabel("Alpha, % per month (bars: 95% Newey-West interval)")
    ax.grid(axis="x", color="#e4e3dd", linewidth=0.6, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(figure_path(name))
    plt.close(fig)


def run(fake: bool = False) -> None:
    pf, fx = load("portfolios", fake), load("factors_ext", fake)
    t = table10(pf, fx)
    print(alpha_summary(t).round(2).to_string())
    figure_alphas(t)
    tp = table10_post_publication(pf, fx)
    print("post-publication:", "no overlapping months" if tp["n_months"].max() == 0 else f"{tp['n_months'].max()} months")
