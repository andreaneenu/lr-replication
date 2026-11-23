"""File contracts: the exact shape of every file passed between members.

Owner: Member 1 (shared file). docs/CONTRACTS.md is the human-readable version of this
module; keep them in sync. A change here needs a PR labelled `contract-change` and an
approval from every member listed in `readers`.

Conventions (apply to every file)
---------------------------------
* `month` is a pandas Timestamp at the calendar month END (e.g. 2001-03-31).
* `date` (daily file only) is a pandas Timestamp at midnight.
* Returns are decimals (0.01 = 1%), never percent.
* Timing rule: a row dated month t only uses information known at the end of month t.
  Predictive files (betas_svd, chars_clean, mu_hat) are indexed by FORMATION month t;
  the return they predict is crsp_monthly.exret at month t+1.
  Return files (crsp_monthly, market, factors_ext, factor_portfolios, portfolios) are
  indexed by the month in which the return is REALIZED.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Contract:
    owner: int                      # member number who writes the file
    readers: tuple[int, ...]        # members who read it
    key: tuple[str, ...]            # unique key columns
    columns: dict[str, str]         # required column -> kind: int|float|bool|datetime
    wide_prefix: str | None = None  # e.g. "beta_": numbered float columns beta_1..beta_K
    wide_min: int = 0               # minimum number of wide columns
    description: str = ""
    extra_float_ok: bool = False    # True if extra float columns are allowed (e.g. chars)


CONTRACTS: dict[str, Contract] = {
    "crsp_daily": Contract(
        owner=2, readers=(3,), key=("permno", "date"),
        columns={"permno": "int", "date": "datetime", "ret": "float", "rf": "float", "exret": "float"},
        description="Daily returns of universe stocks, history_start..end.",
    ),
    "crsp_monthly": Contract(
        owner=2, readers=(4, 5, 6, 7), key=("permno", "month"),
        columns={"permno": "int", "month": "datetime", "ret": "float", "exret": "float",
                 "me": "float", "exchcd": "int", "shrcd": "int", "in_universe": "bool"},
        description="Monthly returns incl. delisting returns; me = market cap in $ millions at month end; "
                    "in_universe = passes share/exchange codes and NYSE 20th pct size filter at month end.",
    ),
    "market": Contract(
        owner=2, readers=(4, 6, 7), key=("month",),
        columns={"month": "datetime", "mkt_exret": "float", "rf": "float"},
        description="Market excess return and risk-free rate (Ken French library).",
    ),
    "factors_ext": Contract(
        owner=7, readers=(4, 6, 7), key=("month",),
        columns={"month": "datetime", "mkt_rf": "float", "smb": "float", "hml": "float",
                 "rmw": "float", "cma": "float", "umd": "float",
                 "q_me": "float", "q_ia": "float", "q_roe": "float", "q_eg": "float",
                 "sy_mgmt": "float", "sy_perf": "float"},
        description="External factors, decimals. q5 from global-q.org, Stambaugh-Yuan mispricing factors.",
    ),
    "betas_svd": Contract(
        owner=3, readers=(4, 6), key=("permno", "month"),
        columns={"permno": "int", "month": "datetime"},
        wide_prefix="beta_", wide_min=5,
        description="Latent-factor betas from the SVD of the past 252 days ending in month t. "
                    "beta_1 is the largest factor. Used as the hedge for month t+1 returns.",
    ),
    "betas_svd_weekly": Contract(
        owner=3, readers=(6,), key=("permno", "month"),
        columns={"permno": "int", "month": "datetime"},
        wide_prefix="beta_", wide_min=5,
        description="ROBUSTNESS (frequency): same as betas_svd but from WEEKLY excess returns over the past "
                    "104 weeks. Member 6 rebuilds the beta-neutral portfolio with these.",
    ),
    "eigen": Contract(
        owner=3, readers=(3,), key=("month", "k"),
        columns={"month": "datetime", "k": "int", "eigenvalue": "float", "share_explained": "float"},
        description="Eigenvalues of the daily covariance each month (for Figures 1 and 3).",
    ),
    "chars_clean": Contract(
        owner=5, readers=(5,), key=("permno", "month"),
        columns={"permno": "int", "month": "datetime"},
        extra_float_ok=True,
        description="Characteristics known at end of month t, standardized cross-sectionally each month. "
                    "Characteristic columns are prefixed c_.",
    ),
    "mu_hat": Contract(
        owner=5, readers=(4, 6, 7), key=("permno", "month"),
        columns={"permno": "int", "month": "datetime", "mu_ols": "float", "mu_lasso": "float", "mu_rf": "float"},
        description="Out-of-sample forecasts, made at end of month t, of exret in month t+1. "
                    "mu_rf may be NaN while the random forest is still running.",
    ),
    "factor_portfolios": Contract(
        owner=4, readers=(4, 7), key=("month",),
        columns={"month": "datetime"},
        wide_prefix="fexp_", wide_min=5,
        description="Zero-cost factor-exposure portfolio returns (beta 1 on factor k, 0 on others), "
                    "realized in `month`.",
    ),
    "earnings_dates": Contract(
        owner=2, readers=(4,), key=("permno", "rdq"),
        columns={"permno": "int", "rdq": "datetime"},
        description="Quarterly earnings announcement dates (Compustat fundq.rdq) linked to permno via "
                    "the CRSP-Compustat link table. Used for the cash-flow news test.",
    ),
    "portfolio_weights": Contract(
        owner=6, readers=(4,), key=("permno", "month"),
        columns={"permno": "int", "month": "datetime", "w_ls": "float", "w_bn": "float"},
        description="Weights of the main unhedged (w_ls) and beta-neutral (w_bn) portfolios formed at the "
                    "end of `month` (formation month t), held during t+1. Each sums to 0, sum|w| = 2.",
    ),
    "portfolios": Contract(
        owner=6, readers=(7,), key=("month",),
        columns={"month": "datetime", "mkt": "float", "ls_main": "float", "bn_main": "float"},
        extra_float_ok=True,
        description="Monthly excess returns realized in `month`. ls_* = unhedged long-short, "
                    "bn_* = beta-neutral. ls_main/bn_main use the main forecast and k_main betas. "
                    "Extra columns: ls_<model>, bn_<model>_k<K>.",
    ),
}

_KIND_CHECKS = {
    "int": pd.api.types.is_integer_dtype,
    "float": pd.api.types.is_float_dtype,
    "bool": pd.api.types.is_bool_dtype,
    "datetime": pd.api.types.is_datetime64_any_dtype,
}


class ContractError(ValueError):
    pass


def wide_columns(df: pd.DataFrame, prefix: str) -> list[str]:
    """Numbered wide columns in numeric order, e.g. beta_1, beta_2, ..."""
    cols = [c for c in df.columns if c.startswith(prefix) and c[len(prefix):].isdigit()]
    return sorted(cols, key=lambda c: int(c[len(prefix):]))


def validate(df: pd.DataFrame, name: str) -> None:
    """Raise ContractError if df does not match the contract for `name`."""
    if name not in CONTRACTS:
        raise ContractError(f"Unknown contract '{name}'. Known: {sorted(CONTRACTS)}")
    c = CONTRACTS[name]
    errors = []
    for col, kind in c.columns.items():
        if col not in df.columns:
            errors.append(f"missing column '{col}'")
        elif not _KIND_CHECKS[kind](df[col]):
            errors.append(f"column '{col}' should be {kind}, got {df[col].dtype}")
    if c.wide_prefix:
        w = wide_columns(df, c.wide_prefix)
        if len(w) < c.wide_min:
            errors.append(f"needs at least {c.wide_min} '{c.wide_prefix}k' columns, found {len(w)}")
        if w and w != [f"{c.wide_prefix}{i}" for i in range(1, len(w) + 1)]:
            errors.append(f"'{c.wide_prefix}' columns must be numbered 1..K with no gaps")
    known = set(c.columns) | set(wide_columns(df, c.wide_prefix) if c.wide_prefix else [])
    extra = [col for col in df.columns if col not in known]
    if extra and not c.extra_float_ok:
        errors.append(f"unexpected columns {extra[:5]}{'...' if len(extra) > 5 else ''}")
    if not errors:
        if df.duplicated(list(c.key)).any():
            errors.append(f"duplicate keys on {c.key}")
        if "month" in df.columns and len(df):
            m = df["month"]
            if not (m == m + pd.offsets.MonthEnd(0)).all():
                errors.append("'month' must be month-end timestamps (use + pd.offsets.MonthEnd(0))")
    if errors:
        raise ContractError(f"{name}: " + "; ".join(errors))
