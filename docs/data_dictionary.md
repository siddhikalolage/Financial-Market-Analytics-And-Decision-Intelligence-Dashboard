# Data Dictionary

## Source

`data/stock_data.csv` is the historical OHLCV dataset used by the application.

| Field | Type | Meaning |
|---|---|---|
| Date | Date | Trading observation date |
| Open | Numeric | Opening price |
| High | Numeric | Highest observed price |
| Low | Numeric | Lowest observed price |
| Close | Numeric | Closing price |
| Volume | Numeric | Trading volume |

## Derived analytical fields

| Field | Definition |
|---|---|
| Daily_Return | Decimal percentage change in Close versus the previous observation |
| Daily_Return_Pct | Daily return expressed as a percentage for API/dashboard presentation |
| Cumulative_Return | Decimal cumulative price return from the first observed Close |
| MA_20 | 20-observation simple moving average of Close |
| MA_50 | 50-observation simple moving average of Close |
| MA_200 | 200-observation simple moving average of Close where sufficient history exists |
| Rolling_Volatility_20D | 20-observation standard deviation of daily returns annualized by √252 |
| Rolling_Avg_Volume_20D | 20-observation average of Volume |
| Volume_Ratio | Current Volume divided by the 20-observation average volume |
| Drawdown | Percentage decline from the running historical maximum Close |
| Volume_Change | Percentage change in Volume versus the previous observation |
| Range_Pct | High-Low range expressed as a percentage of Close |

## KPI and API fields

The `/api/metrics` endpoint aggregates the analytical dataset into stakeholder-facing KPIs. The dashboard uses the following fields:

| KPI / API field | Meaning |
|---|---|
| last_close | Latest observed closing price |
| percent_change | Latest daily return expressed as a percentage |
| period_return | Total return from first to latest observed Close |
| return_5d | Five-observation return |
| return_20d | Twenty-observation return |
| ytd_return | Return from the first available observation in the latest calendar year |
| cagr | Annualized growth rate over the observed calendar period |
| annualized_volatility | Standard deviation of daily returns annualized by √252 |
| downside_volatility | Annualized variability of negative return observations |
| sharpe_ratio | Annualized return relative to annualized volatility under the implementation's assumptions |
| sortino_ratio | Annualized return relative to downside volatility |
| calmar_ratio | CAGR relative to absolute maximum drawdown |
| max_drawdown | Worst historical peak-to-trough decline |
| current_drawdown | Latest distance from the running historical peak |
| average_volume | Mean volume across the available observations |
| volume_ratio | Latest volume relative to the 20-observation volume baseline |
| up_days | Number of positive-return observations |
| down_days | Number of negative-return observations |
| flat_days | Number of zero-return observations |
| average_daily_return | Mean daily return across the available observations |
| observations | Number of validated historical observations |
| start_date / end_date | Analytical date range |

## Data-quality fields

| Field | Definition | Expected outcome |
|---|---|---|
| missing_values | Count of missing values in required analytical data | `0` preferred |
| duplicate_dates | Count of duplicate dates after validation | `0` preferred |
| date_order_valid | Boolean confirming chronological ordering | `true` |

## Calculation conventions

- Moving averages use observation counts rather than calendar-day interpolation.
- Rolling volatility uses a 20-observation window and a 252-observation annualization convention.
- Drawdown is measured from the running historical maximum closing price.
- Volume ratio uses the current volume divided by the 20-observation rolling average volume.
- Returns are historical descriptive measures and are not forecasts or investment recommendations.

## Lineage

```text
stock_data.csv
    ↓
load_data()
    ↓
validated OHLCV dataset
    ↓
derived analytical fields
    ↓
build_metrics() / chart_payload()
    ↓
/api/metrics + /api/data
    ↓
Dashboard KPI cards + charts
```

For formal business interpretation of the headline KPIs, see [`docs/kpi_dictionary.md`](kpi_dictionary.md).
