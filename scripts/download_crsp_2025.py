
"""Download CRSP CIZ monthly observations for 2025."""

from pathlib import Path

import wrds

from lrrep.data.crsp import pull_monthly_ciz


def main():
    output = Path("data/real/crsp_ciz_2025_raw.parquet")

    if output.exists():
        raise FileExistsError(
            f"{output} already exists. "
            "The existing file will not be overwritten."
        )

    print("Connecting to WRDS...", flush=True)

    db = wrds.Connection()

    try:
        print("Downloading 2025 monthly CRSP data...", flush=True)

        raw = pull_monthly_ciz(
            db,
            "2025-01-01",
            "2025-12-31",
        )
    finally:
        db.close()

    output.parent.mkdir(parents=True, exist_ok=True)
    raw.to_parquet(
        output,
        index=False,
        compression="snappy",
    )

    print("\n2025 MONTHLY DOWNLOAD COMPLETE")
    print("Saved:", output)
    print("Observations:", len(raw))
    print("Unique securities:", raw["permno"].nunique())
    print("First month:", raw["mthcaldt"].min())
    print("Last month:", raw["mthcaldt"].max())
    print("Missing returns:", raw["mthret"].isna().sum())
    print("Missing market caps:", raw["mthcap"].isna().sum())


if __name__ == "__main__":
    main()
