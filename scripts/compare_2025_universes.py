
"""Compare conservative and broad CIZ investment universes for 2025."""

import pandas as pd

from lrrep.config import data_dir


def main():
    folder = data_dir()

    historical = pd.read_parquet(
        folder / "crsp_monthly.parquet",
        columns=["permno", "month", "shrcd", "exchcd"],
    )

    raw = pd.read_parquet(
        folder / "crsp_ciz_2025_raw.parquet",
        columns=[
            "permno",
            "mthcaldt",
            "mthcap",
            "securitytype",
            "securitysubtype",
            "sharetype",
            "primaryexch",
        ],
    )

    # December 2024 historical classifications.
    last = historical.loc[
        historical["month"].eq(pd.Timestamp("2024-12-31")),
        ["permno", "shrcd", "exchcd"],
    ].drop_duplicates("permno")

    df = raw.merge(
        last, on="permno", how="left", validate="many_to_one"
    )

    df["month"] = (
        pd.to_datetime(df["mthcaldt"])
        + pd.offsets.MonthEnd(0)
    )

    df["me"] = pd.to_numeric(
        df["mthcap"], errors="coerce"
    ) / 1000.0

    # Current 2025 CIZ classifications.
    common_ciz = (
        df["securitytype"].eq("EQTY")
        & df["securitysubtype"].eq("COM")
        & df["sharetype"].eq("NS")
    )

    valid_exchange = df["primaryexch"].isin(["N", "A", "Q"])

    # Broad CIZ universe before the size filter.
    df["broad_candidate"] = common_ciz & valid_exchange

    # Conservative universe: also requires valid legacy
    # common-stock classification in December 2024.
    legacy_common = df["shrcd"].isin([10, 11])

    df["conservative_candidate"] = (
        df["broad_candidate"] & legacy_common
    )

    # Apply the NYSE 20th percentile separately for
    # each universe definition.
    for name in ["broad", "conservative"]:
        candidate = df[f"{name}_candidate"]

        nyse = (
            candidate
            & df["primaryexch"].eq("N")
            & df["me"].gt(0)
        )

        threshold = (
            df.loc[nyse]
            .groupby("month")["me"]
            .quantile(0.20)
        )

        df[f"{name}_p20"] = df["month"].map(threshold)

        df[f"{name}_eligible"] = (
            candidate
            & df["me"].notna()
            & df["me"].gt(0)
            & df["me"].ge(df[f"{name}_p20"])
        )

    # Monthly comparison.
    summary = (
        df.groupby("month")
        .agg(
            conservative_stocks=(
                "conservative_eligible", "sum"
            ),
            broad_stocks=("broad_eligible", "sum"),
        )
        .reset_index()
    )

    summary["difference"] = (
        summary["broad_stocks"]
        - summary["conservative_stocks"]
    )

    print("\n2025 INVESTMENT UNIVERSE COMPARISON")
    print(summary.to_string(index=False))

    print("\nANNUAL SUMMARY")
    print(
        "Average conservative stocks:",
        round(summary["conservative_stocks"].mean(), 1),
    )
    print(
        "Average broad CIZ stocks:",
        round(summary["broad_stocks"].mean(), 1),
    )
    print(
        "Average difference:",
        round(summary["difference"].mean(), 1),
    )

    print("\nCLASSIFICATION COVERAGE")
    print(
        "Conservative eligible stock-months:",
        int(df["conservative_eligible"].sum()),
    )
    print(
        "Broad eligible stock-months:",
        int(df["broad_eligible"].sum()),
    )

    # Save comparison, not the final contract dataset.
    output = folder / "universe_comparison_2025.parquet"

    if output.exists():
        raise FileExistsError(
            f"{output} already exists; refusing to overwrite"
        )

    df.to_parquet(
        output, index=False, compression="snappy"
    )

    print("\nSaved:", output)


if __name__ == "__main__":
    main()
