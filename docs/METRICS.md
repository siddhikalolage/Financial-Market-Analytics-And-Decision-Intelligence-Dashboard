# Financial Metrics Reference

## Performance

### Daily Return

Percentage change in closing price between consecutive trading observations.

### 5-Day Return

Percentage change in closing price over five trading observations.

### 20-Day Return

Percentage change in closing price over twenty trading observations.

### YTD Return

Return from the first available trading observation of the current calendar year to the latest observation.

### Cumulative Return

Total compounded return across the available observation period.

### CAGR

Compound Annual Growth Rate representing the annualized growth rate over the observation period.

### Win Rate

Percentage of trading observations with a positive daily return.

### Profit Factor

Ratio of aggregate gains to aggregate losses.

## Risk-Adjusted Metrics

### Sharpe Ratio

Measures return relative to total return volatility.

### Sortino Ratio

Measures return relative to downside volatility.

### Calmar Ratio

Relates annualized return to maximum drawdown.

## Risk Metrics

### Rolling Volatility

Standard deviation of returns over a rolling 20-trading-day window.

### Annualized Volatility

Rolling return volatility scaled to an annualized measure.

### Downside Volatility

Volatility calculated from negative return behaviour.

### Maximum Drawdown

Largest observed decline from a previous running peak.

### Current Drawdown

Current decline from the historical running peak.

### Drawdown Duration

Number of observations spent below the previous running peak.

## Trend Metrics

The system uses:

- MA20
- MA50
- MA200
- Price versus MA20
- Price versus MA50
- Price versus MA200

A combined moving-average assessment is used to classify the current trend.

## Momentum

Momentum is evaluated using recent 5-day and 20-day returns.

## Volume

### Volume Ratio

Current volume divided by the rolling 20-day average volume.

### Volume Spike

Identifies unusually elevated trading activity according to the project's configured threshold.

## Interpretation

These metrics are analytical indicators rather than investment recommendations. Individual metrics should be interpreted together with market conditions, risk, and model reliability.
