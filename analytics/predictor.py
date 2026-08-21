"""
Production inference pipeline for the Financial Market Analytics dashboard.

Responsibilities:
- Load trained model artifacts
- Lazy-load TensorFlow only when ML inference is required
- Cache model artifacts in memory
- Load and validate market data
- Recreate training-time features
- Generate next-trading-day prediction
- Calculate prediction change
- Expose model metadata and diagnostics

Architecture:
- Flask application startup does NOT import TensorFlow.
- Model artifacts are loaded only when prediction is requested.
- Loaded artifacts remain cached in memory.
- Model metadata can be accessed without loading TensorFlow.

This improves application startup performance while preserving
the existing ML inference pipeline.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "stock_data.csv"
MODEL_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIR / "market_model.keras"
SCALER_PATH = MODEL_DIR / "feature_scaler.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


# ---------------------------------------------------------------------
# Feature configuration
# ---------------------------------------------------------------------

FEATURES = [
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


# ---------------------------------------------------------------------
# Lightweight metadata loading
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_metadata() -> dict[str, Any]:
    """
    Load model metadata without importing TensorFlow.

    This function is intentionally lightweight so that Flask health
    checks and model-information requests do not initialize the
    TensorFlow runtime.
    """

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {METADATA_PATH}"
        )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ---------------------------------------------------------------------
# Cached ML artifact loading
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_model_artifacts():
    """
    Load the trained TensorFlow model, scaler and metadata once.

    TensorFlow is imported INSIDE this function intentionally.

    Therefore:
        import app

    does not initialize TensorFlow.

    TensorFlow is initialized only when actual ML inference is needed.
    """

    # -------------------------------------------------------------
    # Import TensorFlow lazily.
    # -------------------------------------------------------------

    print("[ML] Initializing TensorFlow...")

    import tensorflow as tf

    # -------------------------------------------------------------
    # Validate model artifacts.
    # -------------------------------------------------------------

    missing = [
        path
        for path in [
            MODEL_PATH,
            SCALER_PATH,
            METADATA_PATH,
        ]
        if not path.exists()
    ]

    if missing:
        missing_names = ", ".join(
            str(path)
            for path in missing
        )

        raise FileNotFoundError(
            "Required model artifact(s) not found: "
            f"{missing_names}"
        )

    print("[ML] Loading model artifacts...")

    # -------------------------------------------------------------
    # Load trained neural network.
    # -------------------------------------------------------------

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False,
    )

    # -------------------------------------------------------------
    # Load feature scaler.
    # -------------------------------------------------------------

    scaler = joblib.load(
        SCALER_PATH
    )

    # -------------------------------------------------------------
    # Load metadata.
    # -------------------------------------------------------------

    metadata = load_metadata()

    print(
        "[ML] Model artifacts loaded successfully."
    )

    return model, scaler, metadata


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------

def load_market_data(
    data_path: Path = DATA_PATH,
) -> pd.DataFrame:
    """Load and validate the market dataset."""

    if not data_path.exists():
        raise FileNotFoundError(
            f"Market dataset not found: {data_path}"
        )

    df = pd.read_csv(
        data_path
    )

    required_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{missing_columns}"
        )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    if df["Date"].isna().any():
        raise ValueError(
            "Dataset contains invalid Date values."
        )

    df = (
        df
        .sort_values("Date")
        .drop_duplicates(
            subset=["Date"]
        )
        .reset_index(drop=True)
    )

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    if df[numeric_columns].isna().any().any():
        raise ValueError(
            "Dataset contains missing or invalid "
            "OHLCV values."
        )

    return df


# ---------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------

def engineer_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Recreate the exact features used during model training.
    """

    result = df.copy()

    # -------------------------------------------------------------
    # Returns
    # -------------------------------------------------------------

    result["Return_1D"] = (
        result["Close"].pct_change()
    )

    result["Return_5D"] = (
        result["Close"].pct_change(5)
    )

    result["Return_20D"] = (
        result["Close"].pct_change(20)
    )

    # -------------------------------------------------------------
    # Moving averages
    # -------------------------------------------------------------

    result["MA20"] = (
        result["Close"]
        .rolling(20)
        .mean()
    )

    result["MA50"] = (
        result["Close"]
        .rolling(50)
        .mean()
    )

    result["MA200"] = (
        result["Close"]
        .rolling(200)
        .mean()
    )

    # -------------------------------------------------------------
    # Volatility
    # -------------------------------------------------------------

    result["Rolling_Volatility_20D"] = (
        result["Return_1D"]
        .rolling(20)
        .std()
    )

    # -------------------------------------------------------------
    # Volume activity
    # -------------------------------------------------------------

    result["Average_Volume_20D"] = (
        result["Volume"]
        .rolling(20)
        .mean()
    )

    result["Volume_Ratio"] = (
        result["Volume"]
        / result["Average_Volume_20D"]
    )

    return result


