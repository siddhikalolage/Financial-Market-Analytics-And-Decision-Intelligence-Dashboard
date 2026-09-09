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
| Daily_Return | Percentage change in Close versus the previous observation |
| Cumulative_Return | Percentage change from the first observed Close |
| MA_20 | 20-observation simple moving average of Close |
| MA_50 | 50-observation simple moving average of Close |
| Rolling_Volatility_20D | 20-observation standard deviation of daily returns annualized by √252 |
| Rolling_Avg_Volume_20D | 20-observation average of Volume |
| Drawdown | Percentage decline from the running historical maximum Close |
| Volume_Change | Percentage change in Volume versus the previous observation |
| Range_Pct | High-Low range expressed as a percentage of Close |
