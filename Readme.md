Financial Market Analytics & Decision Intelligence Dashboard

An end-to-end financial analytics project combining time-series analysis, risk analytics, machine learning, and Flask-based decision intelligence into an interactive stock market dashboard.

Disclaimer: This project is for educational and research purposes only. It does not provide financial advice or investment recommendations.

Project Overview

This project transforms historical OHLCV stock data into analytical insights through four layers:

Data Layer — loads and validates historical market data.

Analytics Layer — calculates returns, trends, volatility, drawdowns, volume behaviour, and risk-adjusted metrics.

Machine Learning Layer — trains a neural-network regression model for next-day price prediction and evaluates it against a persistence baseline.

Decision Intelligence Layer — combines market evidence, momentum, trend, risk, volume, and model reliability into an explainable market decision.

The results are exposed through a Flask dashboard and REST API endpoints.

Key Capabilities

Financial Analytics

Daily, 5-day, and 20-day returns

YTD and cumulative returns

CAGR

Win rate

Average gain and loss

Profit factor

Sharpe ratio

Sortino ratio

Calmar ratio

Maximum and current drawdown

Rolling and annualized volatility

Downside volatility

Moving averages: MA20, MA50, MA200

Price distance from moving averages

Volume ratio and volume spike detection

Drawdown duration

Dataset statistics

Machine Learning

Next-day closing-price prediction

Sequential time-series train/test methodology

Feature scaling

Neural-network regression

Prediction evaluation

Persistence-baseline comparison

Model reliability scoring

ML warning when the model underperforms the baseline

Decision Intelligence

Bullish / Bearish / Neutral market classification

Market decision score

Confidence score

Risk level

Explainable evidence

Momentum assessment

Trend assessment

Volume assessment

ML reliability weighting

Human-readable decision explanation

Dashboard & API

Interactive Flask dashboard

Financial KPI cards

Trend and risk visualizations

Prediction information

Decision intelligence panel

REST endpoints for analytics and model outputs

JSON-safe API responses

Architecture

                    ┌─────────────────────┐
                    │  stock_data.csv     │
                    │       OHLCV         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Data Loader      │
                    │ validation/loading  │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ Financial Metrics│       │ Machine Learning │
       │ Returns / Risk   │       │ Prediction Model │
       │ Trend / Volume   │       │ Evaluation       │
       └────────┬─────────┘       └────────┬─────────┘
                │                          │
                └────────────┬─────────────┘
                             ▼
                  ┌──────────────────────┐
                  │ Decision Intelligence│
                  │ Score / Confidence   │
                  │ Evidence / Risk      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Flask Dashboard + API│
                  └──────────────────────┘

Repository Structure

Financial-Market-Analytics-And-Decision-Intelligence-Dashboard/
│
├── analytics/
│   ├── data_loader.py
│   ├── metrics.py
│   └── decision_engine.py
│
├── data/
│   └── stock_data.csv
│
├── model/
│   └── model and preprocessing artifacts
│
├── notebook/
│   └── analysis_and_prediction_executed.ipynb
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── tests/
│   └── test files
│
├── app.py
├── requirements.txt
├── create_notebook.py
├── save_model_artifacts.py
└── README.md

Data

The project uses historical daily OHLCV data:

Column

Description

Date

Trading date

Open

Opening price

High

Highest price

Low

Lowest price

Close

Closing price

Volume

Trading volume

Current development dataset:

522 observations

6 columns

2023-01-02 to 2024-12-31

Daily trading observations

Financial Metrics

The analytics engine calculates:

Returns

1-day return

5-day return

20-day return

YTD return

Cumulative return

CAGR

Risk-Adjusted Performance

Sharpe Ratio — measures return relative to total volatility.

Sortino Ratio — measures return relative to downside volatility.

Calmar Ratio — measures CAGR relative to maximum drawdown.

Risk

Rolling volatility

Annualized volatility

Downside volatility

Maximum drawdown

Current drawdown

Drawdown duration

Trend

MA20

MA50

MA200

Price vs MA20

Price vs MA50

Price vs MA200

Bullish/bearish moving-average count

Volume

Current volume

20-day average volume

Volume ratio

Volume spike detection

Machine Learning Pipeline

Historical OHLCV
       │
       ▼
Feature Selection
       │
       ▼
Target Creation
(next-day Close)
       │
       ▼
Sequential Train/Test Split
       │
       ▼
Feature Scaling
       │
       ▼
Neural Network
       │
       ▼
Prediction
       │
       ▼
Model Evaluation
       │
       ▼
Baseline Comparison
       │
       ▼
Reliability Score

The ML task is next-day closing-price regression. The pipeline preserves chronological order and avoids random shuffling so future observations are not introduced into the training process.

Model Reliability

The decision engine does not blindly trust the ML prediction. The trained model is evaluated against a persistence baseline:

Tomorrow's price = Today's price

Model performance is compared using metrics such as MAE, R², and improvement versus baseline. If the ML model performs worse than the baseline, its decision weight is reduced or removed and the dashboard explicitly reports low model reliability.

Decision Intelligence

