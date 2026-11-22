"""Paper vs ours: one table of headline numbers with differences.

Owner: Member 7. Reads: results/tables/*.csv. Writes: results/tables/comparison.csv.

Use the values in Table 6 of the paper (Feb 2023 version), NOT the in-text numbers on
pp. 31-32, which disagree with the table (they come from an older draft).
"""
from __future__ import annotations

import pandas as pd

# Paper Table 6: monthly mean (%), monthly std. dev (%), annualized Sharpe.
PAPER_TABLE6 = {
    "1974-2021": {"mkt": (0.68, 4.57, 0.52), "ls_main": (1.05, 4.33, 0.84), "bn_main": (0.93, 1.40, 2.31)},
    "1974-1999": {"mkt": (0.65, 4.64, 0.48), "ls_main": (1.12, 2.61, 1.49), "bn_main": (0.99, 1.48, 2.32)},
    "2000-2021": {"mkt": (0.61, 4.51, 0.46), "ls_main": (0.48, 5.68, 0.29), "bn_main": (0.34, 1.28, 0.91)},
}
# Figure 1 benchmarks: cumulative share of variance explained.
PAPER_FIGURE1 = {5: 0.10, 50: 0.50}


def comparison_table() -> pd.DataFrame:
    """Rows: each headline number. Columns: paper, ours, difference, note.
    Reads our results/tables/table6.csv etc.; save_table(..., 'comparison')."""
    raise NotImplementedError("Member 7: comparison table")


def run(fake: bool = False) -> None:
    comparison_table()
