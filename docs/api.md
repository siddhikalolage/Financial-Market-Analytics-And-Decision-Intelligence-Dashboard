# API Reference

The Flask application exposes JSON endpoints for the dashboard's analytical layers.

## Health

`GET /api/health`

Returns application health information.

## Historical Data

`GET /api/data`

Returns prepared historical chart data including dates, OHLC values, volume, returns, moving averages, volatility, Sharpe/Sortino series, drawdown, and volume ratio.

## Metrics

`GET /api/metrics`

Returns the structured financial analytics summary under the `metrics` key.

Major sections include:

- `price`
- `performance`
- `risk_adjusted`
- `trend`
- `momentum`
- `risk`
- `volume`
- `dataset`

## Insights

`GET /api/insights`

Returns generated analytical observations derived from the metrics layer.

## Decision

`GET /api/decision`

Returns the explainable decision-support assessment, including market score, decision label, confidence, evidence, risk level, ML signal, prediction information, and model reliability.

## Prediction

`GET /api/prediction`

Returns the cached ML prediction used by the dashboard. Normal dashboard requests intentionally avoid loading TensorFlow inference; the application consumes the precomputed prediction cache.

## Error Contract

Successful JSON responses use an `error: false` field where implemented. Failed endpoints return an HTTP 500 status and a JSON object containing `error: true` and an explanatory `message`.

## Architecture Note

The application keeps TensorFlow inference outside the normal dashboard request path. Market analytics, metadata, and prediction cache data are loaded through cached application functions, reducing repeated expensive work during dashboard rendering.
