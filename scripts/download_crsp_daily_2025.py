
"""Download 2025 CRSP CIZ daily observations without overwriting history."""


import pandas as pd
import wrds

from lrrep.config import data_dir
from lrrep.data.crsp import pull_daily


def main():
    output = data_dir() / "crsp_daily_2025_raw.parquet"

    if output.exists():
        raise FileExistsError(f"File already exists: {output}")

    historical = pd.read_parquet(
        data_dir() / "crsp_monthly.parquet",
        columns=["permno", "in_universe"],
    )

    raw_monthly = pd.read_parquet(
        data_dir() / "crsp_ciz_2025_raw.parquet",
        columns=[
            "permno", "securitytype", "securitysubtype",
            "sharetype", "primaryexch",
        ],
    )

    historical_permnos = set(
        historical.loc[
            historical["in_universe"].fillna(False), "permno"
        ].astype(int)
    )

    ciz_common = (
        raw_monthly["securitytype"].eq("EQTY")
        & raw_monthly["securitysubtype"].eq("COM")
        & raw_monthly["sharetype"].eq("NS")
        & raw_monthly["primaryexch"].isin(["N", "A", "Q"])
    )

    candidates_2025 = set(
        raw_monthly.loc[ciz_common, "permno"].astype(int)
    )

    permnos = sorted(historical_permnos | candidates_2025)

    print("Securities requested:", len(permnos), flush=True)

    db = wrds.Connection()
    try:
        raw = pull_daily(
            db, permnos, "2025-01-01", "2025-12-31"
        )
    finally:
        db.close()

    if raw.empty:
        raise ValueError("WRDS returned no daily observations")

    if raw.duplicated(["permno", "date"]).any():
        raise ValueError("Duplicate 2025 stock-day observations")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp.parquet")

    raw.to_parquet(
        temporary, index=False, compression="snappy"
    )
    temporary.replace(output)

    print("\n2025 DAILY DOWNLOAD COMPLETE")
    print("Saved:", output)
    print("Observations:", len(raw))
    print("Unique securities:", raw["permno"].nunique())
    print("First date:", raw["date"].min())
    print("Last date:", raw["date"].max())
    print("Missing daily returns:", raw["ret"].isna().sum())


if __name__ == "__main__":
    main()
