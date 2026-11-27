
"""Build and validate processed CRSP daily returns for 2025."""

import pandas as pd

from lrrep.config import data_dir
from lrrep.contracts import validate
from lrrep.data.crsp import pull_daily_risk_free


def main():
    folder = data_dir()

    source = folder / "crsp_daily_2025_raw.parquet"
    output = folder / "crsp_daily_2025.parquet"

    if output.exists():
        raise FileExistsError(
            f"{output} already exists. "
            "Existing data will not be overwritten."
        )

    raw = pd.read_parquet(source)
    rf = pull_daily_risk_free()

    print("Raw daily observations:", len(raw))

    # Standardize dates and numeric returns.
    raw["date"] = pd.to_datetime(raw["date"]).dt.normalize()
    raw["ret"] = pd.to_numeric(raw["ret"], errors="coerce")

    rf["date"] = pd.to_datetime(rf["date"]).dt.normalize()
    rf["rf"] = pd.to_numeric(rf["rf"], errors="coerce")

    # Remove missing stock returns, consistent with historical processing.
    daily = raw.dropna(subset=["ret"]).copy()

    # Attach daily risk-free rates.
    daily = daily.merge(
        rf[["date", "rf"]],
        on="date",
        how="left",
        validate="many_to_one",
    )

    if daily["rf"].isna().any():
        raise ValueError(
            "Some 2025 trading dates have missing risk-free rates."
        )

    # Calculate excess returns.
    daily["exret"] = daily["ret"] - daily["rf"]

    # Match the official crsp_daily contract.
    out = daily[
        ["permno", "date", "ret", "rf", "exret"]
    ].copy()

    out["permno"] = out["permno"].astype("int64")

    out = out.sort_values(
        ["permno", "date"]
    ).reset_index(drop=True)

    validate(out, "crsp_daily")

    # Write safely using a temporary file.
    temporary = output.with_suffix(".tmp.parquet")

    out.to_parquet(
        temporary,
        index=False,
        compression="snappy",
    )

    temporary.replace(output)

    print("\n2025 DAILY PROCESSING COMPLETE")
    print("Saved:", output)
    print("Observations:", len(out))
    print("Unique securities:", out["permno"].nunique())
    print("First date:", out["date"].min())
    print("Last date:", out["date"].max())
    print("Missing returns:", out["ret"].isna().sum())
    print("Missing risk-free rates:", out["rf"].isna().sum())
    print(
        "Duplicate stock-days:",
        out.duplicated(["permno", "date"]).sum(),
    )


if __name__ == "__main__":
    main()