Market Movement
      +
Momentum
      +
Trend
      +
Volume
      +
ML Signal
      +
Model Reliability
      +
Risk
      ↓
Decision Score
      ↓
Confidence
      ↓
Explainable Decision

The system can produce Bullish, Bearish, or Neutral decisions together with confidence, risk level, evidence, and a human-readable explanation.

Example Analytics Snapshot

Example output from the current historical dataset:

Performance
-----------
5D Return:              -2.41%
20D Return:             -7.68%
YTD Return:              4.17%
Cumulative Return:      17.52%
CAGR:                    8.42%
Win Rate:               51.63%
Profit Factor:           1.07

Risk Adjusted
-------------
Sharpe Ratio:             0.41
Sortino Ratio:            0.73
Calmar Ratio:             0.30

Trend
-----
Price vs MA20:           -4.76%
Price vs MA50:           -6.50%
Price vs MA200:          -8.43%
Trend:                   Bearish

Risk
----
Annualized Volatility:   27.11%
Maximum Drawdown:       -27.99%
Current Drawdown:       -24.92%
Risk Level:              High

Volume
------
Volume Ratio:             1.37x
Status:                   Elevated Volume

These values are generated from the project's historical dataset and may change if the data changes.

Flask Application

Run the dashboard with:

python app.py

Local URL:

http://127.0.0.1:5000

API Endpoints

GET /
GET /api/health
GET /api/metrics
GET /api/decision
GET /api/prediction

Installation

git clone https://github.com/siddhikalolage/Financial-Market-Analytics-And-Decision-Intelligence-Dashboard.git
cd Financial-Market-Analytics-And-Decision-Intelligence-Dashboard
python -m venv .venv

Windows PowerShell:

.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

Notebook

The repository includes:

notebook/analysis_and_prediction_executed.ipynb

The notebook documents data loading, inspection, EDA, visualization, feature preparation, target generation, model training, evaluation, prediction visualization, and analytical conclusions.

Testing

Python Syntax

python -m py_compile app.py
python -m py_compile analytics\metrics.py
python -m py_compile analytics\decision_engine.py

API Smoke Test

python -c "from app import app; c=app.test_client(); print('HEALTH:',c.get('/api/health').status_code); print('METRICS:',c.get('/api/metrics').status_code); print('DECISION:',c.get('/api/decision').status_code); print('PREDICTION:',c.get('/api/prediction').status_code); print('DASHBOARD:',c.get('/').status_code)"

Expected:

HEALTH: 200
METRICS: 200
DECISION: 200
PREDICTION: 200
DASHBOARD: 200

Repository Validation

git diff --check
git status

Reproducibility

The project is designed for reproducible local execution through a static historical dataset, deterministic analytical calculations, explicit feature construction, chronological train/test separation, saved model artifacts where applicable, JSON-safe API outputs, and dependency declaration through requirements.txt.

Data Quality & Safety Principles

Missing and invalid numerical values are handled safely.

Infinite and NaN values are converted to JSON-safe representations.

Rolling calculations use historical observations only.

Time-series ordering is preserved.

Future observations are not used for historical feature construction.

Model performance is compared against a simple baseline.

Low-reliability ML predictions are explicitly flagged.

Financial outputs include a research-use disclaimer.

Technologies

Programming

Python

Data Analytics

Pandas

NumPy

Matplotlib

Machine Learning

scikit-learn

TensorFlow

Keras

Web

Flask

Jinja2

HTML

CSS

JavaScript

Development

Jupyter Notebook

Git

GitHub

What This Project Demonstrates

This project demonstrates practical skills relevant to Data Analyst, Data Scientist, Business Intelligence, and Financial Analytics roles:

Data cleaning and validation

Exploratory data analysis

Time-series analysis

Statistical metrics

Financial risk analytics

Feature engineering

Machine learning

Model evaluation

Baseline benchmarking

Explainable decision systems

REST API development

Dashboard development

Reproducible analytical workflows

Git/GitHub project management

Limitations

This project is an educational analytics system and is not a production trading platform.

Historical data does not guarantee future performance.

The ML model is not a production trading system.

The dataset is limited compared with institutional market datasets.

Transaction costs and slippage are not modeled.

Market regime changes can reduce model reliability.

External macroeconomic and fundamental variables are not included.

The dashboard should not be used as an automated investment decision system.

Future Improvements

Live market-data ingestion

Multi-stock portfolio analytics

Sector-level comparison

Fundamental financial indicators

RSI and MACD indicators

Walk-forward validation

Hyperparameter optimization

Model comparison across multiple algorithms

Automated model monitoring

Backtesting framework

Portfolio risk analysis

Docker deployment

CI/CD testing

Cloud deployment

Authentication and role-based dashboard access

Project Status

Status: Active Development

The current version focuses on financial analytics, explainable decision intelligence, ML benchmarking, dashboard/API integration, and reproducible data-science workflows.

Author

Siddhika Lolage

GitHub: https://github.com/siddhikalolage

Repository: https://github.com/siddhikalolage/Financial-Market-Analytics-And-Decision-Intelligence-Dashboard