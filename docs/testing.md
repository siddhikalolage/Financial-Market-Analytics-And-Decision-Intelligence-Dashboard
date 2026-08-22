# Testing Strategy

## Objective

Testing focuses on analytical correctness, API stability, data validation, and safe handling of numerical edge cases.

## Unit Tests

The analytics layer should be tested independently from Flask. Priority functions include:

- OHLCV validation and loading
- return calculations
- moving averages
- CAGR
- Sharpe ratio
- Sortino ratio
- maximum drawdown
- Calmar ratio
- win rate
- average gain/loss
- profit factor
- volume ratio and spike classification
- decision scoring
- model reliability scoring

## Edge Cases

Tests should explicitly cover:

- empty datasets
- insufficient observations for rolling metrics
- zero starting prices
- constant prices
- missing required columns
- malformed dates
- NaN and infinite numerical values
- missing prediction/model metadata

## API Tests

Flask test-client coverage should verify that the main endpoints return successful status codes and valid JSON structures:

- `/api/health`
- `/api/data`
- `/api/metrics`
- `/api/insights`
- `/api/decision`
- `/api/prediction`
- `/`

## Regression Testing

The dashboard previously experienced template failures when the decision response did not contain the expected `model_reliability` structure. API and dashboard smoke tests should therefore be retained as regression tests whenever the analytics or decision schemas change.

## Validation Commands

Recommended local quality gate:

```text
python -m py_compile analytics/*.py app.py
pytest -q
python -c "from app import app; c=app.test_client(); assert c.get('/').status_code == 200"
git diff --check
```

## Test Philosophy

A passing test suite is not evidence that a financial model is profitable or statistically reliable. Tests establish software and analytical correctness for the implemented logic; model quality must be evaluated separately against appropriate validation baselines.