# ---------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------

def predict_next_close(
    df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """
    Generate a next-trading-day closing-price prediction.

    TensorFlow is loaded only when this function actually needs
    to perform inference.

    Once loaded, the model and scaler remain cached in memory.
    """

    if df is None:
        df = load_market_data()

    # -------------------------------------------------------------
    # Feature engineering
    # -------------------------------------------------------------

    featured_df = engineer_features(
        df
    )

    # -------------------------------------------------------------
    # Remove rows where training features are unavailable.
    # -------------------------------------------------------------

    valid_rows = (
        featured_df
        .dropna(subset=FEATURES)
        .copy()
    )

    if valid_rows.empty:
        raise ValueError(
            "Not enough historical data to calculate "
            "model features."
        )

    latest = valid_rows.iloc[-1]

    # -------------------------------------------------------------
    # Prepare feature vector.
    # -------------------------------------------------------------

    feature_values = pd.DataFrame(
        [
            latest[
                FEATURES
            ].to_dict()
        ],
        columns=FEATURES,
    )

    # -------------------------------------------------------------
    # Load cached ML artifacts.
    #
    # TensorFlow initialization happens here, not at application
    # startup.
    # -------------------------------------------------------------

    model, scaler, metadata = (
        load_model_artifacts()
    )

    # -------------------------------------------------------------
    # Apply training-time scaler.
    # -------------------------------------------------------------

    scaled_features = (
        scaler.transform(
            feature_values
        )
    )

    # -------------------------------------------------------------
    # Generate prediction.
    # -------------------------------------------------------------

    prediction = model.predict(
        scaled_features,
        verbose=0,
    )

    predicted_close = float(
        np.asarray(
            prediction
        ).reshape(-1)[0]
    )

    current_close = float(
        latest["Close"]
    )

    # -------------------------------------------------------------
    # Calculate expected movement.
    # -------------------------------------------------------------

    predicted_change = (
        (
            predicted_close
            / current_close
        )
        - 1
    ) * 100

    # -------------------------------------------------------------
    # Direction classification.
    # -------------------------------------------------------------

    if predicted_change > 0.5:
        direction = "Bullish"

    elif predicted_change < -0.5:
        direction = "Bearish"

    else:
        direction = "Neutral"

    # -------------------------------------------------------------
    # Return complete prediction package.
    # -------------------------------------------------------------

    return {
        "date": latest[
            "Date"
        ].strftime("%Y-%m-%d"),

        "current_close": round(
            current_close,
            4,
        ),

        "predicted_next_close": round(
            predicted_close,
            4,
        ),

        "predicted_change_percent": round(
            predicted_change,
            4,
        ),

        "direction": direction,

        "model_type": metadata.get(
            "model_type",
            "Unknown",
        ),

        "target": metadata.get(
            "target",
            "next_trading_day_close",
        ),

        "feature_count": metadata.get(
            "feature_count",
            len(FEATURES),
        ),

        # ---------------------------------------------------------
        # Model evaluation metrics
        # ---------------------------------------------------------

        "training_samples": metadata.get(
            "training_samples"
        ),

        "testing_samples": metadata.get(
            "testing_samples"
        ),

        "model_mae": metadata.get(
            "model_mae"
        ),

        "model_rmse": metadata.get(
            "model_rmse"
        ),

        "model_r2": metadata.get(
            "model_r2"
        ),

        "baseline_mae": metadata.get(
            "baseline_mae"
        ),

        "baseline_rmse": metadata.get(
            "baseline_rmse"
        ),

        "baseline_r2": metadata.get(
            "baseline_r2"
        ),
    }


# ---------------------------------------------------------------------
# Model information
# ---------------------------------------------------------------------

def get_model_metadata() -> dict[str, Any]:
    """
    Return saved model metadata.

    IMPORTANT:
    This does NOT load TensorFlow or the Keras model.

    This keeps health checks and model-information requests fast.
    """

    return load_metadata()


# ---------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------

def clear_model_cache() -> None:
    """
    Clear cached model artifacts and metadata.

    Useful when replacing the trained model while the application
    is running.
    """

    load_model_artifacts.cache_clear()
    load_metadata.cache_clear()

    print(
        "[ML] Model artifact and metadata caches cleared."
    )


# ---------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------

if __name__ == "__main__":

    result = predict_next_close()

    print("=" * 60)
    print(
        "Financial Market ML Prediction"
    )
    print("=" * 60)

    for key, value in result.items():
        print(
            f"{key}: {value}"
        )