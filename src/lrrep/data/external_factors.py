"""External factors for the alpha regressions: FF5 + momentum, q5, Stambaugh-Yuan.

Owner: Member 7. Writes: factors_ext. Spec: docs/members/member-7.md

Sources (`download_raw` fetches them; or download by hand into the shared data folder under
raw/factors/, never in git):
- Fama-French 5 factors (2x3) and momentum, monthly: Ken French data library
  (F-F_Research_Data_5_Factors_2x3_CSV.zip, F-F_Momentum_Factor_CSV.zip). PERCENT: divide by 100.
  The CSVs also hold an annual block (4-digit years), which is skipped; -99.99 / -999 = missing.
- q5 factors, monthly: global-q.org, q5_factors_monthly_<year>.csv (year, month, R_F, R_MKT,
  R_ME, R_IA, R_ROE, R_EG). PERCENT: divide by 100.
- Stambaugh-Yuan mispricing factors: M4.csv (YYYYMM, MKTRF, SMB, MGMT, PERF, RF) from
  Robert Stambaugh's website. Already DECIMALS. The published file ends in 2016-12.

mkt_rf and smb come from Fama-French; SY's own SMB is not in the contract (docs/DEVIATIONS.md).
"""
from __future__ import annotations

import io
import re
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from lrrep.io import save

FF_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FF5_FILE = "F-F_Research_Data_5_Factors_2x3_CSV.zip"
MOM_FILE = "F-F_Momentum_Factor_CSV.zip"
Q5_URL = "https://global-q.org/uploads/1/2/2/6/122679606/q5_factors_monthly_{year}.csv"
SY_URL = "https://faculty.wharton.upenn.edu/wp-content/uploads/2016/11/M4.csv"
COLUMNS = ["month", "mkt_rf", "smb", "hml", "rmw", "cma", "umd",
           "q_me", "q_ia", "q_roe", "q_eg", "sy_mgmt", "sy_perf"]
_YYYYMM = re.compile(r"^\s*(\d{6})\s*$")


def _month_end(yyyymm: pd.Series) -> pd.Series:
    return pd.to_datetime(yyyymm.astype(str), format="%Y%m") + pd.offsets.MonthEnd(0)


def _read_text(path: Path) -> str:
    """Text of a CSV, or of the single CSV inside a zip."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
            return z.read(name).decode("latin-1")
    return path.read_text(encoding="latin-1")


def _find(raw_dir: Path, pattern: str) -> Path:
    hits = sorted(Path(raw_dir).glob(pattern))
    if not hits:
        raise FileNotFoundError(f"no file matching {pattern} in {raw_dir} (run download_raw or see module docstring)")
    return hits[-1]  # latest vintage if several (names sort by year)


def parse_french(text: str) -> pd.DataFrame:
    """Monthly block of a Ken French CSV: header row starting with ',' then YYYYMM rows.
    Returns month + the file's columns, still in PERCENT, with -99.99/-999 set to NaN."""
    lines = text.splitlines()
    out, header = [], None
    for line in lines:
        cells = [c.strip() for c in line.split(",")]
        if header is None:
            if line.startswith(",") and len(cells) > 1:
                header = cells[1:]
            continue
        if _YYYYMM.match(cells[0]):
            out.append([cells[0]] + cells[1:len(header) + 1])
        elif out:  # first non-monthly line after the block (blank / "Annual Factors")
            break
    if header is None or not out:
        raise ValueError("no monthly block found in Fama-French file")
    df = pd.DataFrame(out, columns=["yyyymm"] + header)
    vals = df[header].apply(pd.to_numeric, errors="coerce").replace([-99.99, -999.0], np.nan)
    vals.insert(0, "month", _month_end(df["yyyymm"]))
    return vals


def load_ff(raw_dir) -> pd.DataFrame:
    """Return month, mkt_rf, smb, hml, rmw, cma, umd in decimals."""
    ff5 = parse_french(_read_text(_find(raw_dir, "F-F_Research_Data_5_Factors_2x3*")))
    mom = parse_french(_read_text(_find(raw_dir, "F-F_Momentum_Factor*")))
    ff5 = ff5.rename(columns={"Mkt-RF": "mkt_rf", "SMB": "smb", "HML": "hml", "RMW": "rmw", "CMA": "cma"})
    mom = mom.rename(columns={mom.columns[1]: "umd"})[["month", "umd"]]
    df = ff5[["month", "mkt_rf", "smb", "hml", "rmw", "cma"]].merge(mom, on="month", how="left")
    df.iloc[:, 1:] = df.iloc[:, 1:] / 100.0
    return df


