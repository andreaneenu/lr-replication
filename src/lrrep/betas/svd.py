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

from collections.abc import Iterator

import numpy as np
import pandas as pd

from lrrep.config import CFG
from lrrep.io import figure_path, load, save

_EMPTY_BETAS_COLS = ["permno", "month"]
_EIGEN_COLS = ["month", "k", "eigenvalue", "share_explained"]


# --------------------------------------------------------------------------------------------
# One month
# --------------------------------------------------------------------------------------------

def betas_for_month(window: pd.DataFrame, k_max: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """SVD betas for one month.

    window: crsp_daily rows (permno, date, exret) for the stocks and days in the window.
    Returns (betas: permno, beta_1..beta_k_max) and (eig: k, eigenvalue, share_explained).
    """
    wide = window.pivot(index="date", columns="permno", values="exret").sort_index()
    R = wide.to_numpy(dtype=float)                       # T x N, NaN where a day is missing
    T = R.shape[0]

    R = R - np.nanmean(R)                                # 2. grand mean, not stock by stock
    w = CFG["betas"]["winsor"]
    lo, hi = np.nanquantile(R, [w, 1 - w])               # 3. pooled quantiles
    R = np.clip(R, lo, hi)
    R = np.nan_to_num(R, nan=0.0)                        # missing day -> 0 after demeaning

    _, s, Vt = np.linalg.svd(R, full_matrices=False)     # 4. compact SVD
    V = Vt.T                                             # N x min(T, N), largest factor first
    lam = s**2 / T
    eig = pd.DataFrame({"k": np.arange(1, len(lam) + 1, dtype="int64"),
                        "eigenvalue": lam, "share_explained": lam / lam.sum()})

    K = min(k_max, V.shape[1])
    beta = V[:, :K] * V[:, 0].sum()                      # 5. beta = V / omega_1, omega_1 = 1 / sum(V_1)
    sign = np.sign(beta.mean(axis=0))
    beta = beta * np.where(sign == 0, 1.0, sign)         # each column's mean positive

    betas = pd.DataFrame(beta, columns=[f"beta_{j}" for j in range(1, K + 1)])
    betas.insert(0, "permno", wide.columns.to_numpy().astype("int64"))
    return betas, eig


# --------------------------------------------------------------------------------------------
# Loop over months
# --------------------------------------------------------------------------------------------

def _universe(crsp_monthly: pd.DataFrame) -> dict[pd.Timestamp, np.ndarray]:
    u = crsp_monthly.loc[crsp_monthly["in_universe"], ["month", "permno"]]
    return {m: g.to_numpy() for m, g in u.groupby("month")["permno"]}


def _stack(parts_b: list[pd.DataFrame], parts_e: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    if parts_b:
        betas = pd.concat(parts_b, ignore_index=True)
    else:
        betas = pd.DataFrame({"permno": pd.Series(dtype="int64"), "month": pd.Series(dtype="datetime64[ns]")})
    if parts_e:
        eig = pd.concat(parts_e, ignore_index=True)
    else:
        eig = pd.DataFrame({"month": pd.Series(dtype="datetime64[ns]"), "k": pd.Series(dtype="int64"),
                            "eigenvalue": pd.Series(dtype=float), "share_explained": pd.Series(dtype=float)})
    betas = betas[_EMPTY_BETAS_COLS + [c for c in betas.columns if c.startswith("beta_")]]
    return betas.sort_values(["month", "permno"]).reset_index(drop=True), eig[_EIGEN_COLS]


def _select(window: pd.DataFrame, permnos: np.ndarray | None, min_obs: int) -> pd.DataFrame:
    """Universe stocks at t with at least min_obs non-missing returns in the window."""
    if permnos is None:
        return window.iloc[0:0]
    window = window[window["permno"].isin(permnos)]
    n_obs = window.groupby("permno")["exret"].count()
    return window[window["permno"].isin(n_obs.index[n_obs >= min_obs])]


def _month_list(months, candidates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if months is None:
        return list(candidates)
    return sorted({pd.Timestamp(m) + pd.offsets.MonthEnd(0) for m in months})


def _daily_windows(crsp_daily: pd.DataFrame, crsp_monthly: pd.DataFrame, months, n_days: int
                   ) -> Iterator[tuple[pd.Timestamp, pd.DataFrame]]:
    """Yield (t, daily rows of the last n_days trading days ending at t). Uses only dates <= t."""
    daily = crsp_daily[["permno", "date", "exret"]].sort_values("date", kind="stable")
    dates = daily["date"].to_numpy()
    days = np.unique(dates)
    month_ends = pd.DatetimeIndex(np.sort(crsp_monthly["month"].unique()))
    for t in _month_list(months, month_ends):
        end = np.searchsorted(days, np.datetime64(t), side="right")      # days[:end] are <= t
        if end < n_days or days[end - 1] < np.datetime64(t - pd.offsets.MonthBegin(1)):
            continue                                     # window not full, or no trading day in month t
        lo = np.searchsorted(dates, days[end - n_days], side="left")
        hi = np.searchsorted(dates, days[end - 1], side="right")
        yield t, daily.iloc[lo:hi]


def compute_betas(crsp_daily: pd.DataFrame, crsp_monthly: pd.DataFrame,
                  months: list[pd.Timestamp] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Loop over month-ends (default: every month with a full window) and stack the results.

    Returns (betas_svd, eigen) frames matching their contracts, with a `month` column.
    Must use only daily rows dated <= t for month t (tests/test_member_3.py checks this).
    """
    cfg = CFG["betas"]
    universe = _universe(crsp_monthly)
    parts_b, parts_e = [], []
    for t, window in _daily_windows(crsp_daily, crsp_monthly, months, cfg["window_days"]):
        window = _select(window, universe.get(t), cfg["min_obs"])
        if window["permno"].nunique() < 2:
            continue
        b, e = betas_for_month(window, cfg["k_max"])
        b.insert(1, "month", t)
        e.insert(0, "month", t)
        parts_b.append(b)
        parts_e.append(e)
    return _stack(parts_b, parts_e)


# --------------------------------------------------------------------------------------------
# Figure 1
# --------------------------------------------------------------------------------------------

def figure1(eigen: pd.DataFrame) -> None:
    """Average (over months) cumulative share_explained for k = 1..k_max.
    Paper benchmark: about 10% at k = 5, about 50% at k = 50. Save via lrrep.io.figure_path('figure1')."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    k_max = CFG["betas"]["k_max"]
    e = eigen.sort_values(["month", "k"]).copy()
    e["cum_share"] = e.groupby("month")["share_explained"].cumsum()
    avg = e[e["k"] <= k_max].groupby("k")["cum_share"].mean()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(avg.index, avg.to_numpy() * 100, color="#1f4e79", lw=2)
    for k in (5, 50):
        if k in avg.index:
            ax.scatter([k], [avg[k] * 100], color="#c0392b", zorder=3)
            ax.annotate(f"k = {k}: {avg[k]:.0%}", (k, avg[k] * 100), textcoords="offset points",
                        xytext=(8, -14))
    ax.set_xlabel("Number of factors k")
    ax.set_ylabel("Cumulative share of variance explained (%)")
    ax.set_title("Figure 1: variance explained by the first k latent factors\n"
                 f"(average over {e['month'].nunique()} months)")
    ax.set_xlim(0, avg.index.max())
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p = figure_path("figure1")
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------------------------
# Frequency robustness: weekly returns
# --------------------------------------------------------------------------------------------

def _weekly(daily: pd.DataFrame) -> pd.DataFrame:
    """Compound daily ret and rf within Wednesday-to-Wednesday weeks; weekly exret = ret - rf.
    `date` becomes the last trading day of the week present in `daily`."""
    d = daily.assign(g_ret=np.log1p(daily["ret"]), g_rf=np.log1p(daily["rf"]),
                     week=daily["date"].dt.to_period("W-WED"))
    w = d.groupby(["permno", "week"]).agg(g_ret=("g_ret", "sum"), g_rf=("g_rf", "sum"),
                                          n=("ret", "count"), date=("date", "max")).reset_index()
    w = w[w["n"] > 0]
    w["exret"] = np.expm1(w["g_ret"]) - np.expm1(w["g_rf"])
    # every stock in a week shares the same week-end label, so the pivot lines up across stocks
    w["date"] = w.groupby("week")["date"].transform("max")
    return w[["permno", "date", "exret"]]


def compute_betas_weekly(crsp_daily: pd.DataFrame, crsp_monthly: pd.DataFrame,
                         months: list[pd.Timestamp] | None = None, weeks: int = 104) -> pd.DataFrame:
    """ROBUSTNESS (guideline: 'frequency of observation'): the same SVD betas, but from WEEKLY excess
    returns (compound daily exret within Wednesday-to-Wednesday or calendar weeks) over the past
    `weeks` weeks ending at month-end t. Same normalization. Returns the betas_svd_weekly contract.
    Reuse betas_for_month on the weekly matrix (rename `date` to the week-end date).

    Weeks run Thursday-Wednesday. Only days <= t are used, so the last week of each window
    may be partial (it ends on the last trading day of month t). A stock needs
    weeks * min_obs / window_days non-missing weeks (about 99 of 104).
    """
    cfg = CFG["betas"]
    min_weeks = int(np.ceil(weeks * cfg["min_obs"] / cfg["window_days"]))
    universe = _universe(crsp_monthly)
    daily = crsp_daily[["permno", "date", "ret", "rf"]].sort_values("date", kind="stable")
    dates = daily["date"].to_numpy()
    month_ends = pd.DatetimeIndex(np.sort(crsp_monthly["month"].unique()))
    parts = []
    for t in _month_list(months, month_ends):
        hi = np.searchsorted(dates, np.datetime64(t), side="right")      # rows dated <= t
        if hi == 0 or dates[hi - 1] < np.datetime64(t - pd.offsets.MonthBegin(1)):
            continue
        start = (t - pd.Timedelta(weeks=weeks + 1)).to_datetime64()
        if dates[0] > start:
            continue                                     # not enough history for a full window
        lo = np.searchsorted(dates, start, side="left")
        wk = _weekly(daily.iloc[lo:hi])
        last = np.sort(wk["date"].unique())[-weeks:]
        wk = _select(wk[wk["date"].isin(last)], universe.get(t), min_weeks)
        if wk["permno"].nunique() < 2:
            continue
        b, _ = betas_for_month(wk, cfg["k_max"])
        b.insert(1, "month", t)
        parts.append(b)
    betas, _ = _stack(parts, [])
    return betas


def run(fake: bool = False) -> None:
    daily, monthly = load("crsp_daily", fake), load("crsp_monthly", fake)
    betas, eig = compute_betas(daily, monthly)
    save(betas, "betas_svd", fake)
    save(eig, "eigen", fake)
    figure1(eig)
    save(compute_betas_weekly(daily, monthly), "betas_svd_weekly", fake)
