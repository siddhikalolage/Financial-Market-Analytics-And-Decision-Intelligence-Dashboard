# KPI Dictionary

## Purpose

This document defines the analytical KPIs exposed by the Financial Market Analytics & Decision Intelligence Dashboard. The goal is to make every headline metric reproducible, interpretable, and traceable from source data to dashboard output.

## Data lineage

```text
stock_data.csv
    ↓
Data validation
    ↓
Derived daily metrics
    ↓
KPI calculations
    ↓
Flask API (/api/metrics, /api/data)
    ↓
Dashboard KPI cards + charts
    ↓
Analyst interpretation
```

The project uses historical OHLCV observations. KPIs describe observed market behaviour in the selected dataset; they are not trading recommendations or forecasts.

## KPI definitions

| KPI | Definition | Formula / Method | Business interpretation |
|---|---|---|---|
| Latest Close | Most recent closing price | `Close` on latest date | Current endpoint of the historical price series |
| Daily Return | One-session percentage movement | `(Close_t / Close_(t-1) - 1) × 100` | Measures short-term price movement |
| Period Return | Total return across the dataset period | `(Last Close / First Close - 1) × 100` | Shows overall historical price change |
| 5D Return | Five-observation price return | `(Close_t / Close_(t-5) - 1) × 100` | Short-term momentum context |
| 20D Return | Twenty-observation price return | `(Close_t / Close_(t-20) - 1) × 100` | Medium-short-term performance context |
| YTD Return | Return from first available observation of the calendar year | `(Latest Close / First YTD Close - 1) × 100` | Calendar-year performance context |
| CAGR | Annualized growth over the observed period | `(Ending / Beginning)^(1 / years) - 1` | Normalizes long-period growth to an annual rate |
| Annualized Volatility | Standard deviation of daily returns scaled to a trading year | `STDDEV(daily returns) × √252` | Measures variability of observed returns |
| Downside Volatility | Volatility calculated from negative daily returns | Standard deviation of negative return observations, annualized | Focuses risk measurement on downside movement |
| Sharpe Ratio | Return relative to observed volatility | Annualized return / annualized volatility | Risk-adjusted performance indicator; interpretation depends on assumptions |
| Sortino Ratio | Return relative to downside volatility | Annualized return / downside volatility | Emphasizes downside risk rather than total volatility |
| Calmar Ratio | Annualized return relative to maximum drawdown | Annualized return / absolute max drawdown | Contextualizes growth against historical peak-to-trough loss |
| Maximum Drawdown | Largest peak-to-trough decline | `min((Close / running_peak) - 1)` | Measures worst observed historical decline from a prior peak |
| Current Drawdown | Drawdown at the latest observation | `(Latest Close / latest running peak - 1) × 100` | Shows current distance from the historical running peak |
| Average Volume | Mean traded volume over the dataset | `AVG(Volume)` | Baseline level of market participation |
| 20D Average Volume | Rolling 20-observation volume baseline | `AVG(Volume)` over 20 rows | Recent participation baseline |
| Volume Ratio | Current volume relative to recent baseline | `Volume / 20D Average Volume` | Highlights unusually high or low volume |
| Up Days | Count of positive-return observations | `Daily Return > 0` | Measures frequency of positive sessions |
| Down Days | Count of negative-return observations | `Daily Return < 0` | Measures frequency of negative sessions |
| Flat Days | Count of zero-return observations | `Daily Return = 0` | Identifies sessions without price movement |
| Average Daily Return | Mean of daily percentage returns | `AVG(Daily Return)` | Describes average observed session movement |
| Observations | Number of historical rows | `COUNT(*)` | Establishes analytical sample size |

## Data-quality KPIs

| Check | Definition | Expected outcome |
|---|---|---|
| Missing Values | Count of null values across required OHLCV fields | `0` preferred |
| Duplicate Dates | Number of duplicated date records | `0` preferred |
| OHLC Consistency | Validates `High >= Open/Close` and `Low <= Open/Close` | No invalid rows |
| Negative Values | Detects negative OHLCV values | No invalid rows |
| Zero Close | Detects zero closing prices that could break return calculations | `0` preferred |
| Chronological Order | Confirms observations are ordered by date before time-series calculations | `PASS` |

## Interpretation rules

- **Returns:** Positive values indicate price appreciation over the selected window; negative values indicate decline.
- **Volatility:** Higher values indicate greater historical variability, not necessarily greater future risk.
- **Drawdown:** More negative values indicate a larger decline from a previous observed peak.
- **Volume ratio:** Values above `1.0` indicate volume above the rolling baseline; values below `1.0` indicate volume below baseline.
- **Risk-adjusted ratios:** These are descriptive measures and depend on the project's annualization and return assumptions.
- **Risk bands:** The SQL decision-support layer uses `Normal Range`, `Moderate Drawdown`, and `High Drawdown` as analytical review categories rather than investment recommendations.

## Dashboard mapping

```text
Performance KPIs
  → Latest Close / Daily Return / 20D Return / YTD Return / CAGR

Risk KPIs
  → Annualized Volatility / Max Drawdown / Sharpe / Sortino / Current Drawdown

Participation KPIs
  → Average Volume / Volume Ratio

Data-quality KPIs
  → Missing Values / Duplicate Dates / Date Order

Supporting visuals
  → Price + MA20 + MA50
  → Volume + 20D Average Volume
  → Rolling Volatility
  → Drawdown
```

## Why this matters for BI

A KPI dictionary prevents the dashboard from becoming a collection of unexplained numbers. Each metric has a defined calculation, interpretation, and lineage. This supports stakeholder communication, reproducibility, QA, and consistent implementation across Python, SQL, APIs, and BI-style presentation layers.
