# SQL Analytics Layer

This directory demonstrates how the project's Python-derived analytics can be translated into relational SQL for a Data Analyst / BI Analyst workflow.

## Analytical flow

```text
stock_data
   │
   ├── Data quality audit
   │      ├── NULL checks
   │      ├── duplicate-date checks
   │      ├── OHLC consistency
   │      └── date coverage
   │
   ├── Window-function transformations
   │      ├── LAG → daily returns
   │      ├── FIRST_VALUE → cumulative return
   │      ├── MAX → running peak / drawdown
   │      └── AVG → moving averages / volume baseline
   │
   ├── KPI layer
   │      ├── 5D / 20D performance
   │      ├── volume ratio
   │      └── up / down session mix
   │
   ├── Risk layer
   │      ├── rolling volatility
   │      ├── downside volatility
   │      └── drawdown bands
   │
   └── Decision-support layer
          ├── rankings
          ├── unusual observations
          └── analyst review queues
```

## Query catalogue

| File | Business purpose | Main SQL techniques |
|---|---|---|
| `data_quality.sql` | Validate analytical reliability before reporting | CASE, GROUP BY, HAVING, aggregate checks |
| `kpi_analysis.sql` | Build executive KPI outputs | LAG, FIRST_VALUE, MAX, AVG, window functions |
| `performance_analysis.sql` | Study returns and trend | LAG, moving averages, ranking |
| `risk_analysis.sql` | Quantify volatility and downside risk | rolling windows, standard deviation, drawdown |
| `ranking_analysis.sql` | Prioritize observations for analyst review | CASE, DENSE_RANK, risk bands |

## Example stakeholder questions

### Performance
- What is the latest daily return?
- How has the asset performed over 5 and 20 observations?
- Which sessions produced the strongest positive/negative moves?
- Is the current price above or below its moving-average context?

### Risk
- What is the annualized historical volatility?
- What is the current and maximum drawdown?
- Which dates belong to elevated drawdown bands?
- How frequently does downside movement occur?

### Market participation
- How does the latest volume compare with the 20-observation baseline?
- Which sessions show unusually high participation?

### Data quality
- Are there missing OHLCV fields?
- Are dates duplicated or out of sequence?
- Are OHLC relationships logically valid?

## SQL-to-dashboard mapping

```text
SQL / Python analytical layer
            ↓
        KPI outputs
            ↓
     Flask JSON endpoints
            ↓
       Chart.js dashboard
            ↓
   Analyst interpretation
```

## SQL dialect

The examples are written using common SQL window-function patterns and PostgreSQL-style analytical syntax where dialect-specific functions are required. Adapt casting, standard-deviation functions and row-limiting syntax when running against SQL Server, MySQL or another warehouse.

## Why this layer matters

The SQL layer demonstrates that the project is not only a Python dashboard. The same business logic can be expressed as reusable database transformations, which is closer to how analytical reporting pipelines are implemented in production BI environments.
