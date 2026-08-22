import json
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = ROOT / "notebook"
OUTPUT = NOTEBOOK_DIR / "analysis_and_prediction.ipynb"

NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)

nb = nbf.v4.new_notebook()

cells = []


def markdown(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


# ============================================================
# 1. TITLE
# ============================================================

markdown("""# Financial Market Analytics & Decision Intelligence

## Stock Market Data Analysis and Prediction

This notebook performs exploratory data analysis, financial feature engineering,
baseline comparison, machine-learning modelling, and prediction evaluation.

> **Important:** This project is for analytical and educational purposes.
> Market predictions are inherently uncertain and should not be treated as
> financial advice.
""")


# ============================================================
# 2. OBJECTIVES
# ============================================================

markdown("""## 1. Objectives

The analysis focuses on:

- Understanding historical OHLCV market behaviour
- Performing data-quality validation
- Engineering financial time-series features
- Establishing a simple baseline
- Training a neural-network regression model
- Evaluating prediction performance
- Comparing actual and predicted prices
- Preparing the model for integration with the Flask dashboard
""")


# ============================================================
# 3. IMPORTS
# ============================================================

markdown("## 2. Import Libraries")

code("""import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Input

print("TensorFlow version:", tf.__version__)
""")


# ============================================================
# 4. LOAD DATA
# ============================================================

markdown("## 3. Load Dataset")

code("""DATA_PATH = "../data/stock_data.csv"

df = pd.read_csv(DATA_PATH)

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date").reset_index(drop=True)

print("Dataset shape:", df.shape)
df.head()
""")


# ============================================================
# 5. DATA INFORMATION
# ============================================================

markdown("## 4. Dataset Overview")

code("""print("Rows:", len(df))
print("Columns:", list(df.columns))

print("\\nData types:")
display(df.dtypes)

print("\\nMissing values:")
display(df.isna().sum())
""")


# ============================================================
# 6. STATISTICS
# ============================================================

markdown("## 5. Descriptive Statistics")

code("""df.describe().T
""")


# ============================================================
# 7. PRICE HISTORY
# ============================================================

markdown("## 6. Closing Price History")

code("""plt.figure(figsize=(14, 6))

plt.plot(df["Date"], df["Close"])

plt.title("Historical Closing Price")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
""")


# ============================================================
# 8. VOLUME
# ============================================================

markdown("## 7. Trading Volume")

code("""plt.figure(figsize=(14, 5))

plt.plot(df["Date"], df["Volume"])

plt.title("Historical Trading Volume")
plt.xlabel("Date")
plt.ylabel("Volume")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
""")


# ============================================================
# 9. RETURNS
# ============================================================

markdown("## 8. Return Feature Engineering")

code("""df["Return_1D"] = df["Close"].pct_change()
df["Return_5D"] = df["Close"].pct_change(5)
df["Return_20D"] = df["Close"].pct_change(20)

df[[
    "Date",
    "Close",
    "Return_1D",
    "Return_5D",
    "Return_20D"
]].tail()
""")


# ============================================================
# 10. MOVING AVERAGES
# ============================================================

markdown("## 9. Moving Average Features")

code("""df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()
df["MA200"] = df["Close"].rolling(200).mean()

plt.figure(figsize=(14, 7))

plt.plot(df["Date"], df["Close"], label="Close")
plt.plot(df["Date"], df["MA20"], label="MA20")
plt.plot(df["Date"], df["MA50"], label="MA50")
plt.plot(df["Date"], df["MA200"], label="MA200")

plt.title("Price and Moving Averages")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
""")


# ============================================================
# 11. VOLATILITY
# ============================================================

markdown("## 10. Volatility Analysis")

code("""df["Rolling_Volatility_20D"] = (
    df["Return_1D"]
    .rolling(20)
    .std()
)

df["Annualized_Volatility"] = (
    df["Rolling_Volatility_20D"]
    * np.sqrt(252)
)

df[[
    "Date",
    "Rolling_Volatility_20D",
    "Annualized_Volatility"
]].tail()
""")


# ============================================================
# 12. DRAWDOWN
# ============================================================

markdown("## 11. Drawdown Analysis")

code("""running_max = df["Close"].cummax()

df["Drawdown"] = (
    (df["Close"] - running_max)
    / running_max
)

maximum_drawdown = df["Drawdown"].min()

print(
    f"Maximum historical drawdown: "
    f"{maximum_drawdown * 100:.2f}%"
)
""")


# ============================================================
# 13. VOLUME RATIO
# ============================================================

markdown("## 12. Volume Activity")

code("""df["Average_Volume_20D"] = (
    df["Volume"]
    .rolling(20)
    .mean()
)

df["Volume_Ratio"] = (
    df["Volume"]
    / df["Average_Volume_20D"]
)

df[[
    "Date",
    "Volume",
    "Average_Volume_20D",
    "Volume_Ratio"
]].tail()
""")


# ============================================================
# 14. TARGET
# ============================================================

markdown("""## 13. Prediction Target

The target is the **next trading day's closing price**.

The target is shifted by one observation so that today's market information
is used to estimate tomorrow's close.
""")

code("""df["Target"] = df["Close"].shift(-1)

model_df = df.dropna().copy()

print("Model dataset shape:", model_df.shape)
""")


# ============================================================
# 15. FEATURES
# ============================================================

markdown("## 14. Model Features")

code("""FEATURES = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Return_1D",
    "Return_5D",
    "Return_20D",
    "MA20",
    "MA50",
    "MA200",
    "Rolling_Volatility_20D",
    "Volume_Ratio",
]

model_df = model_df.dropna(
    subset=FEATURES + ["Target"]
).copy()

X = model_df[FEATURES]
y = model_df["Target"]

print("Features:", FEATURES)
print("X shape:", X.shape)
print("y shape:", y.shape)
""")


# ============================================================
# 16. CHRONOLOGICAL SPLIT
# ============================================================

markdown("""## 15. Chronological Train/Test Split

Financial time-series data must preserve temporal order.

A random train/test split can introduce future information into the training
process, so the data is split chronologically.
""")

code("""split_index = int(len(model_df) * 0.8)

X_train = X.iloc[:split_index].copy()
X_test = X.iloc[split_index:].copy()

y_train = y.iloc[:split_index].copy()
y_test = y.iloc[split_index:].copy()

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
""")


# ============================================================
# 17. SCALING
# ============================================================

markdown("## 16. Feature Scaling")

code("""scaler = MinMaxScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.transform(X_test)

print("Training data scaled.")
print("Test data transformed using the training scaler.")
""")


# ============================================================
# 18. BASELINE
# ============================================================

markdown("## 17. Naive Baseline")

code("""baseline_predictions = X_test["Close"].values

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)

baseline_r2 = r2_score(
    y_test,
    baseline_predictions
)

print(f"Baseline MAE:  {baseline_mae:.4f}")
print(f"Baseline RMSE: {baseline_rmse:.4f}")
print(f"Baseline R²:   {baseline_r2:.4f}")
""")


# ============================================================
# 19. MODEL
# ============================================================

markdown("## 18. Neural Network Regression Model")

code("""tf.random.set_seed(42)
np.random.seed(42)

model = Sequential([
    Input(shape=(X_train_scaled.shape[1],)),
    Dense(64, activation="relu"),
    Dense(32, activation="relu"),
    Dense(16, activation="relu"),
    Dense(1)
])

model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)

model.summary()
""")


# ============================================================
# 20. TRAIN
# ============================================================

markdown("## 19. Model Training")

code("""history = model.fit(
    X_train_scaled,
    y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    shuffle=False,
    verbose=1
)
""")


# ============================================================
# 21. TRAINING CURVE
# ============================================================

markdown("## 20. Training History")

code("""plt.figure(figsize=(12, 5))

plt.plot(
    history.history["loss"],
    label="Training Loss"
)

plt.plot(
    history.history["val_loss"],
    label="Validation Loss"
)

plt.title("Training and Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
plt.legend()
plt.tight_layout()
plt.show()
""")


# ============================================================
# 22. PREDICTION
# ============================================================

markdown("## 21. Generate Predictions")

code("""predictions = model.predict(
    X_test_scaled,
    verbose=0
).flatten()

print("Predictions generated:", len(predictions))
""")


# ============================================================
# 23. EVALUATION
# ============================================================

markdown("## 22. Model Evaluation")

code("""mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)

print(f"Neural Network MAE:  {mae:.4f}")
print(f"Neural Network RMSE: {rmse:.4f}")
print(f"Neural Network R²:   {r2:.4f}")
""")


# ============================================================
# 24. COMPARISON
# ============================================================

markdown("## 23. Baseline vs Neural Network")

code("""comparison = pd.DataFrame({
    "Model": [
        "Naive Baseline",
        "Neural Network"
    ],
    "MAE": [
        baseline_mae,
        mae
    ],
    "RMSE": [
        baseline_rmse,
        rmse
    ],
    "R2": [
        baseline_r2,
        r2
    ]
})

comparison
""")


# ============================================================
# 25. ACTUAL VS PREDICTED
# ============================================================

markdown("## 24. Actual vs Predicted Prices")

code("""plt.figure(figsize=(14, 6))

plt.plot(
    y_test.values,
    label="Actual"
)

plt.plot(
    predictions,
    label="Predicted"
)

plt.title("Actual vs Predicted Closing Price")
plt.xlabel("Test Observation")
plt.ylabel("Closing Price")
plt.legend()
plt.tight_layout()
plt.show()
""")


# ============================================================
# 26. PREDICTION ERROR
# ============================================================

markdown("## 25. Prediction Error Analysis")

code("""errors = y_test.values - predictions

plt.figure(figsize=(14, 5))

plt.plot(errors)

plt.axhline(
    0,
    linestyle="--"
)

plt.title("Prediction Errors")
plt.xlabel("Test Observation")
plt.ylabel("Actual - Predicted")
plt.tight_layout()
plt.show()
""")


# ============================================================
# 27. ERROR STATISTICS
# ============================================================

markdown("## 26. Error Statistics")

code("""error_summary = pd.Series(errors).describe()

error_summary
""")


# ============================================================
# 28. LATEST PREDICTION
# ============================================================

markdown("## 27. Latest Next-Day Prediction")

code("""latest_features = X.iloc[[-1]]

latest_scaled = scaler.transform(
    latest_features
)

next_day_prediction = float(
    model.predict(
        latest_scaled,
        verbose=0
    )[0][0]
)

current_price = float(
    df["Close"].iloc[-1]
)

predicted_change = (
    (next_day_prediction / current_price) - 1
) * 100

print(f"Current close: {current_price:.2f}")
print(
    f"Predicted next close: "
    f"{next_day_prediction:.2f}"
)
print(
    f"Predicted change: "
    f"{predicted_change:.2f}%"
)
""")


# ============================================================
# 29. MODEL LIMITATIONS
# ============================================================

markdown("""## 28. Model Limitations

This model should be interpreted as an analytical experiment rather than a
reliable trading system.

Important limitations include:

- Financial markets are highly non-stationary.
- Historical OHLCV data does not capture all market information.
- News, macroeconomic events, sentiment, and liquidity can affect prices.
- Regression accuracy does not imply profitable trading performance.
- The model predicts price levels rather than actual trading returns.
- Longer-horizon forecasts accumulate uncertainty.
""")


# ============================================================
# 30. CONCLUSION
# ============================================================

markdown("""## 29. Conclusion

The analysis establishes a complete machine-learning workflow:

**Data → Validation → Feature Engineering → Chronological Split → Scaling →
Baseline → Neural Network → Evaluation → Error Analysis**

The resulting model can serve as the machine-learning component of the Flask
Financial Market Analytics and Decision Intelligence Dashboard.
""")


# ============================================================
# CREATE NOTEBOOK
# ============================================================

nb["cells"] = cells

nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.10",
    },
}

nb["nbformat"] = 4
nb["nbformat_minor"] = 5

with open(OUTPUT, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Created valid Jupyter notebook: {OUTPUT}")
print(f"Cells created: {len(nb['cells'])}")
print(f"Code cells: {sum(c.cell_type == 'code' for c in nb['cells'])}")