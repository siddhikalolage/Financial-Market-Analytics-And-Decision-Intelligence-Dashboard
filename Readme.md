# Financial Market Analytics & Decision Intelligence Dashboard

> **Portfolio focus:** Data Analytics • BI Analytics • Financial Data Analysis

A decision-oriented financial analytics project that transforms historical OHLCV market data into performance, risk, market-behaviour and actionable analytical insights through a Flask dashboard and reproducible Python workflow.

## 1. Business Problem

Financial market datasets contain large volumes of price and trading-activity information, but raw OHLCV records do not directly answer business questions.

This project is designed to answer questions such as:

- How has the asset performed over the analysis period?
- What is the latest daily return and cumulative return?
- How volatile has the market been?
- What was the largest historical drawdown?
- How has trading volume changed?
- Is the latest price above or below its short-term moving average?
- What signals should an analyst monitor when evaluating market behaviour?

The project therefore emphasizes **descriptive analytics, KPI development, risk measurement and decision support** rather than presenting speculative price predictions as investment advice.

## 2. Analytical Workflow

```text
Historical OHLCV Data
        ↓
Data Validation & Cleaning
        ↓
Feature Engineering
        ↓
Financial KPIs
        ↓
Performance + Risk Analysis
        ↓
Decision-Oriented Insights
        ↓
Interactive Dashboard / API
```

## 3. Key Analytics

| Area | Metrics / Analysis |
|---|---|
| Performance | Daily return, cumulative return, moving averages |
| Risk | Annualized volatility, rolling volatility, maximum drawdown |
| Participation | 30-day average volume, volume change |
| Market behaviour | Price range %, up/down observations, price-vs-MA position |
| Data quality | Required-column validation, type coercion, duplicates, missing values, chronological ordering |
| Decision intelligence | Automated analyst observations highlighting performance, risk and participation |

## 4. Dashboard

The web dashboard is structured around the questions an analyst or BI stakeholder would typically ask:

1. **Executive KPIs** — latest close, daily return, period return, volatility, drawdown and average volume.
2. **Performance** — price trend with 20-day moving average.
3. **Participation** — trading-volume behaviour.
4. **Risk** — rolling volatility and historical drawdown.
5. **Decision Intelligence** — concise observations generated from the underlying metrics.
6. **Methodology** — definitions and interpretation guidance so the dashboard is auditable.

## 5. Data

The current repository uses `data/stock_data.csv` with the following fields:

- `Date`
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

The application treats the file as a **historical analytical dataset**. It does not claim real-time market connectivity.

## 6. Data Preparation

`app.py` validates the dataset before calculating analytics:

- confirms required OHLCV columns exist;
- parses dates safely;
- coerces numeric fields to numeric types;
- removes invalid rows and duplicate dates;
- sorts observations chronologically;
- checks that enough observations exist for rolling metrics;
- rejects negative OHLCV values.

Derived analytical fields include daily return, cumulative return, moving averages, rolling volatility, rolling average volume, drawdown, volume change and intraday range percentage.

## 7. SQL Analytics Layer

The `sql/` directory provides database-oriented versions of the analytical logic so the project demonstrates skills beyond Python scripting:

- `data_quality.sql` — nulls, duplicates, OHLC consistency and date coverage.
- `kpi_analysis.sql` — current KPI calculations and drawdown.
- `performance_analysis.sql` — returns and moving averages.
- `risk_analysis.sql` — rolling volatility and drawdown analysis.
- `ranking_analysis.sql` — performance ranking and descriptive risk bands.

The SQL examples use modern window-function patterns and are intended to be adapted to a relational database containing the same `stock_data` schema.

## 8. Analytical Documentation

- `docs/data_dictionary.md` — source and derived field definitions.
- `docs/methodology.md` — calculation methodology and interpretation principles.
- `docs/business_questions.md` — mapping between stakeholder questions, metrics and dashboard views.

## 9. Technology Stack

- **Python** — analytical and application logic
- **Pandas / NumPy** — data preparation and numerical analysis
- **Flask** — dashboard and JSON API layer
- **Chart.js** — interactive browser visualizations
- **HTML / CSS** — responsive presentation layer
- **Jupyter Notebook** — exploratory analysis and modelling workflow
- **SQL** — data-quality, KPI, performance, risk and ranking analytics
- **Pytest / GitHub Actions** — automated validation

## 10. API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Render the analytics dashboard |
| `GET /api/data` | Return the latest 90 observations with selected derived metrics |
| `GET /api/metrics` | Return the current analytical KPI set |
| `GET /api/health` | Lightweight application health check |

## 11. Project Structure

```text
Financial-Market-Analytics-And-Decision-Intelligence-Dashboard/
├── data/
│   └── stock_data.csv
├── docs/
│   ├── business_questions.md
│   ├── data_dictionary.md
│   └── methodology.md
├── notebook/
│   └── analysis_and_prediction.ipynb
├── sql/
│   ├── data_quality.sql
│   ├── kpi_analysis.sql
│   ├── performance_analysis.sql
│   ├── risk_analysis.sql
│   └── ranking_analysis.sql
├── tests/
│   └── test_app.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── Readme.md
```

## 12. Running Locally

```bash
git clone https://github.com/siddhikalolage/Financial-Market-Analytics-And-Decision-Intelligence-Dashboard.git
cd Financial-Market-Analytics-And-Decision-Intelligence-Dashboard
python -m venv .venv
```

Activate the environment and install dependencies:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000/` in a browser.

Run automated tests with:

```powershell
python -m pytest -q
```

For development debugging, set `FLASK_DEBUG=1`. The application defaults to debug-disabled behaviour.

## 13. Analytical Methodology

### Daily Return

`(Current Close / Previous Close - 1) × 100`

### Cumulative Return

`(Current Close / First Close - 1) × 100`

### Annualized Volatility

The standard deviation of daily percentage returns is scaled by `√252`, a common approximation for the number of trading sessions in a year.

### Maximum Drawdown

`(Current Close / Running Peak - 1) × 100`

### Moving Average

The dashboard uses a 20-observation moving average as a descriptive trend indicator.

See `docs/methodology.md` for the full analytical contract.

## 14. Predictive Modelling Note

The notebook retains a small predictive benchmark as a secondary learning component. Its chronological split now occurs before feature scaling, preventing test-period information from influencing the scaler. The production dashboard deliberately prioritizes transparent historical analytics and decision support over speculative forecasting.

Any future predictive model should be evaluated against appropriate chronological baselines, with leakage prevention, time-aware validation and clearly reported error metrics before being treated as a serious forecasting component.

## 15. Testing & Quality

The repository includes automated tests for the dataset contract and API health, metrics and data endpoints. GitHub Actions runs the test suite for changes to the main and analytics-upgrade branches.

## 16. Data Analyst / BI Analyst Relevance

This project demonstrates an end-to-end analytical workflow:

**Data → Quality Checks → Transformation → KPI Design → Risk/Performance Analysis → Visualization → Insight → Decision Support**

Relevant skills demonstrated include:

- Python and Pandas analytics
- Time-series data preparation
- SQL window functions
- Financial KPI design
- Statistical risk indicators
- Dashboard development
- API-based data delivery
- Analytical storytelling
- Reproducible methodology
- Automated testing / CI

## 17. Ownership

This repository is maintained as an individual portfolio project by **Siddhika Lolage**.

## 18. Disclaimer

This project is for educational and portfolio demonstration purposes. Historical analytics do not guarantee future market performance and should not be interpreted as financial, investment or trading advice.
