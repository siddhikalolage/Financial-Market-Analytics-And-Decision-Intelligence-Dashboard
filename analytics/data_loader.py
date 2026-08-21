from pathlib import Path
from typing import Final

import pandas as pd


REQUIRED_COLUMNS: Final = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


NUMERIC_COLUMNS: Final = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


class DataValidationError(ValueError):
    """Raised when the financial dataset fails validation."""


def load_stock_data(
    file_path: str | Path = "data/stock_data.csv"
) -> pd.DataFrame:
    """
    Load and validate OHLCV stock market data.

    The function performs structural, datatype, missing-value,
    OHLC relationship, price, volume, chronological ordering,
    and duplicate-date validation.

    Parameters
    ----------
    file_path:
        Path to the CSV dataset.

    Returns
    -------
    pd.DataFrame
        Clean, chronologically sorted stock data.

    Raises
    ------
    FileNotFoundError
        If the dataset does not exist.

    DataValidationError
        If the dataset fails validation.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Stock dataset not found: {path}"
        )

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise DataValidationError(
            f"Unable to read stock dataset: {exc}"
        ) from exc

    validate_required_columns(df)

    # ---------------------------------------------------------
    # DATE VALIDATION
    # ---------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    if df["Date"].isna().any():

        invalid_count = int(
            df["Date"].isna().sum()
        )

        raise DataValidationError(
            f"Dataset contains {invalid_count} "
            f"invalid date value(s)."
        )

    # ---------------------------------------------------------
    # NUMERIC VALIDATION
    # ---------------------------------------------------------

    for column in NUMERIC_COLUMNS:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # MISSING VALUE VALIDATION
    # ---------------------------------------------------------

    validate_missing_values(df)

    # ---------------------------------------------------------
    # OHLCV VALIDATION
    # ---------------------------------------------------------

    validate_ohlc_data(df)

    # ---------------------------------------------------------
    # CHRONOLOGICAL ORDER
    # ---------------------------------------------------------

    df = (
        df
        .sort_values("Date")
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # DUPLICATE TRADING DATES
    # ---------------------------------------------------------

    duplicate_dates = df["Date"].duplicated(
        keep="last"
    )

    if duplicate_dates.any():

        df = (
            df.loc[~duplicate_dates]
            .reset_index(drop=True)
        )

    # ---------------------------------------------------------
    # FINAL EMPTY DATASET CHECK
    # ---------------------------------------------------------

    if df.empty:

        raise DataValidationError(
            "Dataset is empty after validation."
        )

    return df


def validate_required_columns(
    df: pd.DataFrame
) -> None:
    """Validate that all required OHLCV columns exist."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise DataValidationError(
            "Missing required column(s): "
            + ", ".join(missing_columns)
        )


def validate_missing_values(
    df: pd.DataFrame
) -> None:
    """Validate that required columns contain no missing values."""

    missing = (
        df[REQUIRED_COLUMNS]
        .isna()
        .sum()
    )

    missing = missing[missing > 0]

    if not missing.empty:

        details = ", ".join(
            f"{column}: {count}"
            for column, count in missing.items()
        )

        raise DataValidationError(
            f"Dataset contains missing values: {details}"
        )


def validate_ohlc_data(
    df: pd.DataFrame
) -> None:
    """
    Validate financial OHLC and volume relationships.
    """

    invalid_ohlc = (
        (df["High"] < df["Open"])
        | (df["High"] < df["Close"])
        | (df["Low"] > df["Open"])
        | (df["Low"] > df["Close"])
        | (df["High"] < df["Low"])
    )

    if invalid_ohlc.any():

        count = int(
            invalid_ohlc.sum()
        )

        raise DataValidationError(
            f"Found {count} row(s) "
            f"with invalid OHLC relationships."
        )

    if (df["Volume"] < 0).any():

        count = int(
            (df["Volume"] < 0).sum()
        )

        raise DataValidationError(
            f"Found {count} row(s) "
            f"with negative volume values."
        )

    if (df["Close"] <= 0).any():

        count = int(
            (df["Close"] <= 0).sum()
        )

        raise DataValidationError(
            f"Found {count} row(s) "
            f"with non-positive closing prices."
        )


def generate_data_quality_report(
    df: pd.DataFrame
) -> dict:
    """
    Generate a reusable data-quality report.

    This function does not modify the input DataFrame.

    Returns
    -------
    dict
        Structured data-quality information suitable for
        dashboards, reports, logging, and testing.
    """

    report = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": 0,
        "missing_by_column": {},
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "duplicate_dates": int(
            df["Date"].duplicated().sum()
        )
        if "Date" in df.columns
        else 0,
        "invalid_dates": 0,
        "invalid_ohlc_rows": 0,
        "negative_volume_rows": 0,
        "non_positive_close_rows": 0,
        "date_range": {
            "start": None,
            "end": None,
        },
        "status": "PASS",
    }

    # ---------------------------------------------------------
    # MISSING VALUES
    # ---------------------------------------------------------

    missing = df.isna().sum()

    missing = missing[missing > 0]

    report["missing_values"] = int(
        missing.sum()
    )

    report["missing_by_column"] = {
        str(column): int(count)
        for column, count in missing.items()
    }

    # ---------------------------------------------------------
    # DATE QUALITY
    # ---------------------------------------------------------

    if "Date" in df.columns:

        parsed_dates = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        report["invalid_dates"] = int(
            parsed_dates.isna().sum()
        )

        valid_dates = parsed_dates.dropna()

        if not valid_dates.empty:

            report["date_range"] = {
                "start": valid_dates.min().strftime(
                    "%Y-%m-%d"
                ),
                "end": valid_dates.max().strftime(
                    "%Y-%m-%d"
                ),
            }

    # ---------------------------------------------------------
    # OHLC QUALITY
    # ---------------------------------------------------------

    required_for_ohlc = set(
        [
            "Open",
            "High",
            "Low",
            "Close",
        ]
    )

    if required_for_ohlc.issubset(
        df.columns
    ):

        invalid_ohlc = (
            (df["High"] < df["Open"])
            | (df["High"] < df["Close"])
            | (df["Low"] > df["Open"])
            | (df["Low"] > df["Close"])
            | (df["High"] < df["Low"])
        )

        report["invalid_ohlc_rows"] = int(
            invalid_ohlc.sum()
        )

    # ---------------------------------------------------------
    # VOLUME QUALITY
    # ---------------------------------------------------------

    if "Volume" in df.columns:

        report["negative_volume_rows"] = int(
            (df["Volume"] < 0).sum()
        )

    # ---------------------------------------------------------
    # PRICE QUALITY
    # ---------------------------------------------------------

    if "Close" in df.columns:

        report["non_positive_close_rows"] = int(
            (df["Close"] <= 0).sum()
        )

    # ---------------------------------------------------------
    # OVERALL QUALITY STATUS
    # ---------------------------------------------------------

    quality_failures = [
        report["missing_values"] > 0,
        report["invalid_dates"] > 0,
        report["invalid_ohlc_rows"] > 0,
        report["negative_volume_rows"] > 0,
        report["non_positive_close_rows"] > 0,
    ]

    if any(quality_failures):

        report["status"] = "FAIL"

    elif report["duplicate_rows"] > 0:

        report["status"] = "WARNING"

    elif report["duplicate_dates"] > 0:

        report["status"] = "WARNING"

    return report