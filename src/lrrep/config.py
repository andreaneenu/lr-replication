"""Load config.yaml once and expose it as CFG (a plain dict).

Owner: Member 1 (shared file: change only by reviewed PR).
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_config(path: Path | None = None) -> dict:
    path = path or REPO_ROOT / "config.yaml"
    with open(path) as f:
        cfg = yaml.safe_load(f)
    env_dir = os.environ.get("LRREP_DATA_DIR")
    if env_dir:
        cfg["paths"]["data_dir"] = env_dir
    return cfg


CFG = load_config()


def data_dir(fake: bool = False) -> Path:
    """Folder holding the Parquet contract files (real or fake)."""
    p = CFG["paths"]["fake_dir"] if fake else CFG["paths"]["data_dir"]
    p = Path(p)
    return p if p.is_absolute() else REPO_ROOT / p


def results_dir() -> Path:
    p = REPO_ROOT / CFG["paths"]["results_dir"]
    (p / "tables").mkdir(parents=True, exist_ok=True)
    (p / "figures").mkdir(parents=True, exist_ok=True)
    return p
