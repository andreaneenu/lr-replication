"""Latent-factor betas from the SVD of the daily return matrix (paper Section 2.1).

Owner: Member 3. Reads: crsp_daily, crsp_monthly. Writes: betas_svd, eigen.
Outputs: Figure 1 (cumulative share of variance explained by the first k factors),
optional Figure 3 (share explained over time). Spec: docs/members/member-3.md

Method for each month-end t:
 1. R = T x N matrix of daily EXCESS returns over the last CFG['betas']['window_days'] trading
    days ending at t, for stocks with in_universe == True at t and at least
    CFG['betas']['min_obs'] non-missing days in the window.
 2. Demean with the GRAND mean of R (one number across all stocks and days), not stock means.
 3. Winsorize R at CFG['betas']['winsor'] and 1 - winsor (pooled quantiles).
    Missing days: set to 0 AFTER demeaning (document this choice; it is ours, not the paper's).
 4. Compact SVD: R = U S V'. V is N x T. Column k of V holds the betas on factor k.
    Eigenvalues of the covariance: lambda_k = s_k^2 / T. share_explained_k = lambda_k / sum(lambda).
 5. Normalization (paper p.13): omega_1 = 1 / sum(V[:, 0]); beta_k = V[:, k] / omega_1.
    Then flip the sign of each beta_k column so its cross-sectional mean is positive.
    (Scaling does not change which portfolios are beta-neutral; it only makes columns comparable.)
 6. Save the first CFG['betas']['k_max'] betas as beta_1..beta_K, plus eigenvalues for all k.

Hedging later uses betas_svd at month t for returns in t+1: that is "last month's betas".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import load, save


def betas_for_month(window: pd.DataFrame, k_max: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """SVD betas for one month.

    window: crsp_daily rows (permno, date, exret) for the stocks and days in the window.
    Returns (betas: permno, beta_1..beta_k_max) and (eig: k, eigenvalue, share_explained).
    """
    raise NotImplementedError("Member 3: SVD betas for one month")


def compute_betas(crsp_daily: pd.DataFrame, crsp_monthly: pd.DataFrame,
                  months: list[pd.Timestamp] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loop over month-ends (default: every month with a full window) and stack the results.

    Returns (betas_svd, eigen) frames matching their contracts, with a `month` column.
    Must use only daily rows dated <= t for month t (tests/test_member_3.py checks this).
    """
    raise NotImplementedError("Member 3: loop over months")


def figure1(eigen: pd.DataFrame) -> None:
    """Average (over months) cumulative share_explained for k = 1..k_max.
    Paper benchmark: about 10% at k = 5, about 50% at k = 50. Save via lrrep.io.figure_path('figure1')."""
    raise NotImplementedError("Member 3: Figure 1")


def compute_betas_weekly(crsp_daily: pd.DataFrame, crsp_monthly: pd.DataFrame,
                         months: list[pd.Timestamp] | None = None, weeks: int = 104) -> pd.DataFrame:
    """ROBUSTNESS (guideline: 'frequency of observation'): the same SVD betas, but from WEEKLY excess
    returns (compound daily exret within Wednesday-to-Wednesday or calendar weeks) over the past
    `weeks` weeks ending at month-end t. Same normalization. Returns the betas_svd_weekly contract.
    Reuse betas_for_month on the weekly matrix (rename `date` to the week-end date)."""
    raise NotImplementedError("Member 3: weekly-return betas")


def run(fake: bool = False) -> None:
    daily, monthly = load("crsp_daily", fake), load("crsp_monthly", fake)
    betas, eig = compute_betas(daily, monthly)
    save(betas, "betas_svd", fake)
    save(eig, "eigen", fake)
    figure1(eig)
    save(compute_betas_weekly(daily, monthly), "betas_svd_weekly", fake)
    _ = (np, CFG)
