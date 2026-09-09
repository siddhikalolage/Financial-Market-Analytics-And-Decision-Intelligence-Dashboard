# Business Questions & Dashboard Mapping

The dashboard is designed around questions a Data Analyst or BI Analyst would answer for a stakeholder reviewing historical market behaviour.

| Business question | Primary metric / analysis | Dashboard view |
|---|---|---|
| How has the asset performed? | Daily, 5D, 20D, YTD and period returns | Executive KPI cards |
| What is the latest observed price? | Latest Close | Executive KPI card |
| Is recent price behaviour above or below its short-term baseline? | Close vs MA20 | Price & MA chart / analyst insights |
| How does the medium-term trend compare? | MA50 | Price & MA chart |
| How volatile has the market been? | Annualized and rolling 20D volatility | Risk KPI / volatility chart |
| How severe has historical downside been? | Maximum and current drawdown | Risk KPI / drawdown chart |
| How does historical return compare with observed risk? | Sharpe, Sortino and Calmar ratios | Risk-adjusted KPI cards |
| Is current market participation elevated? | Volume and 20D volume ratio | Volume chart / Volume Ratio KPI |
| How frequently were sessions positive or negative? | Up, down and flat session counts | KPI / SQL analysis |
| Which observations deserve analyst investigation? | Extreme returns, drawdowns and volume conditions | Decision-intelligence insights / SQL rankings |
| Can the dataset be trusted for analysis? | Missing, duplicate, chronological and OHLC validation | Data-quality section |
| Can the analysis be reproduced in a database workflow? | SQL window functions and analytical queries | `sql/` analytical layer |

## Stakeholder interpretation flow

```text
Performance
    ↓
Trend context
    ↓
Risk & downside
    ↓
Market participation
    ↓
Data quality confidence
    ↓
Analyst observations
    ↓
Further investigation / decision support
```

## Decision-support principle

The dashboard translates transparent historical metrics into concise observations so a stakeholder can identify periods requiring investigation. These observations are descriptive and historical; they are **not trading recommendations, forecasts, or guarantees of future performance**.
