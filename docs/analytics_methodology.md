# Analytics Methodology

## 1. Analytical objective

The project converts historical financial-market OHLCV data into a structured decision-support view for analysts. The methodology prioritizes data quality, descriptive statistics, time-series transformations, KPI design, SQL analysis, and dashboard storytelling.

This is an analytics and BI project. It does not provide investment advice, execute trades, or claim to predict future market prices.

## 2. End-to-end analytical flow

```text
                    ┌─────────────────────┐
                    │ Historical OHLCV CSV │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Data Quality Layer  │
                    │ nulls / duplicates  │
                    │ OHLC logic / dates  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Transformation Layer│
                    │ returns / MAs /     │
                    │ volume / drawdown   │
                    └──────────┬──────────┘
                               ↓
             ┌─────────────────┴─────────────────┐
             ↓                                   ↓
    ┌──────────────────┐                ┌──────────────────┐
    │ Python KPI Layer │                │ SQL Analytics    │
    │ performance/risk │                │ window functions │
    └────────┬─────────┘                └────────┬─────────┘
             └─────────────────┬─────────────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Decision-Support    │
                    │ insights / rankings │
                    │ review categories   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Flask API Layer     │
                    │ metrics + data      │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Dashboard           │
                    │ KPI → trend → risk │
                    │ → data quality      │
                    └─────────────────────┘
```

## 3. Step 1 — Source data

The analytical dataset follows an OHLCV structure:

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

The data is treated as historical observations rather than a live market feed.

## 4. Step 2 — Data validation

Before calculations are consumed by the dashboard, the project checks:

1. Required fields and missing values.
2. Duplicate dates.
3. Chronological ordering.
4. Non-negative OHLCV values.
5. Non-zero closing prices.
6. OHLC logical consistency:
   - `High >= max(Open, Close)`
   - `Low <= min(Open, Close)`
   - `High >= Low`

The same validation philosophy is represented in the SQL data-quality layer so that quality controls are understandable outside the Python application.

## 5. Step 3 — Time-series transformations

The application derives reusable analytical fields rather than calculating every visual independently.

### Returns

```text
Daily Return = (Close_t / Close_(t-1)) - 1
```

The dashboard expresses daily returns as percentages.

### Moving averages

- MA20 = rolling mean of the last 20 observations.
- MA50 = rolling mean of the last 50 observations.
- MA200 = rolling mean of the last 200 observations where sufficient history exists.

Moving averages provide trend context and are not treated as trading signals.

### Rolling volatility

20-observation return variability is annualized using a 252-observation trading-year convention.

```text
Annualized Volatility = Daily Return Std. Dev. × √252
```

### Drawdown

A running historical peak is maintained and drawdown is calculated as:

```text
Drawdown = (Close / Running Peak) - 1
```

The most negative value is maximum drawdown.

### Volume ratio

```text
Volume Ratio = Current Volume / 20D Average Volume
```

This provides context for whether recent participation is above or below its recent baseline.

## 6. Step 4 — KPI framework

The KPI layer is organized around four business dimensions:

### Performance

- Latest Close
- Daily Return
- 5D Return
- 20D Return
- YTD Return
- Period Return
- CAGR

### Risk

- Annualized Volatility
- Downside Volatility
- Maximum Drawdown
- Current Drawdown
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio

### Market participation

- Average Volume
- 20D Average Volume
- Volume Ratio
- Up/Down/Flat session counts

### Data quality

- Missing values
- Duplicate dates
- Date ordering
- Invalid OHLCV rows

See `docs/kpi_dictionary.md` for the formal definition of each KPI.

## 7. Step 5 — SQL analytical layer

The SQL layer demonstrates how the same analytical questions can be expressed using relational analytics techniques.

Key techniques include:

- `LAG()` for period-over-period returns.
- `FIRST_VALUE()` for period baselines.
- `MAX() OVER()` for running peaks.
- `AVG() OVER()` for moving averages and volume baselines.
- `DENSE_RANK()` for analyst review queues.
- `CASE` expressions for direction and risk classification.

The SQL files are written as PostgreSQL-style analytical examples. The exact syntax should be adapted when moving the queries to another database engine.

## 8. Step 6 — Decision-support layer

The project turns calculations into analyst-oriented observations instead of presenting raw statistics only.

Examples include:

- price distance from MA20,
- current drawdown relative to historical maximum drawdown,
- annualized volatility,
- current volume relative to the 20-day baseline,
- strongest and weakest observed sessions.

These outputs support investigation and reporting. They intentionally avoid prescriptive buy/sell recommendations.

## 9. Step 7 — Dashboard storytelling

The dashboard follows an executive-to-diagnostic sequence:

```text
Executive Snapshot
      ↓
Performance Context
      ↓
Risk Context
      ↓
Market Participation
      ↓
Trend / Volatility / Drawdown Charts
      ↓
Data Quality
      ↓
Analyst Insights
      ↓
Methodology
```

This ordering helps a stakeholder answer:

1. What is happening?
2. How large is the movement?
3. How volatile or drawdown-heavy is the period?
4. Is market participation unusual?
5. Can the result be trusted?
6. What should an analyst investigate next?

## 10. API and presentation architecture

```text
Python analytical dataframe
          ↓
   Flask application
      ↙         ↘
/api/metrics   /api/data
      ↓           ↓
 KPI cards     Chart payloads
      \           /
       ↓         ↓
        Dashboard UI
```

The API separates analytical computation from presentation, making the dashboard easier to maintain and test.

## 11. Testing and reproducibility

The repository includes automated tests for core application contracts, including source columns, chronological integrity, derived analytics, API fields, KPI keys, and metric consistency.

A reproducible workflow is:

```text
Clone repository
    ↓
Install requirements
    ↓
Run tests
    ↓
Run Flask application
    ↓
Inspect dashboard
    ↓
Review SQL analysis
```

CI is intended to execute the automated test suite on supported Python environments.

## 12. Analyst limitations

- The source dataset is historical rather than a guaranteed live feed.
- Moving averages and risk metrics are descriptive.
- Annualized metrics depend on the 252-observation convention.
- Risk-adjusted ratios depend on their return and volatility assumptions.
- No causal relationship should be inferred from correlations or coincident price/volume movements.
- The dashboard is decision support, not investment advice.

## 13. Data Analyst / BI Analyst competency mapping

| Competency | Evidence in project |
|---|---|
| Data cleaning | Explicit OHLCV validation and quality checks |
| SQL analytics | Window functions, ranking, risk and KPI queries |
| Python analytics | Pandas-based transformations and KPI computation |
| KPI design | Formal KPI dictionary and business interpretation |
| Dashboarding | Executive KPI cards, trend, risk and quality visuals |
| Business thinking | Business questions and decision-support insights |
| Data quality | Null, duplicate, range, chronology and value checks |
| Testing | Automated application/data-contract tests |
| Documentation | README, SQL guide, methodology and KPI dictionary |
| Communication | Executive-to-diagnostic dashboard storytelling |
