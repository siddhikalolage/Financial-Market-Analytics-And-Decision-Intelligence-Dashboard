from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200


def test_metrics_endpoint():
    client = app.test_client()
    response = client.get("/api/metrics")

    assert response.status_code == 200


def test_decision_endpoint():
    client = app.test_client()
    response = client.get("/api/decision")

    assert response.status_code == 200

    data = response.get_json()

    assert data is not None
    assert data.get("error") is False
    assert "decision" in data


def test_prediction_endpoint():
    client = app.test_client()
    response = client.get("/api/prediction")

    assert response.status_code == 200


def test_dashboard_endpoint():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert len(response.data) > 0