def load_q5(raw_dir) -> pd.DataFrame:
    """Return month, q_me, q_ia, q_roe, q_eg in decimals."""
    raw = pd.read_csv(_find(raw_dir, "q5_factors_monthly*.csv"))
    raw.columns = [c.strip().upper() for c in raw.columns]
    month = pd.to_datetime(dict(year=raw["YEAR"], month=raw["MONTH"], day=1)) + pd.offsets.MonthEnd(0)
    out = pd.DataFrame({"month": month})
    for src, dst in [("R_ME", "q_me"), ("R_IA", "q_ia"), ("R_ROE", "q_roe"), ("R_EG", "q_eg")]:
        out[dst] = pd.to_numeric(raw[src], errors="coerce") / 100.0
    return out


def load_sy(raw_dir) -> pd.DataFrame:
    """Return month, sy_mgmt, sy_perf in decimals (the source file is already in decimals)."""
    raw = pd.read_csv(_find(raw_dir, "M4*.csv"))
    raw.columns = [c.strip().upper() for c in raw.columns]
    out = pd.DataFrame({"month": _month_end(raw["YYYYMM"]),
                        "sy_mgmt": pd.to_numeric(raw["MGMT"], errors="coerce"),
                        "sy_perf": pd.to_numeric(raw["PERF"], errors="coerce")})
    if out[["sy_mgmt", "sy_perf"]].abs().max().max() > 1:  # guard against a percent vintage
        raise ValueError("Stambaugh-Yuan file looks like it is in percent; expected decimals")
    return out


def build_factors(raw_dir) -> pd.DataFrame:
    """Outer-join the three sources on month (month-end), columns as CONTRACTS['factors_ext']."""
    df = load_ff(raw_dir).merge(load_q5(raw_dir), on="month", how="outer").merge(load_sy(raw_dir), on="month", how="outer")
    df = df.sort_values("month").reset_index(drop=True)[COLUMNS]
    df[COLUMNS[1:]] = df[COLUMNS[1:]].astype(float)
    return df


def download_raw(raw_dir, q5_years: range | None = None) -> list[Path]:
    """Fetch the public factor files into raw_dir. q5 tries this year back to 5 years ago."""
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    def get(url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (lrrep)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()

    saved = []
    for f in (FF5_FILE, MOM_FILE):
        (raw_dir / f).write_bytes(get(FF_URL + f))
        saved.append(raw_dir / f)
    for y in q5_years or range(date.today().year, date.today().year - 6, -1):
        try:
            body = get(Q5_URL.format(year=y))
        except OSError:
            continue
        if body.lstrip().lower().startswith(b"year"):
            (raw_dir / f"q5_factors_monthly_{y}.csv").write_bytes(body)
            saved.append(raw_dir / f"q5_factors_monthly_{y}.csv")
            break
    else:
        raise RuntimeError("could not download a q5 file from global-q.org; fetch it by hand")
    body = get(SY_URL)
    pd.read_csv(io.BytesIO(body), nrows=1)  # fail loudly if we got an HTML page
    (raw_dir / "M4.csv").write_bytes(body)
    saved.append(raw_dir / "M4.csv")
    return saved


def run(fake: bool = False) -> None:
    if fake:
        print("external factors: fake file comes from `make fake`; nothing to do")
        return
    from lrrep.config import data_dir

    raw = data_dir() / "raw" / "factors"
    if not any(raw.glob("q5_factors_monthly*.csv")):
        download_raw(raw)
    df = build_factors(raw)
    save(df, "factors_ext")
    for c in ("mkt_rf", "umd", "q_me", "sy_mgmt"):
        s = df.dropna(subset=[c])["month"]
        print(f"factors_ext {c}: {s.min():%Y-%m} .. {s.max():%Y-%m}")
    print(f"factors_ext: {len(df)} rows, {df.month.min():%Y-%m} .. {df.month.max():%Y-%m}")
