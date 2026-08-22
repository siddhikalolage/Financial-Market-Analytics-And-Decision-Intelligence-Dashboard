import numpy as np
import pandas as pd

from analytics.metrics import (
    enrich_market_data,
    calculate_metrics,
    calculate_ytd_return,
    calculate_cumulative_return,
    calculate_cagr,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_calmar_ratio,
    calculate_win_rate,
    calculate_profit_factor,
)


def sample_data(rows=260):
    dates = pd.date_range("2023-01-02", periods=rows, freq="B")
    close = np.linspace(100, 150, rows)

    return pd.DataFrame({
        "Date": dates,
        "Open": close - 1,
        "High": close + 2,
        "Low": close - 2,
        "Close": close,
        "Volume": np.full(rows, 100000),
    })


def test_enrich_market_data_creates_expected_columns():
    df = sample_data()
    result = enrich_market_data(df)

    expected = {
        "Return_1D",
        "Return_5D",
        "Return_20D",
        "MA20",
        "MA50",
        "MA200",
        "Price_vs_MA20",
        "Price_vs_MA50",
        "Price_vs_MA200",
        "Rolling_Volatility_20D",
        "Annualized_Volatility",
        "Downside_Volatility_20D",
        "Average_Volume_20D",
        "Volume_Ratio",
        "Volume_Spike",
        "Running_Max",
        "Drawdown",
        "Rolling_Sharpe_20D",
        "Rolling_Sortino_20D",
    }

    assert expected.issubset(result.columns)
    assert len(result) == len(df)


def test_metrics_contains_required_sections():
    metrics = calculate_metrics(sample_data())

    required_sections = {
        "price",
        "performance",
        "risk_adjusted",
        "trend",
        "momentum",
        "risk",
        "volume",
        "dataset",
    }

    assert required_sections.issubset(metrics.keys())


def test_metrics_contains_no_nan_or_infinite_values_in_serializable_output():
    metrics = calculate_metrics(sample_data())

    def check(value):
        if isinstance(value, dict):
            for item in value.values():
                check(item)
        elif isinstance(value, (float, int)):
            assert np.isfinite(value)

    check(metrics)


def test_ytd_return_is_numeric():
    result = calculate_ytd_return(sample_data())
    assert isinstance(result, float)
    assert np.isfinite(result)


def test_cumulative_return_is_numeric():
    result = calculate_cumulative_return(sample_data())
    assert isinstance(result, float)
    assert np.isfinite(result)


def test_cagr_is_numeric():
    result = calculate_cagr(sample_data())
    assert isinstance(result, float)
    assert np.isfinite(result)


def test_sharpe_ratio_is_numeric_or_nan():
    result = calculate_sharpe_ratio(sample_data())
    assert isinstance(result, float)


def test_sortino_ratio_is_numeric_or_nan():
    result = calculate_sortino_ratio(sample_data())
    assert isinstance(result, float)


def test_max_drawdown_is_non_positive():
    result = calculate_max_drawdown(sample_data())
    assert result <= 0


def test_calmar_ratio_is_numeric_or_nan():
    result = calculate_calmar_ratio(sample_data())
    assert isinstance(result, float)


def test_win_rate_is_between_zero_and_hundred():
    result = calculate_win_rate(sample_data())
    assert 0 <= result <= 100


def test_profit_factor_is_non_negative_or_nan():
    result = calculate_profit_factor(sample_data())

    if not np.isnan(result):
        assert result >= 0


def test_metrics_preserves_input_dataframe():
    df = sample_data()
    original_columns = list(df.columns)
    original_length = len(df)

    calculate_metrics(df)

    assert list(df.columns) == original_columns
    assert len(df) == original_length
