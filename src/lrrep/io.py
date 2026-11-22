"""Read and write contract files. Every save is validated against lrrep.contracts.

Owner: Member 1 (shared file).

Usage:
    from lrrep.io import load, save
    daily = load("crsp_daily", fake=True)
    save(betas_df, "betas_svd", fake=True)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from lrrep.config import data_dir, results_dir
from lrrep.contracts import validate


def path_for(name: str, fake: bool = False) -> Path:
    return data_dir(fake) / f"{name}.parquet"


def load(name: str, fake: bool = False, columns: list[str] | None = None) -> pd.DataFrame:
    p = path_for(name, fake)
    if not p.exists():
        hint = "run `make fake`" if fake else "sync the shared data folder or ask the file's owner (see docs/CONTRACTS.md)"
        raise FileNotFoundError(f"{p} not found: {hint}")
    return pd.read_parquet(p, columns=columns)


def save(df: pd.DataFrame, name: str, fake: bool = False) -> Path:
    validate(df, name)
    p = path_for(name, fake)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)
    return p


def save_table(df: pd.DataFrame, name: str) -> Path:
    """Save a results table (small CSV, committed to git) as results/tables/<name>.csv."""
    p = results_dir() / "tables" / f"{name}.csv"
    df.to_csv(p)
    return p


def figure_path(name: str) -> Path:
    """Path for a results figure, results/figures/<name>.png."""
    return results_dir() / "figures" / f"{name}.png"
