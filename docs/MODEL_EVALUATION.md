# Model Evaluation

## Prediction Task

The machine-learning component performs supervised regression to estimate the next-trading-day closing price.

### Target

`next_trading_day_close`

## Features

The model uses OHLCV and engineered time-series features including:

- Open
- High
- Low
- Close
- Volume
- 1-day return
- 5-day return
- 20-day return
- MA20
- MA50
- MA200
- Rolling volatility
- Volume ratio

## Validation Strategy

The dataset is split chronologically rather than randomly.

This preserves temporal ordering and prevents future observations from being introduced into the training set.

## Preprocessing

Features are scaled before model inference using the same saved preprocessing artifact used during training.

## Model

The project uses a neural-network regression model implemented with TensorFlow/Keras.

## Baseline

The model is compared against a persistence baseline:

`Predicted tomorrow price = Today's closing price`

This baseline is intentionally simple and provides a meaningful benchmark for determining whether the ML model adds predictive value.

## Evaluation Metrics

### MAE

Mean Absolute Error measures the average absolute difference between predicted and actual prices.

Lower is better.

### RMSE

Root Mean Squared Error penalizes larger prediction errors more strongly than MAE.

Lower is better.

### R²

R² measures how much variance in the target is explained by the model relative to the baseline mean.

Higher is better.

## Model Reliability

The decision engine compares model performance with the persistence baseline.

If the ML model does not outperform the baseline, the system can:

- Reduce ML influence
- Remove ML contribution from the decision score
- Display an explicit reliability warning

This prevents a weak predictive model from dominating the overall market decision.

## Current Model Interpretation

The model is treated as one analytical signal rather than a guaranteed forecasting mechanism.

Historical prediction performance does not guarantee future performance.

## Limitations

The current model does not include:

- Fundamental company data
- Macroeconomic variables
- News or sentiment
- Transaction costs
- Slippage
- Regime-specific modelling
- Walk-forward retraining

Future improvements can evaluate multiple algorithms and walk-forward validation.
