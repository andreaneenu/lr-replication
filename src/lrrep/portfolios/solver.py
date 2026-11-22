"""Pure-play portfolio solver (paper Section 2.5, eqs 27-32). Shared by Members 4 and 6.

Owner: Member 1. Implemented and unit-tested (tests/test_solver.py); do not change its
behaviour without a reviewed PR.

Problem, for one month's cross-section of N stocks:

    minimize   1/2 w' Omega w
    subject to A' w = a0

Solution: w = Omega^-1 A (A' Omega^-1 A)^-1 a0      (eq 30)
With Omega = I (equal weighting):   w = A (A'A)^-1 a0   (eq 31)
Value weighting: Omega_ii = 1 / market cap.

The weights are linear in the target, so we rescale them so that sum(|w|) = 2
(a normal $1 long / $1 short book). Scaling does not change the Sharpe ratio.
"""
from __future__ import annotations

import numpy as np


def solve_pure_play(A: np.ndarray, a0: np.ndarray, omega_diag: np.ndarray | None = None) -> np.ndarray:
    """Return w minimizing 1/2 w' diag(omega) w subject to A' w = a0.

    A: (N, m) constraint matrix, a0: (m,) targets, omega_diag: (N,) positive weights
    (None = identity). Uses least squares on the small m x m system, so it is
    robust when constraints are nearly collinear.
    """
    A = np.asarray(A, float)
    a0 = np.asarray(a0, float)
    inv_om = np.ones(A.shape[0]) if omega_diag is None else 1.0 / np.asarray(omega_diag, float)
    OA = A * inv_om[:, None]                      # Omega^-1 A
    M = A.T @ OA                                  # A' Omega^-1 A   (m x m)
    lam, *_ = np.linalg.lstsq(M, a0, rcond=None)
    return OA @ lam


def normalize_gross(w: np.ndarray, gross: float = 2.0) -> np.ndarray:
    s = np.abs(w).sum()
    return w * (gross / s) if s > 0 else w


def expected_return_portfolio(mu: np.ndarray, betas: np.ndarray | None = None,
                              omega_diag: np.ndarray | None = None) -> np.ndarray:
    """Zero-cost portfolio with exposure to the forecast `mu`.

    betas=None   -> unhedged long-short (eqs 33-35): constraints sum(w)=0, w'mu=1.
    betas (N,K)  -> beta-neutral (eqs 36-39): also w'beta_k = 0 for every k.
    Returns weights scaled to sum(|w|) = 2. Rows with NaN must be dropped by the caller.
    """
    mu = np.asarray(mu, float)
    cols = [np.ones_like(mu), mu]
    if betas is not None:
        cols += list(np.asarray(betas, float).T)
    A = np.column_stack(cols)
    a0 = np.zeros(A.shape[1])
    a0[1] = 1.0
    return normalize_gross(solve_pure_play(A, a0, omega_diag))


def factor_exposure_portfolio(betas: np.ndarray, k: int, omega_diag: np.ndarray | None = None,
                              zero_cost: bool = True) -> np.ndarray:
    """Portfolio with beta 1 on factor k (0-based) and 0 on all other factors (eqs 15-18).

    zero_cost=True adds sum(w)=0 (the paper's zero-cost factor-exposure portfolios, Table 2).
    Returns weights scaled to sum(|w|) = 2.
    """
    B = np.asarray(betas, float)
    cols = ([np.ones(B.shape[0])] if zero_cost else []) + list(B.T)
    A = np.column_stack(cols)
    a0 = np.zeros(A.shape[1])
    a0[(1 if zero_cost else 0) + k] = 1.0
    return normalize_gross(solve_pure_play(A, a0, omega_diag))
