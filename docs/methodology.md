# Analytics Methodology

## Purpose

This document is the concise methodology reference for the **Financial Market Analytics & Decision Intelligence Dashboard**. The project is positioned as a historical analytics and BI decision-support solution: it transforms validated OHLCV data into transparent KPIs, trend context, market-participation indicators, risk measures, and rule-based analyst observations.

For the full end-to-end methodology, see [`docs/analytics_methodology.md`](analytics_methodology.md). For KPI definitions, see [`docs/kpi_dictionary.md`](kpi_dictionary.md).

## Data foundation

The analytical dataset contains:

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

The Python data layer validates required fields, converts data types, removes invalid/duplicate dates, sorts chronologically, and checks OHLC logical consistency before calculating analytics.

Calculations are based only on observations available at or before each timestamp. Rolling features therefore do not intentionally use future observations.

## Performance analytics

- **Daily return:** percentage change in closing price versus the previous observation.
- **5D return:** closing-price change over five observations.
- **20D return:** closing-price change over twenty observations.
- **Cumulative return:** change from the first available close to the latest close.
- **YTD return:** latest close compared with the first available observation in the latest calendar year.
- **CAGR:** annualized price growth using the actual calendar duration between the first and latest observations.

## Trend analytics

20-day, 50-day, and 200-day simple moving averages are calculated from historical closing prices. The dashboard uses the 20-day and 50-day averages for visible trend context and retains the 200-day average in the analytical dataset for extended analysis.

The latest close's distance from the 20-day moving average is used as a descriptive short-term trend observation; it is not treated as a predictive signal.

## Volatility and downside risk

- **Rolling 20D volatility:** standard deviation of daily returns over the latest 20 observations, annualized with `sqrt(252)`.
- **Annualized volatility:** standard deviation of all available daily returns, annualized with `sqrt(252)`.
- **Downside volatility:** standard deviation of negative daily returns, annualized.
- **Drawdown:** percentage distance of the current close from its historical running maximum.
- **Maximum drawdown:** most negative observed drawdown over the available history.
- **Current drawdown:** latest observed distance from the running peak.

These are historical risk measures, not forecasts of future loss.

## Risk-adjusted performance

- **Sharpe ratio:** annualized mean daily return divided by annualized return volatility, using a zero risk-free-rate assumption in the current implementation.
- **Sortino ratio:** annualized mean daily return divided by annualized downside volatility.
- **Calmar ratio:** CAGR divided by the absolute maximum drawdown.
- **Profit factor:** total positive daily-return magnitude divided by the absolute total negative daily-return magnitude.

These ratios provide context for evaluating historical return relative to observed risk; they should not be interpreted as guarantees of future performance.

## Market participation

- **20D average volume:** rolling mean of volume over 20 observations.
- **Volume ratio:** latest/current volume divided by the corresponding 20D average volume.
- **Volume change:** period-over-period change in volume.
- **Range %:** daily high-low range relative to the close.

The dashboard uses volume ratio to identify whether the latest session's participation was above or below its recent baseline.

## Decision-support layer

The current decision-intelligence layer is **rule-based and descriptive**. It combines multiple observable dimensions:

1. Short-term trend context from moving averages.
2. Recent and period-level returns.
3. Historical volatility and drawdown.
4. Current market participation versus the 20D volume baseline.
5. Latest-session movement.
6. Data-quality status.

The resulting analyst insights are intended to help a stakeholder decide **what deserves attention**, not what trade to execute. The dashboard does not claim predictive trading accuracy and does not present ML predictions as decision outputs.

## SQL analytical layer

The SQL directory mirrors the analytical workflow using PostgreSQL-style SQL examples:

- Data-quality audits for nulls, duplicates, OHLC consistency, and date coverage.
- Window functions such as `LAG`, `FIRST_VALUE`, `MAX`, and `AVG` for returns, running peaks, moving averages, and volume baselines.
- KPI aggregation for performance and participation.
- Risk analysis for rolling volatility and drawdown.
- Ranking queries for strongest/weakest observations and review queues.

The SQL examples demonstrate how the same analytical questions can be translated into a BI/data-warehouse workflow.

## Reproducibility and QA

1. Keep the source dataset traceable and version-controlled where practical.
2. Keep business definitions documented in the KPI dictionary.
3. Use deterministic feature calculations.
4. Validate OHLCV integrity before producing KPIs.
5. Test API outputs and metric consistency before publishing changes.
6. Keep dashboard labels aligned with the underlying metric definitions.

## Interpretation boundary

This project is a **historical financial analytics and decision-support portfolio project**. It is not financial advice, does not guarantee future returns, and should not be represented as an automated trading strategy.
