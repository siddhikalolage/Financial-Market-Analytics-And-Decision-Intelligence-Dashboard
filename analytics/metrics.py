"""
Financial Market Analytics & Decision Intelligence

Core financial metrics and time-series analytics.

Design principles:
- No future information is used in feature calculations.
- Financial calculations are deterministic and reproducible.
- Invalid numerical values are converted to JSON-safe values.
- Existing dashboard/API keys are preserved for compatibility.
- Metrics are reusable by Flask APIs, dashboard components,
  decision intelligence, and analytical notebooks.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

TRADING_DAYS_PER_YEAR = 252
VOLUME_SPIKE_THRESHOLD = 1.5
RISK_FREE_RATE = 0.0

MIN_ROLLING_WINDOW = 20


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _safe_float(value, digits: int = 4):
    """
    Convert a value into a finite rounded Python float.

    Returns None for NaN, infinity, None, or non-numeric values.
    """

    if value is None:
        return None

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None

    if not np.isfinite(numeric_value):
        return None

    return round(numeric_value, digits)


def _safe_divide(
    numerator,
    denominator,
):
    """
    Safely divide two numerical values.
    """

    try:
        numerator = float(numerator)
        denominator = float(denominator)
    except (TypeError, ValueError):
        return np.nan

    if (
        not np.isfinite(numerator)
        or not np.isfinite(denominator)
        or denominator == 0
    ):
        return np.nan

    return numerator / denominator


def _validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate minimum requirements for financial analytics.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    required_columns = {
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    }

    missing_columns = required_columns.difference(
        df.columns
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if df.empty:
        raise ValueError(
            "Financial dataset is empty."
        )


def _daily_returns(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Return daily decimal returns.
    """

    return (
        df["Close"]
        .pct_change()
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
    )


# ============================================================
# DATA ENRICHMENT
# ============================================================

