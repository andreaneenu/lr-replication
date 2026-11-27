
"""Combine validated CRSP history and 2025 extension safely."""


import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from lrrep.config import data_dir
from lrrep.contracts import validate


def main():
    folder = data_dir()

    monthly_output = folder / "crsp_monthly_1965_2025.parquet"
    daily_output = folder / "crsp_daily_1965_2025.parquet"

    # Never overwrite existing outputs.
    for output in [monthly_output, daily_output]:
        if output.exists():
            raise FileExistsError(f"Output already exists: {output}")

    # -------- Monthly --------
    historical = pd.read_parquet(folder / "crsp_monthly.parquet")
    extension = pd.read_parquet(folder / "crsp_monthly_2025.parquet")

    validate(historical, "crsp_monthly")
    validate(extension, "crsp_monthly")

    if historical["month"].max() != pd.Timestamp("2024-12-31"):
        raise ValueError("Unexpected historical monthly endpoint")

    if extension["month"].min() != pd.Timestamp("2025-01-31"):
        raise ValueError("Unexpected extension starting month")

    monthly = pd.concat(
        [historical, extension], ignore_index=True
    )

    validate(monthly, "crsp_monthly")

    if len(monthly) != 4_794_499:
        raise ValueError("Unexpected combined monthly row count")

    temp_monthly = monthly_output.with_suffix(".tmp.parquet")
    monthly.to_parquet(
        temp_monthly, index=False, compression="snappy"
    )
    temp_monthly.replace(monthly_output)

    print("MONTHLY COMBINATION COMPLETE")
    print("Rows:", len(monthly))
    print("Eligible:", int(monthly["in_universe"].sum()))
    print("Saved:", monthly_output)

    del historical, extension, monthly

    # -------- Daily --------
    # Stream Parquet batches to avoid loading 49m rows.
    sources = [
        folder / "crsp_daily.parquet",
        folder / "crsp_daily_2025.parquet",
    ]

    temp_daily = daily_output.with_suffix(".tmp.parquet")

    writer = None
    total_rows = 0

    try:
        for source in sources:
            parquet_file = pq.ParquetFile(source)

            for batch in parquet_file.iter_batches(
                batch_size=100_000
            ):
                table = pa.Table.from_batches([batch])

                if writer is None:
                    writer = pq.ParquetWriter(
                        temp_daily,
                        table.schema,
                        compression="snappy",
                    )

                writer.write_table(table)
                total_rows += table.num_rows

    finally:
        if writer is not None:
            writer.close()

    if total_rows != 49_133_093:
        raise ValueError(
            f"Unexpected combined daily count: {total_rows}"
        )

    temp_daily.replace(daily_output)

    print("\nDAILY COMBINATION COMPLETE")
    print("Rows:", total_rows)
    print("Saved:", daily_output)
    print("\nCOMBINATION FINISHED")


if __name__ == "__main__":
    main()
