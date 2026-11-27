
"""Build 2025 CRSP monthly data using CIZ-native classifications."""

import pandas as pd

from lrrep.config import data_dir
from lrrep.contracts import validate
from lrrep.io import load


def main():
    folder = data_dir()

    source = folder / "crsp_ciz_2025_raw.parquet"
    output = folder / "crsp_monthly_2025.parquet"

    if output.exists():
        raise FileExistsError(
            f"{output} already exists; refusing to overwrite."
        )

    raw = pd.read_parquet(source)
    market = load("market")

    df = raw.copy()

    df["month"] = (
        pd.to_datetime(df["mthcaldt"])
        + pd.offsets.MonthEnd(0)
    )

    df["ret"] = pd.to_numeric(
        df["mthret"], errors="coerce"
    ).astype("float64")

    df["me"] = (
        pd.to_numeric(df["mthcap"], errors="coerce")
        / 1000.0
    ).astype("float64")

    # Proxy share codes, NOT genuine legacy CRSP codes.
    common = (
        df["securitytype"].eq("EQTY")
        & df["securitysubtype"].eq("COM")
        & df["sharetype"].eq("NS")
    )

    df["shrcd"] = common.map(
        {True: 11, False: -1}
    ).astype("int64")

    # Proxy exchange codes.
    exchange_map = {"N": 1, "A": 2, "Q": 3}

    df["exchcd"] = (
        df["primaryexch"]
        .map(exchange_map)
        .fillna(-1)
        .astype("int64")
    )

    # Broad CIZ common-stock candidates.
    candidate = (
        common
        & df["exchcd"].isin([1, 2, 3])
        & df["me"].gt(0)
    )

    # NYSE size threshold by month.
    nyse = candidate & df["exchcd"].eq(1)

    p20 = (
        df.loc[nyse]
        .groupby("month")["me"]
        .quantile(0.20)
    )

    if len(p20) != 12:
        raise ValueError(
            "Missing NYSE size threshold for one or more 2025 months"
        )

    df["p20"] = df["month"].map(p20)

    df["in_universe"] = (
        candidate
        & df["me"].ge(df["p20"])
    ).fillna(False).astype(bool)

    # Attach monthly risk-free rates.
    rf = market[["month", "rf"]].copy()

    df = df.merge(
        rf,
        on="month",
        how="left",
        validate="many_to_one",
    )

    if df["rf"].isna().any():
        raise ValueError(
            "Missing monthly risk-free rates for 2025"
        )

    df["exret"] = (
        df["ret"] - df["rf"]
    ).astype("float64")

    out = df[
        [
            "permno", "month", "ret", "exret",
            "me", "exchcd", "shrcd", "in_universe",
        ]
    ].copy()

    out["permno"] = out["permno"].astype("int64")

    out = out.sort_values(
        ["permno", "month"]
    ).reset_index(drop=True)

    validate(out, "crsp_monthly")

    if out["month"].nunique() != 12:
        raise ValueError("Expected 12 months of 2025 data")

    # Verify consistency with the earlier comparison.
    expected_eligible = 28176

    if int(out["in_universe"].sum()) != expected_eligible:
        raise ValueError(
            "2025 eligibility differs from the validated comparison"
        )

    temporary = output.with_suffix(".tmp.parquet")

    out.to_parquet(
        temporary, index=False, compression="snappy"
    )

    temporary.replace(output)

    print("\n2025 MONTHLY BUILD COMPLETE")
    print("Saved:", output)
    print("Observations:", len(out))
    print("Eligible observations:", int(out["in_universe"].sum()))
    print("Unique securities:", out["permno"].nunique())
    print("First month:", out["month"].min())
    print("Last month:", out["month"].max())
    print("Missing returns:", out["ret"].isna().sum())
    print(
        "Duplicate stock-months:",
        out.duplicated(["permno", "month"]).sum(),
    )


if __name__ == "__main__":
    main()
