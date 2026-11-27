
"""Download and build CRSP monthly data, 1965-2024.

Run from the lr-replication project root.

Raw CRSP data and intermediate batches remain local.
Never commit these files to GitHub.
"""


import pandas as pd
import wrds

from lrrep.config import data_dir
from lrrep.contracts import validate
from lrrep.data.crsp import (
    build_monthly_ciz,
    pull_monthly_ciz,
)
from lrrep.io import load

START_YEAR = 1965
END_YEAR = 2024

DATA_DIR = data_dir(fake=False)
BATCH_DIR = DATA_DIR / "monthly_batches"


def download_monthly() -> None:
    """Execute the historical CRSP extraction workflow."""
    output = DATA_DIR / "crsp_monthly.parquet"

    if output.exists():
        raise FileExistsError(
            f"{output} already exists. "
            "Existing validated data will not be overwritten."
        )

    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    market = load("market")

    # Restrict the risk-free data to the required sample.
    market = market.loc[
        market["month"].dt.year.between(
            START_YEAR, END_YEAR
        )
    ].copy()

    print("Connecting to WRDS...")

    db = wrds.Connection()

    try:
        # Download historical classifications once.
        print("Downloading historical CRSP classifications...")

        names = db.raw_sql(
            """
            SELECT permno, namedt, nameendt, shrcd, exchcd
            FROM crsp.msenames
            WHERE namedt <= %(end)s
              AND nameendt >= %(start)s
            """,
            params={
                "start": f"{START_YEAR}-01-01",
                "end": f"{END_YEAR}-12-31",
            },
            date_cols=["namedt", "nameendt"],
        )

        print("Classification records:", len(names))

        # Process the monthly data one year at a time.
        for year in range(START_YEAR, END_YEAR + 1):

            batch_path = BATCH_DIR / f"crsp_monthly_{year}.parquet"

            if batch_path.exists():
                print(f"{year}: already completed, skipping")
                continue

            print(f"\nProcessing {year}...")

            raw = pull_monthly_ciz(
                db,
                f"{year}-01-01",
                f"{year}-12-31",
            )

            if raw.empty:
                raise ValueError(
                    f"No CRSP observations found for {year}"
                )

            # Only classification records overlapping this year.
            year_names = names.loc[
                (names["namedt"] <= pd.Timestamp(f"{year}-12-31"))
                & (names["nameendt"] >= pd.Timestamp(f"{year}-01-01"))
            ].copy()

            processed = build_monthly_ciz(
                raw,
                year_names,
                market,
            )

            validate(processed, "crsp_monthly")

            if len(processed) != len(raw):
                raise ValueError(
                    f"{year}: observation count changed"
                )

            processed.to_parquet(
                batch_path,
                index=False,
                compression="snappy",
            )

            print(
                f"{year}: {len(processed):,} observations, "
                f"{int(processed['in_universe'].sum()):,} eligible"
            )

            # Release annual DataFrames before the next year.
            del raw, processed

    finally:
        db.close()

    # Combine the annual batches.
    print("\nCombining annual datasets...")

    files = [
        BATCH_DIR / f"crsp_monthly_{year}.parquet"
        for year in range(START_YEAR, END_YEAR + 1)
    ]

    missing = [str(p) for p in files if not p.exists()]

    if missing:
        raise FileNotFoundError(
            f"Missing annual batches: {missing}"
        )

    full = pd.concat(
        [pd.read_parquet(p) for p in files],
        ignore_index=True,
    )

    full = full.sort_values(
        ["permno", "month"]
    ).reset_index(drop=True)

    validate(full, "crsp_monthly")

    # Save the official project dataset.
    output = DATA_DIR / "crsp_monthly.parquet"

    full.to_parquet(
        output,
        index=False,
        compression="snappy",
    )

    print("\nFULL CRSP MONTHLY DATASET COMPLETE")
    print("Saved:", output)
    print("Total observations:", len(full))
    print("Unique securities:", full["permno"].nunique())
    print("Eligible observations:", int(full["in_universe"].sum()))
    print("First month:", full["month"].min())
    print("Last month:", full["month"].max())
    print("Missing returns:", int(full["ret"].isna().sum()))
    print("Missing market caps:", int(full["me"].isna().sum()))
    print(
        "Unmatched classifications:",
        int((full["shrcd"] == -1).sum()),
    )


if __name__ == '__main__':
    download_monthly()