def enrich_market_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add reusable financial analytics columns to OHLCV data.

    All calculations use only historical/current observations.
    No future observations are introduced.
    """

    _validate_dataframe(df)

    result = df.copy()

    # Ensure chronological order without mutating caller data.
    if not result["Date"].is_monotonic_increasing:
        result = result.sort_values(
            "Date"
        ).reset_index(drop=True)

    close = result["Close"].astype(float)

    # ========================================================
    # RETURNS
    # ========================================================

    result["Return_1D"] = (
        close.pct_change()
        * 100
    )

    result["Return_5D"] = (
        close.pct_change(
            periods=5
        )
        * 100
    )

    result["Return_20D"] = (
        close.pct_change(
            periods=20
        )
        * 100
    )

    result["Cumulative_Return"] = (
        (
            close
            / close.iloc[0]
        )
        - 1
    ) * 100

    # ========================================================
    # MOVING AVERAGES
    # ========================================================

    result["MA20"] = (
        close
        .rolling(
            window=20,
            min_periods=20,
        )
        .mean()
    )

    result["MA50"] = (
        close
        .rolling(
            window=50,
            min_periods=50,
        )
        .mean()
    )

    result["MA200"] = (
        close
        .rolling(
            window=200,
            min_periods=200,
        )
        .mean()
    )

    # ========================================================
    # TREND / PRICE DISTANCE
    # ========================================================

    result["Price_vs_MA20"] = (
        (
            close
            / result["MA20"]
        )
        - 1
    ) * 100

    result["Price_vs_MA50"] = (
        (
            close
            / result["MA50"]
        )
        - 1
    ) * 100

    result["Price_vs_MA200"] = (
        (
            close
            / result["MA200"]
        )
        - 1
    ) * 100

    # ========================================================
    # VOLATILITY
    # ========================================================

    result["Rolling_Volatility_20D"] = (
        result["Return_1D"]
        .rolling(
            window=20,
            min_periods=20,
        )
        .std()
    )

    result["Annualized_Volatility"] = (
        result["Rolling_Volatility_20D"]
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
    )

    # ========================================================
    # DOWNSIDE VOLATILITY
    # ========================================================

    daily_returns_decimal = (
        close.pct_change()
    )

    negative_returns = (
        daily_returns_decimal
        .where(
            daily_returns_decimal < 0
        )
    )

    result["Downside_Volatility_20D"] = (
        negative_returns
        .rolling(
            window=20,
            min_periods=2,
        )
        .std()
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
        * 100
    )

    # ========================================================
    # VOLUME ANALYTICS
    # ========================================================

    volume = result["Volume"].astype(float)

    result["Average_Volume_20D"] = (
        volume
        .rolling(
            window=20,
            min_periods=20,
        )
        .mean()
    )

    result["Volume_Ratio"] = (
        volume
        / result["Average_Volume_20D"]
    )

    result["Volume_Spike"] = (
        result["Volume_Ratio"]
        >= VOLUME_SPIKE_THRESHOLD
    )

    # ========================================================
    # DRAWDOWN
    # ========================================================

    running_max = (
        close.cummax()
    )

    result["Running_Max"] = running_max

    result["Drawdown"] = (
        (
            close
            - running_max
        )
        / running_max
        * 100
    )

    # ========================================================
    # ROLLING SHARPE
    # ========================================================

    rolling_mean = (
        result["Return_1D"]
        .rolling(
            window=20,
            min_periods=20,
        )
        .mean()
    )

    rolling_std = (
        result["Return_1D"]
        .rolling(
            window=20,
            min_periods=20,
        )
        .std()
    )

    result["Rolling_Sharpe_20D"] = (
        rolling_mean
        / rolling_std
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
    )

    # ========================================================
    # ROLLING SORTINO
    # ========================================================

    rolling_downside_std = (
        result["Return_1D"]
        .where(
            result["Return_1D"] < 0
        )
        .rolling(
            window=20,
            min_periods=2,
        )
        .std()
    )

    result["Rolling_Sortino_20D"] = (
        rolling_mean
        / rolling_downside_std
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
    )

    # ========================================================
    # TREND STRUCTURE
    # ========================================================

    result["Bullish_MA_Count"] = (
        (
            close > result["MA20"]
        ).astype(int)
        + (
            close > result["MA50"]
        ).astype(int)
        + (
            close > result["MA200"]
        ).astype(int)
    )

    result["Bearish_MA_Count"] = (
        (
            close < result["MA20"]
        ).astype(int)
        + (
            close < result["MA50"]
        ).astype(int)
        + (
            close < result["MA200"]
        ).astype(int)
    )

    # ========================================================
    # MOMENTUM CLASSIFICATION
    # ========================================================

    result["Momentum_Score"] = (
        (
            result["Return_5D"]
            > 0
        ).astype(int)
        +
        (
            result["Return_20D"]
            > 0
        ).astype(int)
    ) * 50

    result["Momentum_Label"] = np.select(
        [
            (
                result["Return_5D"] > 0
            )
            & (
                result["Return_20D"] > 0
            ),

            (
                result["Return_5D"] < 0
            )
            & (
                result["Return_20D"] < 0
            ),
        ],
        [
            "Bullish",
            "Bearish",
        ],
        default="Mixed",
    )

    return result


# ============================================================
# RETURN METRICS
# ============================================================

def calculate_ytd_return(
    df: pd.DataFrame,
) -> float:
    """
    Calculate year-to-date return using the first available
    trading observation of the latest calendar year.
    """

    _validate_dataframe(df)

    latest_date = df["Date"].max()

    latest_year = latest_date.year

    current_year_data = df[
        df["Date"].dt.year == latest_year
    ]

    if current_year_data.empty:
        return float("nan")

    starting_price = float(
        current_year_data.iloc[0]["Close"]
    )

    latest_price = float(
        current_year_data.iloc[-1]["Close"]
    )

    if starting_price <= 0:
        return float("nan")

    return (
        (
            latest_price
            / starting_price
            - 1
        )
        * 100
    )


def calculate_cumulative_return(
    df: pd.DataFrame,
) -> float:
    """
    Calculate total return over the available dataset.
    """

    _validate_dataframe(df)

    starting_price = float(
        df.iloc[0]["Close"]
    )

    ending_price = float(
        df.iloc[-1]["Close"]
    )

    if (
        starting_price <= 0
        or ending_price <= 0
    ):
        return float("nan")

    return (
        (
            ending_price
            / starting_price
            - 1
        )
        * 100
    )


def calculate_cagr(
    df: pd.DataFrame,
) -> float:
    """
    Calculate Compound Annual Growth Rate.

    Uses actual calendar duration between observations.
    """

    _validate_dataframe(df)

    if len(df) < 2:
        return float("nan")

    start_price = float(
        df.iloc[0]["Close"]
    )

    end_price = float(
        df.iloc[-1]["Close"]
    )

    if (
        start_price <= 0
        or end_price <= 0
    ):
        return float("nan")

    start_date = pd.Timestamp(
        df.iloc[0]["Date"]
    )

    end_date = pd.Timestamp(
        df.iloc[-1]["Date"]
    )

    years = (
        end_date - start_date
    ).days / 365.25

    if years <= 0:
        return float("nan")

    return (
        (
            (
                end_price
                / start_price
            )
            ** (
                1 / years
            )
        )
        - 1
    ) * 100


# ============================================================
# RISK-ADJUSTED METRICS
# ============================================================

def calculate_sharpe_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = RISK_FREE_RATE,
) -> float:
    """
    Calculate annualized Sharpe ratio.
    """

    returns = _daily_returns(df)

    if len(returns) < 2:
        return float("nan")

    daily_risk_free = (
        (
            1 + risk_free_rate
        )
        ** (
            1
            / TRADING_DAYS_PER_YEAR
        )
        - 1
    )

    excess_returns = (
        returns
        - daily_risk_free
    )

    volatility = (
        excess_returns.std()
    )

    if (
        volatility == 0
        or pd.isna(volatility)
    ):
        return float("nan")

    return float(
        excess_returns.mean()
        / volatility
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
    )


def calculate_sortino_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = RISK_FREE_RATE,
) -> float:
    """
    Calculate annualized Sortino ratio.

    Uses downside observations only when estimating
    downside deviation.
    """

    returns = _daily_returns(df)

    if len(returns) < 2:
        return float("nan")

    daily_risk_free = (
        (
            1 + risk_free_rate
        )
        ** (
            1
            / TRADING_DAYS_PER_YEAR
        )
        - 1
    )

    excess_returns = (
        returns
        - daily_risk_free
    )

    downside = excess_returns[
        excess_returns < 0
    ]

    if len(downside) < 2:
        return float("nan")

    downside_deviation = (
        downside.std()
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
    )

    annualized_excess_return = (
        excess_returns.mean()
        * TRADING_DAYS_PER_YEAR
    )

    if (
        downside_deviation == 0
        or pd.isna(
            downside_deviation
        )
    ):
        return float("nan")

    return float(
        annualized_excess_return
        / downside_deviation
    )


def calculate_max_drawdown(
    df: pd.DataFrame,
) -> float:
    """
    Calculate maximum historical drawdown.
    """

    _validate_dataframe(df)

    close = df["Close"].astype(float)

    running_max = (
        close.cummax()
    )

    drawdown = (
        (
            close
            - running_max
        )
        / running_max
        * 100
    )

    return float(
        drawdown.min()
    )


def calculate_current_drawdown(
    df: pd.DataFrame,
) -> float:
    """
    Calculate current drawdown from the historical peak.
    """

    _validate_dataframe(df)

    close = df["Close"].astype(float)

    running_max = (
        close.cummax()
    )

    return float(
        (
            (
                close.iloc[-1]
                - running_max.iloc[-1]
            )
            / running_max.iloc[-1]
        )
        * 100
    )


def calculate_calmar_ratio(
    df: pd.DataFrame,
) -> float:
    """
    Calculate Calmar Ratio.

    Calmar Ratio = CAGR / absolute Maximum Drawdown.
    """

    cagr = calculate_cagr(df)

    max_drawdown = (
        calculate_max_drawdown(df)
    )

    if (
        pd.isna(cagr)
        or pd.isna(max_drawdown)
        or max_drawdown >= 0
    ):
        return float("nan")

    return float(
        cagr
        / abs(max_drawdown)
    )


# ============================================================
# PERFORMANCE METRICS
# ============================================================

def calculate_win_rate(
    df: pd.DataFrame,
) -> float:
    """
    Percentage of trading sessions with positive returns.
    """

    returns = _daily_returns(df)

    if returns.empty:
        return float("nan")

    return float(
        (
            returns > 0
        ).mean()
        * 100
    )


def calculate_average_gain(
    df: pd.DataFrame,
) -> float:
    """
    Average positive daily return.
    """

    returns = _daily_returns(df)

    gains = returns[
        returns > 0
    ]

    if gains.empty:
        return float("nan")

    return float(
        gains.mean()
        * 100
    )


def calculate_average_loss(
    df: pd.DataFrame,
) -> float:
    """
    Average negative daily return.
    """

    returns = _daily_returns(df)

    losses = returns[
        returns < 0
    ]

    if losses.empty:
        return float("nan")

    return float(
        losses.mean()
        * 100
    )


def calculate_profit_factor(
    df: pd.DataFrame,
) -> float:
    """
    Calculate profit factor.

    Profit Factor =
        Total Positive Returns
        /
        Absolute Total Negative Returns
    """

    returns = _daily_returns(df)

    gains = returns[
        returns > 0
    ].sum()

    losses = returns[
        returns < 0
    ].sum()

    if losses == 0:
        return float("nan")

    return float(
        gains
        / abs(losses)
    )


def calculate_best_day(
    df: pd.DataFrame,
) -> float:
    """
    Calculate best single-day percentage return.
    """

    returns = _daily_returns(df)

    if returns.empty:
        return float("nan")

    return float(
        returns.max()
        * 100
    )


def calculate_worst_day(
    df: pd.DataFrame,
) -> float:
    """
    Calculate worst single-day percentage return.
    """

    returns = _daily_returns(df)

    if returns.empty:
        return float("nan")

    return float(
        returns.min()
        * 100
    )


def calculate_positive_days(
    df: pd.DataFrame,
) -> int:
    """
    Count positive-return sessions.
    """

    returns = _daily_returns(df)

    return int(
        (
            returns > 0
        ).sum()
    )


def calculate_negative_days(
    df: pd.DataFrame,
) -> int:
    """
    Count negative-return sessions.
    """

    returns = _daily_returns(df)

    return int(
        (
            returns < 0
        ).sum()
    )


def calculate_average_daily_return(
    df: pd.DataFrame,
) -> float:
    """
    Calculate mean daily percentage return.
    """

    returns = _daily_returns(df)

    if returns.empty:
        return float("nan")

    return float(
        returns.mean()
        * 100
    )


def calculate_median_daily_return(
    df: pd.DataFrame,
) -> float:
    """
    Calculate median daily percentage return.
    """

    returns = _daily_returns(df)

    if returns.empty:
        return float("nan")

    return float(
        returns.median()
        * 100
    )


# ============================================================
# RISK STATISTICS
# ============================================================

def calculate_return_volatility(
    df: pd.DataFrame,
) -> float:
    """
    Calculate full-period annualized return volatility.
    """

    returns = _daily_returns(df)

    if len(returns) < 2:
        return float("nan")

    return float(
        returns.std()
        * math.sqrt(
            TRADING_DAYS_PER_YEAR
        )
        * 100
    )


def calculate_drawdown_duration(
    df: pd.DataFrame,
) -> int:
    """
    Calculate the current drawdown duration in trading sessions.

    Returns zero when the latest observation is at a new
    historical high.
    """

    _validate_dataframe(df)

    close = df["Close"].astype(float)

    running_max = (
        close.cummax()
    )

    underwater = (
        close < running_max
    )

    duration = 0

    for value in reversed(
        underwater.tolist()
    ):

        if not value:
            break

        duration += 1

    return int(duration)


# ============================================================
# MAIN METRICS ENGINE
# ============================================================

def calculate_metrics(
    df: pd.DataFrame,
) -> dict:
    """
    Calculate the complete financial analytics summary.

    Existing dashboard/API fields are preserved.
    Additional statistical and risk metrics are included.
    """

    _validate_dataframe(df)

    enriched = enrich_market_data(
        df
    )

    latest = enriched.iloc[-1]

    current_price = float(
        latest["Close"]
    )

    previous_close = (
        float(
            enriched.iloc[-2]["Close"]
        )
        if len(enriched) >= 2
        else current_price
    )

    daily_change = (
        current_price
        - previous_close
    )

    daily_change_pct = (
        _safe_divide(
            daily_change,
            previous_close,
        )
        * 100
        if previous_close != 0
        else np.nan
    )

    # ========================================================
    # TREND CLASSIFICATION
    # ========================================================

    bullish_ma_count = (
        int(
            latest["Bullish_MA_Count"]
        )
        if not pd.isna(
            latest["Bullish_MA_Count"]
        )
        else 0
    )

    bearish_ma_count = (
        int(
            latest["Bearish_MA_Count"]
        )
        if not pd.isna(
            latest["Bearish_MA_Count"]
        )
        else 0
    )

    if bullish_ma_count >= 2:
        trend_label = "Bullish"
    elif bearish_ma_count >= 2:
        trend_label = "Bearish"
    else:
        trend_label = "Mixed"


    # ========================================================
    # MOMENTUM CLASSIFICATION
    # ========================================================

    return_5d = latest[
        "Return_5D"
    ]

    return_20d = latest[
        "Return_20D"
    ]

    if (
        not pd.isna(return_5d)
        and not pd.isna(return_20d)
    ):

        if (
            return_5d > 0
            and return_20d > 0
        ):
            momentum_label = "Bullish"

        elif (
            return_5d < 0
            and return_20d < 0
        ):
            momentum_label = "Bearish"

        else:
            momentum_label = "Mixed"

    else:
        momentum_label = "Insufficient Data"


    # ========================================================
    # VOLUME REGIME
    # ========================================================

    volume_ratio = latest[
        "Volume_Ratio"
    ]

    if pd.isna(volume_ratio):
        volume_label = "Insufficient Data"

    elif volume_ratio >= 1.5:
        volume_label = "Volume Spike"

    elif volume_ratio >= 1.0:
        volume_label = "Elevated Volume"

    else:
        volume_label = "Below Average"


    # ========================================================
    # RISK REGIME
    # ========================================================

    annualized_volatility = latest[
        "Annualized_Volatility"
    ]

    current_drawdown = latest[
        "Drawdown"
    ]

    if (
        not pd.isna(
            annualized_volatility
        )
        and annualized_volatility >= 30
    ) or (
        not pd.isna(
            current_drawdown
        )
        and current_drawdown <= -20
    ):
        risk_label = "High"

    elif (
        not pd.isna(
            annualized_volatility
        )
        and annualized_volatility >= 20
    ) or (
        not pd.isna(
            current_drawdown
        )
        and current_drawdown <= -10
    ):
        risk_label = "Moderate"

    else:
        risk_label = "Low"


    # ========================================================
    # FULL-PERIOD STATISTICS
    # ========================================================

    returns = _daily_returns(df)

    return_std = (
        returns.std() * 100
        if len(returns) >= 2
        else np.nan
    )

    max_drawdown = (
        calculate_max_drawdown(df)
    )

    current_drawdown_value = (
        calculate_current_drawdown(df)
    )

    drawdown_duration = (
        calculate_drawdown_duration(df)
    )

    # ========================================================
    # METRICS DICTIONARY
    # ========================================================

    metrics = {

        # ====================================================
        # PRICE
        # ====================================================

        "price": {

            "current": _safe_float(
                current_price
            ),

            "previous_close": _safe_float(
                previous_close
            ),

            "daily_change": _safe_float(
                daily_change
            ),

            "daily_change_pct": _safe_float(
                daily_change_pct
            ),
        },


        # ====================================================
        # PERFORMANCE
        # ====================================================

        "performance": {

            "return_5d": _safe_float(
                latest["Return_5D"]
            ),

            "return_20d": _safe_float(
                latest["Return_20D"]
            ),

            "ytd_return": _safe_float(
                calculate_ytd_return(df)
            ),

            "cumulative_return": _safe_float(
                calculate_cumulative_return(df)
            ),

            "cagr": _safe_float(
                calculate_cagr(df)
            ),

            "win_rate": _safe_float(
                calculate_win_rate(df)
            ),

            "average_gain": _safe_float(
                calculate_average_gain(df)
            ),

            "average_loss": _safe_float(
                calculate_average_loss(df)
            ),

            "profit_factor": _safe_float(
                calculate_profit_factor(df)
            ),

            "average_daily_return": _safe_float(
                calculate_average_daily_return(df)
            ),

            "median_daily_return": _safe_float(
                calculate_median_daily_return(df)
            ),

            "best_day": _safe_float(
                calculate_best_day(df)
            ),

            "worst_day": _safe_float(
                calculate_worst_day(df)
            ),

            "positive_days": (
                calculate_positive_days(df)
            ),

            "negative_days": (
                calculate_negative_days(df)
            ),

            "observations": len(df),
        },


        # ====================================================
        # RISK-ADJUSTED PERFORMANCE
        # ====================================================

        "risk_adjusted": {

            "sharpe_ratio": _safe_float(
                calculate_sharpe_ratio(df)
            ),

            "sortino_ratio": _safe_float(
                calculate_sortino_ratio(df)
            ),

            "calmar_ratio": _safe_float(
                calculate_calmar_ratio(df)
            ),
        },


        # ====================================================
        # TREND
        # ====================================================

        "trend": {

            "ma20": _safe_float(
                latest["MA20"]
            ),

            "ma50": _safe_float(
                latest["MA50"]
            ),

            "ma200": _safe_float(
                latest["MA200"]
            ),

            "price_vs_ma20": _safe_float(
                latest["Price_vs_MA20"]
            ),

            "price_vs_ma50": _safe_float(
                latest["Price_vs_MA50"]
            ),

            "price_vs_ma200": _safe_float(
                latest["Price_vs_MA200"]
            ),

            "price_above_ma20": (
                bool(
                    current_price
                    > latest["MA20"]
                )
                if not pd.isna(
                    latest["MA20"]
                )
                else None
            ),

            "price_above_ma50": (
                bool(
                    current_price
                    > latest["MA50"]
                )
                if not pd.isna(
                    latest["MA50"]
                )
                else None
            ),

            "price_above_ma200": (
                bool(
                    current_price
                    > latest["MA200"]
                )
                if not pd.isna(
                    latest["MA200"]
                )
                else None
            ),

            "bullish_ma_count": (
                bullish_ma_count
            ),

            "bearish_ma_count": (
                bearish_ma_count
            ),

            "label": trend_label,
        },


        # ====================================================
        # MOMENTUM
        # ====================================================

        "momentum": {

            "return_5d": _safe_float(
                return_5d
            ),

            "return_20d": _safe_float(
                return_20d
            ),

            "label": momentum_label,

            "score": _safe_float(
                latest["Momentum_Score"]
            ),
        },


        # ====================================================
        # RISK
        # ====================================================

        "risk": {

            "rolling_volatility_20d": _safe_float(
                latest[
                    "Rolling_Volatility_20D"
                ]
            ),

            "annualized_volatility": _safe_float(
                latest[
                    "Annualized_Volatility"
                ]
            ),

            "downside_volatility": _safe_float(
                latest[
                    "Downside_Volatility_20D"
                ]
            ),

            "full_period_volatility": _safe_float(
                calculate_return_volatility(df)
            ),

            "return_standard_deviation": _safe_float(
                return_std
            ),

            "maximum_drawdown": _safe_float(
                max_drawdown
            ),

            "current_drawdown": _safe_float(
                current_drawdown_value
            ),

            "drawdown_duration": (
                drawdown_duration
            ),

            "label": risk_label,
        },


        # ====================================================
        # VOLUME
        # ====================================================

        "volume": {

            "current": _safe_float(
                latest["Volume"]
            ),

            "average_20d": _safe_float(
                latest[
                    "Average_Volume_20D"
                ]
            ),

            "ratio": _safe_float(
                latest["Volume_Ratio"]
            ),

            "spike": (
                bool(
                    latest["Volume_Spike"]
                )
                if not pd.isna(
                    latest["Volume_Spike"]
                )
                else None
            ),

            "label": volume_label,
        },


        # ====================================================
        # DATASET INFORMATION
        # ====================================================

        "dataset": {

            "rows": len(df),

            "columns": len(df.columns),

            "start_date": (
                pd.Timestamp(
                    df["Date"].min()
                ).strftime(
                    "%Y-%m-%d"
                )
            ),

            "end_date": (
                pd.Timestamp(
                    df["Date"].max()
                ).strftime(
                    "%Y-%m-%d"
                )
            ),

            "trading_days": len(df),
        },
    }

    return metrics


# ============================================================
# DASHBOARD CHART DATA
# ============================================================

def prepare_chart_data(
    df: pd.DataFrame,
    periods: int = 120,
) -> dict:
    """
    Prepare analytical time-series data for dashboard
    visualization.

    Existing chart keys are preserved.
    Additional analytics are exposed for future charts.
    """

    _validate_dataframe(df)

    if periods <= 0:
        raise ValueError(
            "periods must be greater than zero."
        )

    enriched = (
        enrich_market_data(df)
        .tail(periods)
        .copy()
    )

    def clean_value(value):

        return _safe_float(
            value
        )

    return {

        "dates": (
            enriched["Date"]
            .dt
            .strftime("%Y-%m-%d")
            .tolist()
        ),

        "open": (
            enriched["Open"]
            .round(4)
            .tolist()
        ),

        "high": (
            enriched["High"]
            .round(4)
            .tolist()
        ),

        "low": (
            enriched["Low"]
            .round(4)
            .tolist()
        ),

        "close": (
            enriched["Close"]
            .round(4)
            .tolist()
        ),

        "volume": (
            enriched["Volume"]
            .tolist()
        ),

        "return_1d": [
            clean_value(x)
            for x in enriched[
                "Return_1D"
            ]
        ],

        "return_5d": [
            clean_value(x)
            for x in enriched[
                "Return_5D"
            ]
        ],

        "return_20d": [
            clean_value(x)
            for x in enriched[
                "Return_20D"
            ]
        ],

        "cumulative_return": [
            clean_value(x)
            for x in enriched[
                "Cumulative_Return"
            ]
        ],

        "ma20": [
            clean_value(x)
            for x in enriched[
                "MA20"
            ]
        ],

        "ma50": [
            clean_value(x)
            for x in enriched[
                "MA50"
            ]
        ],

        "ma200": [
            clean_value(x)
            for x in enriched[
                "MA200"
            ]
        ],

        "volatility": [
            clean_value(x)
            for x in enriched[
                "Annualized_Volatility"
            ]
        ],

        "downside_volatility": [
            clean_value(x)
            for x in enriched[
                "Downside_Volatility_20D"
            ]
        ],

        "sharpe": [
            clean_value(x)
            for x in enriched[
                "Rolling_Sharpe_20D"
            ]
        ],

        "sortino": [
            clean_value(x)
            for x in enriched[
                "Rolling_Sortino_20D"
            ]
        ],

        "drawdown": [
            clean_value(x)
            for x in enriched[
                "Drawdown"
            ]
        ],

        "volume_ratio": [
            clean_value(x)
            for x in enriched[
                "Volume_Ratio"
            ]
        ],

        "momentum_score": [
            clean_value(x)
            for x in enriched[
                "Momentum_Score"
            ]
        ],

        "bullish_ma_count": [
            clean_value(x)
            for x in enriched[
                "Bullish_MA_Count"
            ]
        ],

        "bearish_ma_count": [
            clean_value(x)
            for x in enriched[
                "Bearish_MA_Count"
            ]
        ],
    }
