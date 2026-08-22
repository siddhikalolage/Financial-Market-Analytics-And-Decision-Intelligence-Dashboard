import app as app_module
from app import app


TEST_PREDICTION = {
    "date": "2026-01-02",
    "current_close": 117.52,
    "predicted_next_close": 120.10,
    "predicted_change_percent": 2.1954,
    "direction": "Bullish",
    "model_type": "TestModel",
    "target": "next_trading_day_close",
    "feature_count": 14,
    "training_samples": 1000,
    "testing_samples": 200,
    "model_mae": 1.5,
    "model_rmse": 2.0,
    "model_r2": 0.75,
    "baseline_mae": 2.0,
    "baseline_rmse": 2.5,
    "baseline_r2": 0.65,
}


TEST_METADATA = {
    "model_type": "TestModel",
    "target": "next_trading_day_close",
    "feature_count": 14,
    "training_samples": 1000,
    "testing_samples": 200,
    "model_mae": 1.5,
    "model_rmse": 2.0,
    "model_r2": 0.75,
    "baseline_mae": 2.0,
    "baseline_rmse": 2.5,
    "baseline_r2": 0.65,
}


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200


def test_metrics_endpoint(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "load_cached_prediction",
        lambda: TEST_PREDICTION,
    )
    monkeypatch.setattr(
        app_module,
        "load_cached_model_metadata",
        lambda: TEST_METADATA,
    )

    client = app.test_client()
    response = client.get("/api/metrics")

    assert response.status_code == 200


def test_decision_endpoint(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "load_cached_prediction",
        lambda: TEST_PREDICTION,
    )
    monkeypatch.setattr(
        app_module,
        "load_cached_model_metadata",
        lambda: TEST_METADATA,
    )

    client = app.test_client()
    response = client.get("/api/decision")

    assert response.status_code == 200

    data = response.get_json()

    assert data is not None
    assert data.get("error") is False
    assert "decision" in data


def test_prediction_endpoint(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "load_cached_prediction",
        lambda: TEST_PREDICTION,
    )

    client = app.test_client()
    response = client.get("/api/prediction")

    assert response.status_code == 200


def test_dashboard_endpoint(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "load_cached_prediction",
        lambda: TEST_PREDICTION,
    )
    monkeypatch.setattr(
        app_module,
        "load_cached_model_metadata",
        lambda: TEST_METADATA,
    )

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert len(response.data) > 0