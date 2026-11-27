
"""Download and process CRSP CIZ daily returns, 1965-2024.

Run from the project root. Licensed data remain in data/real/.
Completed annual batches are reusable after validation.
"""

import gc
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import wrds

from lrrep.contracts import validate
from lrrep.data.crsp import build_daily, pull_daily, pull_daily_risk_free

START_YEAR = 1965
END_YEAR = 2024

DATA_DIR = Path("data/real")
BATCH_DIR = DATA_DIR / "daily_batches"

def download_daily() -> None:
    """Execute the historical CRSP extraction workflow."""
    output = DATA_DIR / "crsp_daily.parquet"

    if output.exists():
        raise FileExistsError(
            f"{output} already exists. "
            "Existing validated data will not be overwritten."
        )

    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    monthly = pd.read_parquet(
        DATA_DIR / "crsp_monthly.parquet",
        columns=["permno", "month", "in_universe"],
    )

    permnos = (
        monthly.loc[monthly["in_universe"], "permno"]
        .drop_duplicates()
        .astype(int)
        .tolist()
    )

    print("Eligible securities:", len(permnos), flush=True)

    # Download the daily risk-free series once.
    rf_daily = pull_daily_risk_free()

    # The build_daily function uses universe membership to retain
    # historical observations of securities ever eligible.
    membership = monthly.loc[
        monthly["in_universe"], ["permno", "in_universe"]
    ].drop_duplicates(subset=["permno"])

    del monthly
    gc.collect()

    print("Connecting to WRDS...", flush=True)
    db = wrds.Connection()

    try:
        for year in range(START_YEAR, END_YEAR + 1):
            path = BATCH_DIR / f"crsp_daily_{year}.parquet"

            # Validate existing batches before skipping them.
            if path.exists():
                try:
                    existing = pd.read_parquet(path)
                    validate(existing, "crsp_daily")
                    print(f"{year}: validated existing batch, skipping", flush=True)
                    del existing
                    continue
                except Exception:
                    print(f"{year}: invalid batch, rebuilding", flush=True)

            print(f"\nProcessing {year}...", flush=True)

            raw = pull_daily(
                db,
                permnos,
                f"{year}-01-01",
                f"{year}-12-31",
            )

            processed = build_daily(raw, rf_daily, membership)

            validate(processed, "crsp_daily")

            if processed.duplicated(["permno", "date"]).any():
                raise ValueError(f"{year}: duplicate stock-days")

            # Write to a temporary file, then rename when complete.
            temp = path.with_suffix(".tmp.parquet")
            processed.to_parquet(
                temp,
                index=False,
                compression="snappy",
            )
            temp.replace(path)

            print(
                f"{year}: {len(processed):,} daily observations, "
                f"{processed['permno'].nunique():,} securities",
                flush=True,
            )

            del raw, processed
            gc.collect()

    finally:
        db.close()

    # Combine batches without loading all years into pandas.
    print("\nCombining annual batches...", flush=True)

    output = DATA_DIR / "crsp_daily.parquet"
    temp_output = DATA_DIR / "crsp_daily.tmp.parquet"

    writer = None
    total_rows = 0

    try:
        for year in range(START_YEAR, END_YEAR + 1):
            path = BATCH_DIR / f"crsp_daily_{year}.parquet"

            if not path.exists():
                raise FileNotFoundError(f"Missing batch: {path}")

            parquet_file = pq.ParquetFile(path)

            for record_batch in parquet_file.iter_batches(
                batch_size=100_000
            ):
                table = pa.Table.from_batches([record_batch])

                if writer is None:
                    writer = pq.ParquetWriter(
                        temp_output,
                        table.schema,
                        compression="snappy",
                    )

                writer.write_table(table)
                total_rows += table.num_rows

            print(f"{year}: combined", flush=True)

    finally:
        if writer is not None:
            writer.close()

    if total_rows == 0:
        raise ValueError("No daily observations were combined")

    temp_output.replace(output)

    print("\nFULL CRSP DAILY DATASET COMPLETE")
    print("Saved:", output)
    print("Total observations:", f"{total_rows:,}")
    print("First year:", START_YEAR)
    print("Last year:", END_YEAR)


if __name__ == '__main__':
    download_daily()
