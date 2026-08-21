"""
Financial Market Analytics & Decision Intelligence Dashboard

Application architecture:

Presentation
    ↓
Flask routes
    ↓
Cached analytics layer
    ├── Market data
    ├── Technical metrics
    ├── Market insights
    ├── Cached ML prediction
    └── Decision Intelligence

TensorFlow inference is intentionally isolated from
normal dashboard requests.

The ML model is executed only when a prediction is
explicitly regenerated.

This system is for analytical research and decision
support only. It is not financial advice.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from flask import Flask, jsonify, render_template

from analytics.data_loader import (
    DataValidationError,
    load_stock_data,
)

from analytics.insights import generate_insights

from analytics.metrics import (
    calculate_metrics,
    prepare_chart_data,
)

from analytics.decision_engine import (
    generate_decision,
)


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "stock_data.csv"
)

MODELS_DIR = (
    BASE_DIR
    / "models"
)

METADATA_PATH = (
    MODELS_DIR
    / "model_metadata.json"
)

CACHE_DIR = (
    BASE_DIR
    / "cache"
)

PREDICTION_CACHE_PATH = (
    CACHE_DIR
    / "prediction.json"
)

app = Flask(__name__)


# ============================================================
# FILE HELPERS
# ============================================================

@lru_cache(maxsize=1)
def load_cached_prediction() -> dict:
    """
    Load the precomputed ML prediction from disk.

    IMPORTANT:
    This function does NOT import TensorFlow.

    The prediction is generated separately and stored in
    cache/prediction.json.

    This makes normal dashboard requests extremely fast.
    """

    if not PREDICTION_CACHE_PATH.exists():

        raise FileNotFoundError(
            "ML prediction cache not found. "
            "Generate it using the prediction refresh command."
        )

    try:

        with open(
            PREDICTION_CACHE_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            prediction = json.load(file)

    except json.JSONDecodeError as exc:

        raise ValueError(
            "ML prediction cache contains invalid JSON."
        ) from exc

    if not isinstance(
        prediction,
        dict,
    ):

        raise ValueError(
            "ML prediction cache has an invalid structure."
        )

    return prediction


@lru_cache(maxsize=1)
def load_cached_model_metadata() -> dict:
    """
    Read model metadata directly from JSON.

    This deliberately avoids importing the TensorFlow
    prediction pipeline.

    Metadata is lightweight and does not require the
    neural network to be loaded.
    """

    if not METADATA_PATH.exists():

        raise FileNotFoundError(
            "Model metadata file not found."
        )

    try:

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            metadata = json.load(file)

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Model metadata contains invalid JSON."
        ) from exc

    if not isinstance(
        metadata,
        dict,
    ):

        raise ValueError(
            "Model metadata has an invalid structure."
        )

    return metadata


# ============================================================
# CACHED DATA LAYER
# ============================================================

@lru_cache(maxsize=1)
def load_cached_data():
    """
    Load and cache validated market data.

    The dataset is static during normal dashboard operation,
    so there is no reason to reload the CSV for every request.
    """

    return load_stock_data(
        DATA_PATH
    )


@lru_cache(maxsize=1)
def get_cached_dashboard_data():
    """
    Build the complete dashboard intelligence layer.

    Normal dashboard requests perform only lightweight
    analytics.

    TensorFlow inference is NOT executed here.

    ML prediction is loaded from the precomputed cache.
    """

    df = load_cached_data()

    # --------------------------------------------------------
    # MARKET ANALYTICS
    # --------------------------------------------------------

    metrics = calculate_metrics(
        df
    )

    chart_data = prepare_chart_data(
        df,
        periods=120,
    )

    insights = generate_insights(
        metrics
    )

    # --------------------------------------------------------
    # ML PREDICTION
    # --------------------------------------------------------

    prediction = load_cached_prediction()

    # --------------------------------------------------------
    # MODEL METADATA
    # --------------------------------------------------------

    metadata = load_cached_model_metadata()

    # --------------------------------------------------------
    # DECISION INTELLIGENCE
    # --------------------------------------------------------

    decision = generate_decision(
        metrics=metrics,
        prediction=prediction,
        metadata=metadata,
    )

    return {
        "df": df,
        "metrics": metrics,
        "chart_data": chart_data,
        "insights": insights,
        "prediction": prediction,
        "metadata": metadata,
        "decision": decision,
    }


# ============================================================
# CACHE MANAGEMENT
# ============================================================

def clear_dashboard_cache():
    """
    Clear lightweight dashboard caches.

    This does not execute TensorFlow.
    """

    load_cached_data.cache_clear()

    load_cached_prediction.cache_clear()

    load_cached_model_metadata.cache_clear()

    get_cached_dashboard_data.cache_clear()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():
    """
    Render the main Financial Market Analytics dashboard.
    """

    try:

        dashboard = (
            get_cached_dashboard_data()
        )

        df = dashboard["df"]

        metrics = dashboard[
            "metrics"
        ]

        chart_data = dashboard[
            "chart_data"
        ]

        insights = dashboard[
            "insights"
        ]

        prediction = dashboard[
            "prediction"
        ]

        decision = dashboard[
            "decision"
        ]

        daily_change = metrics[
            "price"
        ]["daily_change"]

        if daily_change > 0:

            trend = "UP"
            trend_color = "green"

        elif daily_change < 0:

            trend = "DOWN"
            trend_color = "red"

        else:

            trend = "FLAT"
            trend_color = "gray"

        return render_template(
            "index.html",

            # ------------------------------------------------
            # PRICE
            # ------------------------------------------------

            last_close=metrics[
                "price"
            ]["current"],

            price_change=daily_change,

            percent_change=metrics[
                "price"
            ]["daily_change_pct"],

            # ------------------------------------------------
            # TREND
            # ------------------------------------------------

            trend=trend,

            trend_color=trend_color,

            # ------------------------------------------------
            # VOLUME
            # ------------------------------------------------

            avg_volume=metrics[
                "volume"
            ]["average_20d"],

            # ------------------------------------------------
            # CHARTS
            # ------------------------------------------------

            chart_data=chart_data,

            # ------------------------------------------------
            # ML PREDICTION
            # ------------------------------------------------

            predictions=[
                prediction[
                    "predicted_next_close"
                ]
            ],

            prediction=prediction,

            # ------------------------------------------------
            # ANALYTICS
            # ------------------------------------------------

            metrics=metrics,

            insights=insights,

            # ------------------------------------------------
            # DECISION INTELLIGENCE
            # ------------------------------------------------

            decision=decision,

            # ------------------------------------------------
            # DATASET
            # ------------------------------------------------

            data_rows=len(df),

        )

    except (
        FileNotFoundError,
        DataValidationError,
        ValueError,
    ) as exc:

        return render_template(
            "index.html",
            error=str(exc),
        ), 500

    except Exception:

        app.logger.exception(
            "Unexpected dashboard error."
        )

        return render_template(
            "index.html",
            error=(
                "Unable to load the "
                "financial dashboard."
            ),
        ), 500


# ============================================================
# HISTORICAL DATA API
# ============================================================

@app.route("/api/data")
def api_data():

    try:

        dashboard = (
            get_cached_dashboard_data()
        )

        return jsonify(
            dashboard[
                "chart_data"
            ]
        )

    except Exception as exc:

        app.logger.exception(
            "Unexpected error in /api/data."
        )

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# METRICS API
# ============================================================

@app.route("/api/metrics")
def api_metrics():

    try:

        dashboard = (
            get_cached_dashboard_data()
        )

        return jsonify({
            "error": False,
            "metrics": dashboard[
                "metrics"
            ],
        })

    except Exception as exc:

        app.logger.exception(
            "Unexpected error in /api/metrics."
        )

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# INSIGHTS API
# ============================================================

@app.route("/api/insights")
def api_insights():

    try:

        dashboard = (
            get_cached_dashboard_data()
        )

        return jsonify({
            "error": False,
            "insights": dashboard[
                "insights"
            ],
        })

    except Exception as exc:

        app.logger.exception(
            "Unexpected error in /api/insights."
        )

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# ML PREDICTION API
# ============================================================

@app.route("/api/prediction")
def api_prediction():

    try:

        prediction = (
            load_cached_prediction()
        )

        return jsonify({
            "error": False,

            "model": prediction.get(
                "model_type"
            ),

            "prediction": prediction,

            "source": (
                "precomputed_ml_cache"
            ),
        })

    except Exception as exc:

        app.logger.exception(
            "Unexpected error in "
            "/api/prediction."
        )

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# DECISION INTELLIGENCE API
# ============================================================

@app.route("/api/decision")
def api_decision():

    try:

        dashboard = (
            get_cached_dashboard_data()
        )

        return jsonify({
            "error": False,
            "decision": dashboard[
                "decision"
            ],
        })

    except Exception as exc:

        app.logger.exception(
            "Unexpected error in "
            "/api/decision."
        )

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# MODEL INFORMATION API
# ============================================================

@app.route("/api/model")
def api_model():

    try:

        metadata = (
            load_cached_model_metadata()
        )

        return jsonify({
            "error": False,
            "model": metadata,
        })

    except Exception as exc:

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# ML PREDICTION REFRESH
# ============================================================

@app.route(
    "/api/prediction/refresh",
    methods=["POST"],
)
def api_prediction_refresh():
    """
    Explicitly regenerate the ML prediction.

    TensorFlow is imported only inside this route.

    Therefore normal dashboard startup remains lightweight.
    """

    try:

        # ----------------------------------------------------
        # IMPORTANT:
        # TensorFlow is intentionally imported lazily.
        # ----------------------------------------------------

        from analytics.predictor import (
            predict_next_close,
        )

        prediction = (
            predict_next_close()
        )

        CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            PREDICTION_CACHE_PATH,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                prediction,
                file,
                indent=4,
            )

        # Refresh lightweight caches.

        load_cached_prediction.cache_clear()

        get_cached_dashboard_data.cache_clear()

        return jsonify({
            "error": False,

            "message": (
                "ML prediction regenerated "
                "successfully."
            ),

            "prediction": prediction,

            "source": (
                "fresh_tensorflow_inference"
            ),
        })

    except Exception as exc:

        app.logger.exception(
            "Unable to regenerate ML prediction."
        )

        return jsonify({
            "error": True,
            "message": str(exc),
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():

    try:

        df = load_cached_data()

        metadata = (
            load_cached_model_metadata()
        )

        prediction_available = (
            PREDICTION_CACHE_PATH.exists()
        )

        return jsonify({

            "status": "healthy",

            "data_loaded": True,

            "row_count": len(df),

            "latest_date": (
                df["Date"]
                .max()
                .strftime("%Y-%m-%d")
            ),

            "ml_model_available": (
                prediction_available
            ),

            "ml_prediction_cached": (
                prediction_available
            ),

            "model_type": metadata.get(
                "model_type"
            ),

            "model_target": metadata.get(
                "target"
            ),

            "decision_engine_available": True,

            "cache_enabled": True,

            "tensorflow_loaded_on_request": (
                False
            ),

        })

    except Exception as exc:

        return jsonify({

            "status": "unhealthy",

            "data_loaded": False,

            "ml_model_available": False,

            "decision_engine_available": False,

            "message": str(exc),

        }), 500


# ============================================================
# CACHE RESET API
# ============================================================

@app.route(
    "/api/cache/clear",
    methods=["POST"],
)
def api_clear_cache():

    try:

        clear_dashboard_cache()

        return jsonify({

            "error": False,

            "message": (
                "Dashboard analytical "
                "cache cleared."
            ),

        })

    except Exception as exc:

        return jsonify({

            "error": True,

            "message": str(exc),

        }), 500


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    # IMPORTANT:
    #
    # TensorFlow is NOT imported during application startup.
    #
    # The Flask development reloader is disabled so the
    # application is not initialized twice.

    app.run(
        debug=False,
        use_reloader=False,
        host="0.0.0.0",
        port=5000,
    )