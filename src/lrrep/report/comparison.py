"""Paper vs ours: one table of headline numbers with differences.

Owner: Member 7. Reads: results/tables/table6.csv (Member 6), table10.csv (Member 7),
the `eigen` file (Member 3, for Figure 1). Writes: results/tables/comparison.csv.

Use the values in Table 6 of the paper (Feb 2023 version), NOT the in-text numbers on
pp. 31-32, which disagree with the table (they come from an older draft).

A number we have not produced yet (its table is missing) shows ours = NaN and a note naming
the owner, so the template works before every stage has run.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import results_dir
from lrrep.io import load, save_table

# Paper Table 6: monthly mean (%), monthly std. dev (%), annualized Sharpe.
PAPER_TABLE6 = {
    "1974-2021": {"mkt": (0.68, 4.57, 0.52), "ls_main": (1.05, 4.33, 0.84), "bn_main": (0.93, 1.40, 2.31)},
    "1974-1999": {"mkt": (0.65, 4.64, 0.48), "ls_main": (1.12, 2.61, 1.49), "bn_main": (0.99, 1.48, 2.32)},
    "2000-2021": {"mkt": (0.61, 4.51, 0.46), "ls_main": (0.48, 5.68, 0.29), "bn_main": (0.34, 1.28, 0.91)},
}
# Figure 1 benchmarks: cumulative share of variance explained.
PAPER_FIGURE1 = {5: 0.10, 50: 0.50}
# Paper Tables 10-11: (alpha % per month, t-stat, adj. R2, N months). 1974-2021; SY 1974-2016.
PAPER_TABLE10 = {
    "CAPM": {"ls_main": (1.24, 7.25, 0.09, 576), "bn_main": (0.92, 14.09, -0.00, 576)},
    "FF5+UMD": {"ls_main": (0.57, 3.51, 0.45, 576), "bn_main": (0.82, 13.04, 0.06, 576)},
    "q5": {"ls_main": (0.38, 1.72, 0.28, 576), "bn_main": (0.72, 10.18, 0.06, 576)},
    "SY": {"ls_main": (0.33, 1.54, 0.38, 516), "bn_main": (0.84, 12.36, 0.07, 516)},
}
# Paper's UMD loading (Table 10), the one standard factor it says both portfolios load on.
PAPER_UMD = {"ls_main": (0.58, 7.12), "bn_main": (0.07, 3.53)}
NAMES = {"mkt": "Market", "ls_main": "Long-short (unhedged)", "bn_main": "Beta-neutral (hedged)"}
STATS = [("Mean", "mean %/mo"), ("Std. dev", "sd %/mo"), ("Sharpe ratio", "Sharpe (ann.)")]


def _read(name: str) -> pd.DataFrame | None:
    p = results_dir() / "tables" / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else None


def _panel_key(label: str) -> str:
    """'1974-01..2021-12' -> '1974-2021' (stack_panels label from lrrep.stats)."""
    a, b = str(label).split("..")
    return f"{a[:4]}-{b[:4]}"


def _row(section, item, paper, ours, note=""):
    diff = ours - paper if pd.notna(ours) and pd.notna(paper) else np.nan
    return {"section": section, "item": item, "paper": paper, "ours": ours, "difference": diff, "note": note}


def _table6_rows(t6: pd.DataFrame | None) -> list[dict]:
    rows = []
    ours = {}
    if t6 is not None:
        t6 = t6.rename(columns={t6.columns[0]: "panel", t6.columns[1]: "stat"})
        for _, r in t6.iterrows():
            ours[(_panel_key(r["panel"]), r["stat"])] = r
    for period, ports in PAPER_TABLE6.items():
        for p, vals in ports.items():
            for (stat, label), pv in zip(STATS, vals, strict=True):
                r = ours.get((period, stat))
                v = float(r[p]) if r is not None and p in r and pd.notna(r[p]) else np.nan
                note = "" if t6 is not None else "table6.csv not produced yet (Member 6)"
                rows.append(_row(f"Table 6 {period}", f"{NAMES[p]}: {label}", pv, v, note))
    return rows


def _table10_rows(t10: pd.DataFrame | None) -> list[dict]:
    rows = []
    for model, ports in PAPER_TABLE10.items():
        for p, (a, t, r2, n) in ports.items():
            sel = None if t10 is None else t10[(t10.model == model) & (t10.portfolio == p) & (t10.term == "alpha")]
            have = sel is not None and len(sel) == 1
            vals = sel.iloc[0] if have else {}

            def g(c, vals=vals):
                return float(vals[c]) if c in vals else np.nan
            note = "" if have else "table10.csv not produced yet (Member 7)"
            if have and model == "SY":
                note = "paper uses SY's own SMB; we use FF SMB (DEVIATIONS)"
            rows += [_row(f"Table 10-11 {model}", f"{NAMES[p]}: alpha %/mo", a, g("coef"), note),
                     _row(f"Table 10-11 {model}", f"{NAMES[p]}: alpha t-stat", t, g("tstat"),
                          "" if have else note),
                     _row(f"Table 10-11 {model}", f"{NAMES[p]}: adj. R2", r2, g("adj_r2"), ""),
                     _row(f"Table 10-11 {model}", f"{NAMES[p]}: N months", n, g("n_months"), "")]
    for p, (b, t) in PAPER_UMD.items():
        sel = None if t10 is None else t10[(t10.model == "FF5+UMD") & (t10.portfolio == p) & (t10.term == "umd")]
        have = sel is not None and len(sel) == 1
        rows += [_row("Table 10 FF5+UMD", f"{NAMES[p]}: UMD loading", b, float(sel.coef.iloc[0]) if have else np.nan),
                 _row("Table 10 FF5+UMD", f"{NAMES[p]}: UMD t-stat", t, float(sel.tstat.iloc[0]) if have else np.nan)]
    return rows


def _figure1_rows(fake: bool) -> list[dict]:
    """Average across months of the cumulative variance share of the first k factors."""
    try:
        e = load("eigen", fake)
    except FileNotFoundError:
        e = None
    rows = []
    for k, pv in PAPER_FIGURE1.items():
        v, note = np.nan, "eigen not produced yet (Member 3)"
        if e is not None:
            e = e.sort_values(["month", "k"])
            cum = e.assign(c=e.groupby("month")["share_explained"].cumsum())
            at_k = cum[cum["k"] == k]
            v, note = (float(at_k["c"].mean()), "") if len(at_k) else (np.nan, f"eigen has fewer than {k} factors")
        rows.append(_row("Figure 1", f"variance share of first {k} factors", pv, v, note))
    return rows


def comparison_table(fake: bool = False) -> pd.DataFrame:
    """Rows: each headline number. Columns: paper, ours, difference, note.
    Reads our results/tables/table6.csv etc.; save_table(..., 'comparison')."""
    rows = _table6_rows(_read("table6")) + _table10_rows(_read("table10")) + _figure1_rows(fake)
    out = pd.DataFrame(rows)
    save_table(out.set_index(["section", "item"]), "comparison")
    return out


def run(fake: bool = False) -> None:
    out = comparison_table(fake)
    filled = out["ours"].notna().sum()
    print(f"comparison: {filled}/{len(out)} numbers filled")
