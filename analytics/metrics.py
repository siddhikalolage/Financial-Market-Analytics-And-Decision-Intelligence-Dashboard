import math

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252
VOLUME_SPIKE_THRESHOLD = 1.5
RISK_FREE_RATE = 0.0


def enrich_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add reusable financial analytics columns to OHLCV data.

    All calculations use only historical/current observations,
    preventing future information from entering the feature calculations.
    """

    result = df.copy()

    # =========================================================
    # RETURNS
    # =========================================================

    result["Return_1D"] = (
        result["Close"].pct_change() * 100
    )

    result["Return_5D"] = (
        result["Close"].pct_change(periods=5) * 100
    )

    result["Return_20D"] = (
        result["Close"].pct_change(periods=20) * 100
    )

    # Cumulative return from the first available observation.
    result["Cumulative_Return"] = (
        result["Close"] / result["Close"].iloc[0] - 1
    ) * 100

    # =========================================================
    # MOVING AVERAGES
    # =========================================================

    result["MA20"] = (
        result["Close"].rolling(window=20).mean()
    )

    result["MA50"] = (
        result["Close"].rolling(window=50).mean()
    )

    result["MA200"] = (
        result["Close"].rolling(window=200).mean()
    )

    # =========================================================
    # TREND / PRICE DISTANCE
    # =========================================================

    result["Price_vs_MA20"] = (
        (result["Close"] / result["MA20"]) - 1
    ) * 100

    result["Price_vs_MA50"] = (
        (result["Close"] / result["MA50"]) - 1
    ) * 100

    result["Price_vs_MA200"] = (
        (result["Close"] / result["MA200"]) - 1
    ) * 100

    # =========================================================
    # VOLATILITY
    # =========================================================

    result["Rolling_Volatility_20D"] = (
        result["Return_1D"]
        .rolling(window=20)
        .std()
    )

    result["Annualized_Volatility"] = (
        result["Return_1D"]
        .rolling(window=20)
        .std()
        * math.sqrt(TRADING_DAYS_PER_YEAR)
    )

    # =========================================================
    # DOWNSIDE VOLATILITY
    # =========================================================

    daily_returns_decimal = (
        result["Close"].pct_change()
    )

    downside_returns = daily_returns_decimal.where(
        daily_returns_decimal < 0
    )

    result["Downside_Volatility_20D"] = (
        downside_returns
        .rolling(window=20)
        .std()
        * math.sqrt(TRADING_DAYS_PER_YEAR)
        * 100
    )

    # =========================================================
    # VOLUME ANALYTICS
    # =========================================================

    result["Average_Volume_20D"] = (
        result["Volume"]
        .rolling(window=20)
        .mean()
    )

    result["Volume_Ratio"] = (
        result["Volume"]
        / result["Average_Volume_20D"]
    )

    result["Volume_Spike"] = (
        result["Volume_Ratio"]
        >= VOLUME_SPIKE_THRESHOLD
    )

    # =========================================================
    # DRAWDOWN
    # =========================================================

    running_max = (
        result["Close"]
        .cummax()
    )

    result["Running_Max"] = running_max

    result["Drawdown"] = (
        (result["Close"] - running_max)
        / running_max
        * 100
    )

    # =========================================================
    # ROLLING SHARPE
    # =========================================================

    result["Rolling_Sharpe_20D"] = (
        result["Return_1D"]
        .rolling(window=20)
        .mean()
        / result["Return_1D"]
        .rolling(window=20)
        .std()
        * math.sqrt(TRADING_DAYS_PER_YEAR)
    )

    # =========================================================
    # ROLLING SORTINO
    # =========================================================

    rolling_mean_return = (
        result["Return_1D"]
        .rolling(window=20)
        .mean()
    )

    rolling_downside = (
        result["Return_1D"]
        .where(result["Return_1D"] < 0)
        .rolling(window=20)
        .std()
    )

    result["Rolling_Sortino_20D"] = (
        rolling_mean_return
        / rolling_downside
        * math.sqrt(TRADING_DAYS_PER_YEAR)
    )

    return result


def calculate_ytd_return(
    df: pd.DataFrame
) -> float:
    """
    Calculate year-to-date return using the first available
    trading observation of the latest calendar year.
    """

    latest_date = df["Date"].max()
    latest_year = latest_date.year

    current_year_data = df[
        df["Date"].dt.year == latest_year
    ]

    if current_year_data.empty:
        return float("nan")

    starting_price = (
        current_year_data.iloc[0]["Close"]
    )

    latest_price = (
        current_year_data.iloc[-1]["Close"]
    )

    if starting_price == 0:
        return float("nan")

    return float(
        (latest_price / starting_price - 1)
        * 100
    )


def calculate_cumulative_return(
    df: pd.DataFrame
) -> float:
    """Calculate total return over the available dataset."""

    if df.empty:
        return float("nan")

    starting_price = float(
        df.iloc[0]["Close"]
    )

    ending_price = float(
        df.iloc[-1]["Close"]
    )

    if starting_price <= 0:
        return float("nan")

    return float(
        (ending_price / starting_price - 1)
        * 100
    )


def calculate_sharpe_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    """
    Calculate annualized Sharpe ratio.

    Parameters
    ----------
    df:
        OHLCV dataframe.

    risk_free_rate:
        Annual risk-free rate expressed as a decimal.
        Default is 0.0 for simplified market analysis.
    """

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    if len(returns) < 2:
        return float("nan")

    daily_risk_free = (
        (1 + risk_free_rate)
        ** (1 / TRADING_DAYS_PER_YEAR)
        - 1
    )

    excess_returns = (
        returns - daily_risk_free
    )

    volatility = excess_returns.std()

    if volatility == 0 or pd.isna(volatility):
        return float("nan")

    return float(
        excess_returns.mean()
        / volatility
        * math.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_sortino_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    """
    Calculate annualized Sortino ratio.

    Unlike Sharpe ratio, Sortino focuses on downside volatility.
    """

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    if len(returns) < 2:
        return float("nan")

    daily_risk_free = (
        (1 + risk_free_rate)
        ** (1 / TRADING_DAYS_PER_YEAR)
        - 1
    )

    excess_returns = (
        returns - daily_risk_free
    )

    downside = excess_returns[
        excess_returns < 0
    ]

    if len(downside) < 2:
        return float("nan")

    downside_deviation = (
        downside.std()
        * math.sqrt(TRADING_DAYS_PER_YEAR)
    )

    annualized_excess_return = (
        excess_returns.mean()
        * TRADING_DAYS_PER_YEAR
    )

    if (
        downside_deviation == 0
        or pd.isna(downside_deviation)
    ):
        return float("nan")

    return float(
        annualized_excess_return
        / downside_deviation
    )


def calculate_win_rate(
    df: pd.DataFrame
) -> float:
    """
    Calculate percentage of trading sessions
    with positive returns.
    """

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    if returns.empty:
        return float("nan")

    return float(
        (returns > 0).mean() * 100
    )


def calculate_average_gain(
    df: pd.DataFrame
) -> float:
    """Calculate average positive daily return."""

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    gains = returns[
        returns > 0
    ]

    if gains.empty:
        return float("nan")

    return float(
        gains.mean() * 100
    )


def calculate_average_loss(
    df: pd.DataFrame
) -> float:
    """Calculate average negative daily return."""

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    losses = returns[
        returns < 0
    ]

    if losses.empty:
        return float("nan")

    return float(
        losses.mean() * 100
    )


def calculate_profit_factor(
    df: pd.DataFrame
) -> float:
    """
    Calculate profit factor.

    Profit Factor =
        Total Positive Returns
        /
        Absolute Total Negative Returns
    """

    returns = (
        df["Close"]
        .pct_change()
        .dropna()
    )

    gains = returns[
        returns > 0
    ].sum()

    losses = returns[
        returns < 0
    ].sum()

    if losses == 0:
        return float("nan")

    return float(
        gains / abs(losses)
    )


def calculate_max_drawdown(
    df: pd.DataFrame
) -> float:
    """Calculate maximum historical drawdown as a percentage."""

    running_max = (
        df["Close"]
        .cummax()
    )

    drawdown = (
        (df["Close"] - running_max)
        / running_max
        * 100
    )

    return float(
        drawdown.min()
    )


def calculate_metrics(
    df: pd.DataFrame
) -> dict:
    """
    Calculate the complete financial analytics summary
    used by the dashboard.
    """

    enriched = enrich_market_data(df)

    latest = enriched.iloc[-1]

    current_price = float(
        latest["Close"]
    )

    previous_close = (
        float(enriched.iloc[-2]["Close"])
        if len(enriched) >= 2
        else current_price
    )

    daily_change = (
        current_price
        - previous_close
    )

    daily_change_pct = (
        daily_change
        / previous_close
        * 100
        if previous_close != 0
        else float("nan")
    )

    def safe_float(value):
        """
        Convert numeric values into JSON-safe floats.
        """

        if pd.isna(value):
            return None

        return round(
            float(value),
            4
        )

    metrics = {

        # =====================================================
        # PRICE
        # =====================================================

        "price": {

            "current": safe_float(
                current_price
            ),

            "previous_close": safe_float(
                previous_close
            ),

            "daily_change": safe_float(
                daily_change
            ),

            "daily_change_pct": safe_float(
                daily_change_pct
            ),
        },

        # =====================================================
        # PERFORMANCE
        # =====================================================

        "performance": {

            "return_5d": safe_float(
                latest["Return_5D"]
            ),

            "return_20d": safe_float(
                latest["Return_20D"]
            ),

            "ytd_return": safe_float(
                calculate_ytd_return(df)
            ),

            "cumulative_return": safe_float(
                calculate_cumulative_return(df)
            ),

            "win_rate": safe_float(
                calculate_win_rate(df)
            ),

            "average_gain": safe_float(
                calculate_average_gain(df)
            ),

            "average_loss": safe_float(
                calculate_average_loss(df)
            ),

            "profit_factor": safe_float(
                calculate_profit_factor(df)
            ),
        },

        # =====================================================
        # RISK-ADJUSTED PERFORMANCE
        # =====================================================

        "risk_adjusted": {

            "sharpe_ratio": safe_float(
                calculate_sharpe_ratio(df)
            ),

            "sortino_ratio": safe_float(
                calculate_sortino_ratio(df)
            ),
        },

        # =====================================================
        # TREND
        # =====================================================

        "trend": {

            "ma20": safe_float(
                latest["MA20"]
            ),

            "ma50": safe_float(
                latest["MA50"]
            ),

            "ma200": safe_float(
                latest["MA200"]
            ),

            "price_vs_ma20": safe_float(
                latest["Price_vs_MA20"]
            ),

            "price_vs_ma50": safe_float(
                latest["Price_vs_MA50"]
            ),

            "price_vs_ma200": safe_float(
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
        },

        # =====================================================
        # RISK
        # =====================================================

        "risk": {

            "rolling_volatility_20d": safe_float(
                latest["Rolling_Volatility_20D"]
            ),

            "annualized_volatility": safe_float(
                latest["Annualized_Volatility"]
            ),

            "downside_volatility": safe_float(
                latest["Downside_Volatility_20D"]
            ),

            "maximum_drawdown": safe_float(
                calculate_max_drawdown(df)
            ),

            "current_drawdown": safe_float(
                latest["Drawdown"]
            ),
        },

        # =====================================================
        # VOLUME
        # =====================================================

        "volume": {

            "current": safe_float(
                latest["Volume"]
            ),

            "average_20d": safe_float(
                latest["Average_Volume_20D"]
            ),

            "ratio": safe_float(
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
        },
    }

    return metrics


def prepare_chart_data(
    df: pd.DataFrame,
    periods: int = 120
) -> dict:
    """
    Prepare analytical time-series data for the dashboard.
    """

    enriched = (
        enrich_market_data(df)
        .tail(periods)
        .copy()
    )

    def clean_value(value):

        if pd.isna(value):
            return None

        return round(
            float(value),
            4
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
            for x in enriched["Return_1D"]
        ],

        "return_5d": [
            clean_value(x)
            for x in enriched["Return_5D"]
        ],

        "return_20d": [
            clean_value(x)
            for x in enriched["Return_20D"]
        ],

        "cumulative_return": [
            clean_value(x)
            for x in enriched["Cumulative_Return"]
        ],

        "ma20": [
            clean_value(x)
            for x in enriched["MA20"]
        ],

        "ma50": [
            clean_value(x)
            for x in enriched["MA50"]
        ],

        "ma200": [
            clean_value(x)
            for x in enriched["MA200"]
        ],

        "volatility": [
            clean_value(x)
            for x in enriched["Annualized_Volatility"]
        ],

        "downside_volatility": [
            clean_value(x)
            for x in enriched["Downside_Volatility_20D"]
        ],

        "sharpe": [
            clean_value(x)
            for x in enriched["Rolling_Sharpe_20D"]
        ],

        "sortino": [
            clean_value(x)
            for x in enriched["Rolling_Sortino_20D"]
        ],

        "drawdown": [
            clean_value(x)
            for x in enriched["Drawdown"]
        ],

        "volume_ratio": [
            clean_value(x)
            for x in enriched["Volume_Ratio"]
        ],
    }