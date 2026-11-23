"""Which characteristics drive the forecasts? (optional extension: interpretation)

Owner: Member 5. Reads: chars_clean, crsp_monthly (and the fitted yearly models).
Writes: results/tables/feature_importance.csv, results/figures/feature_importance.png.
Spec: docs/members/member-5.md

 - For a few retraining years (e.g. 1985, 2000, 2015, and the last one), compute permutation
   importance (sklearn.inspection.permutation_importance) of the random forest on the NEXT 12
   months of data (out of sample), or impurity importance if time is short (say which).
 - Group characteristics by economic category (Chen-Zimmermann's documentation has a category
   column: e.g. momentum, value, profitability, investment, trading frictions) and sum importance
   per group.
 - Figure: horizontal bars of group importance; table: top 15 characteristics.
Ties to the paper: its hedged portfolio loads on momentum; does momentum dominate our forecasts too?
"""
from __future__ import annotations

import pandas as pd


def importance_by_group(models: dict, chars: pd.DataFrame, crsp_monthly: pd.DataFrame,
                        categories: dict[str, str]) -> pd.DataFrame:
    """Return a frame: characteristic, group, importance (per year and averaged)."""
    raise NotImplementedError("Member 5: feature importance")


def run(fake: bool = False) -> None:
    raise NotImplementedError("Member 5: load or refit the yearly forests, then importance_by_group")
