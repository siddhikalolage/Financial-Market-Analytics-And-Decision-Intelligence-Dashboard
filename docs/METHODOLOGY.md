# Methodology

## Objective

The project analyzes historical OHLCV market data and converts it into financial performance metrics, risk indicators, machine-learning predictions, and explainable decision intelligence.

## Analytical Workflow

1. Load historical OHLCV data.
2. Validate dates, numerical fields, ordering, and duplicates.
3. Calculate return, trend, volatility, drawdown, and volume features.
4. Generate time-series features using historical observations.
5. Train and evaluate a neural-network regression model for next-trading-day closing price.
6. Compare model performance against a persistence baseline.
7. Calculate model reliability.
8. Combine market evidence, risk, momentum, trend, volume, and ML reliability.
9. Expose results through Flask APIs and the dashboard.

## Time-Series Design

Chronological ordering is preserved throughout the analytical and machine-learning workflow.

Random shuffling is avoided because future observations must not influence historical training observations.

Rolling indicators such as moving averages and volatility are calculated from historical windows.

## Decision Intelligence

The decision engine combines:

- Price movement
- Momentum
- Moving-average trend
- Volume behaviour
- Risk conditions
- ML prediction
- Model reliability

The ML prediction is not treated as an independent source of truth. When the model performs worse than the persistence baseline, its influence is reduced or removed.

## Reproducibility

The project uses:

- Static historical dataset
- Explicit feature engineering
- Saved model artifacts
- Dependency specification
- Automated tests
- Deterministic analytical calculations
- Chronological train/test methodology

## Limitations

The system is designed for educational and analytical purposes. It does not represent a production trading system and does not provide financial advice.
