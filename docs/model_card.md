# Model Card

## Model Purpose

The machine-learning component estimates the next close from engineered historical market features. Its output is used as one input to an explainable analytical decision-support layer.

## Intended Use

- Research and analytical exploration
- Demonstrating model evaluation and decision-intelligence integration
- Supporting dashboard scenario analysis

## Out of Scope

- Financial advice
- Guaranteed price forecasts
- Autonomous trading
- Claims that the ML model outperforms a market baseline without current validation evidence

## Evaluation

The repository compares the ML model against a persistence baseline. The current stored evaluation indicates that the model does **not** outperform the baseline and therefore receives reduced influence in the decision engine.

Current recorded evaluation:

| Metric | Model | Persistence baseline |
|---|---:|---:|
| MAE | 15.4843 | 2.0582 |
| R² | -17.3629 | 0.6588 |

The negative model R² indicates that the current model performs substantially worse than the baseline on the recorded validation data. This limitation is intentionally surfaced rather than hidden.

## Reliability Handling

The decision engine calculates a reliability score from MAE and R² comparisons. When the model underperforms the baseline, its contribution is reduced. This prevents a weak predictive model from overpowering deterministic market evidence.

## Features

The project uses engineered historical market features rather than raw price alone. The exact feature set is tracked in the model metadata and should be treated as versioned model configuration.

## Limitations

- The current validation result is weak.
- Historical market relationships can change over time.
- A two-year historical dataset is not sufficient evidence for broad generalization.
- Price prediction is sensitive to regime changes and data quality.
- Validation performance should be rechecked whenever data, features, model architecture, or training procedure changes.

## Responsible Interpretation

A model output should be interpreted together with its reliability rating, deterministic market evidence, and risk indicators. The dashboard is designed to demonstrate model-aware analytical decision support, not to make investment recommendations.
