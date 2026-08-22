# Analytics Methodology

## Purpose

This document describes the deterministic analytics layer used by the Financial Market Analytics & Decision Intelligence Dashboard. The analytics layer is designed to be reusable by the Flask application, APIs, decision engine, and analytical notebooks.

## Data

The project works with OHLCV market data containing `Date`, `Open`, `High`, `Low`, `Close`, and `Volume` fields. Calculations are based only on observations available at or before each timestamp; no future observations are introduced into rolling features.

## Return Metrics

- 1-day, 5-day, and 20-day percentage returns measure short- and medium-term price movement.
- Cumulative return measures change from the first available close to the latest close.
- YTD return compares the first available observation in the latest calendar year with the latest observation.
- CAGR annualizes the total price growth using the actual calendar duration between the first and last observations.

## Trend Analytics

20-day, 50-day, and 200-day simple moving averages are calculated from historical closing prices. Price-to-moving-average distance is expressed as a percentage. The dashboard also records whether the latest price is above each moving average and summarizes the resulting trend state.

## Momentum

5-day and 20-day returns are used as momentum indicators. The decision layer treats materially positive 20-day momentum as supportive evidence and materially negative momentum as downside evidence.

## Volatility and Downside Risk

20-day rolling standard deviation of daily returns is used as short-term volatility. Annualized volatility scales daily dispersion by `sqrt(252)`. Downside volatility isolates negative observations for a downside-risk view.

## Risk-Adjusted Performance

### Sharpe Ratio

Annualized excess return divided by annualized return volatility. The configured risk-free rate is zero by default and can be supplied to the calculation function.

### Sortino Ratio

Annualized excess return divided by annualized downside deviation. It focuses on negative-return variability rather than total volatility.

### Calmar Ratio

CAGR divided by the absolute value of maximum historical drawdown. It relates annualized growth to observed drawdown risk.

## Drawdown

Running maximum close is calculated with `cummax()`. Drawdown is the percentage distance from the running maximum. Maximum drawdown is the minimum observed drawdown over the available history.

## Volume Analytics

A 20-day average volume and volume ratio are calculated. A ratio of 1.5 or greater is classified as a volume spike; ratios above 1.2 are treated as elevated activity by the decision layer.

## Performance Statistics

The analytics summary includes win rate, average gain, average loss, profit factor, average daily return, median daily return, best day, worst day, positive-day count, negative-day count, and observation count.

## Decision Intelligence

The decision engine combines technical evidence, momentum, risk, volume, ML prediction, and model reliability. The ML component is deliberately weighted by validation reliability rather than being allowed to dominate the decision.

The system is an analytical decision-support tool and must not be presented as financial advice or a guaranteed trading strategy.

## Reproducibility Principles

1. Keep source data versioned or otherwise traceable.
2. Keep model metadata alongside the model artifact.
3. Use deterministic feature calculations.
4. Validate generated outputs for JSON-safe numerical values.
5. Run the automated test suite before publishing changes.
