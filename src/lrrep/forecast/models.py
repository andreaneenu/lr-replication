"""Out-of-sample return forecasts (paper Section 2.4).

Owner: Member 5. Reads: chars_clean, crsp_monthly. Writes: mu_hat.
Spec: docs/members/member-5.md

Training scheme (our 6-day version of the paper's monthly retraining):
 - At each retraining month t0 (every CFG['forecast']['retrain_every_months'] months), fit on
   pairs (chars at s, exret at s+1) for s in the CFG['forecast']['train_months'] months
   ENDING AT t0 - 1, so the latest target used is exret at t0. Nothing after t0 is used.
 - Use that fitted model to predict exret(t+1) from chars(t) for t = t0, ..., t0 + 11.
 - Models: OLS (fast, first), LASSO, random forest with
   CFG['forecast']['random_forest'] (500 trees, max depth 5). Seed CFG['seed'].
 - Output mu_hat: permno, month (= t, the formation month), mu_ols, mu_lasso, mu_rf.
   Ship mu_ols and mu_lasso first (day 2-3) so Member 6 can build Table 6; add mu_rf when the
   forest finishes (run it overnight; save partial progress per year so a crash loses little).

Forecast quality to report (docs/members/member-5.md): out-of-sample R^2 vs a zero forecast,
and the average spread in realized exret between the top and bottom deciles of mu.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import load, save

MODELS = ("ols", "lasso", "rf")


def make_model(name: str):
    """Return an unfitted sklearn estimator for 'ols', 'lasso' or 'rf' using CFG values."""
    raise NotImplementedError("Member 5: model factory")


def training_pairs(chars: pd.DataFrame, crsp_monthly: pd.DataFrame) -> pd.DataFrame:
    """Join chars at month t to exret at month t+1 (by permno). Column 'y' = next-month exret."""
    raise NotImplementedError("Member 5: build (X_t, y_t+1) pairs")


def rolling_forecasts(pairs: pd.DataFrame, chars: pd.DataFrame, model: str) -> pd.Series:
    """Fit every retrain_every_months on the trailing train_months window and predict forward.
    Returns a Series indexed like `chars` (permno, month) of forecasts for model `model`.
    Must never fit on targets dated after the formation month being predicted."""
    raise NotImplementedError("Member 5: rolling out-of-sample forecasts")


def run(fake: bool = False, models: tuple[str, ...] = MODELS) -> None:
    chars, monthly = load("chars_clean", fake), load("crsp_monthly", fake)
    pairs = training_pairs(chars, monthly)
    out = chars[["permno", "month"]].copy()
    for m in MODELS:
        out[f"mu_{m}"] = rolling_forecasts(pairs, chars, m).to_numpy() if m in models else np.nan
    save(out, "mu_hat", fake)
    _ = CFG
