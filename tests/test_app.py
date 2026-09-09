from app import app, load_data, build_metrics


def test_dataset_contract():
    df = load_data()
    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    assert required.issubset(df.columns)
    assert df["Date"].is_monotonic_increasing
    assert not df["Date"].duplicated().any()
    assert (df[["Open", "High", "Low", "Close", "Volume"]] >= 0).all().all()
    assert {"Daily_Return", "Daily_Return_Pct", "Cumulative_Return", "MA_20", "MA_50", "MA_200", "Drawdown", "Volume_Ratio"}.issubset(df.columns)
    assert (df["High"] >= df[["Open", "Close"]].max(axis=1)).all()
    assert (df["Low"] <= df[["Open", "Close"]].min(axis=1)).all()


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["observations"] >= 31
    assert payload["start_date"] <= payload["end_date"]


def test_metrics_endpoint_exposes_analyst_kpis():
    client = app.test_client()
    response = client.get("/api/metrics")
    assert response.status_code == 200
    payload = response.get_json()
    for key in [
        "last_close", "percent_change", "period_return", "return_5d", "return_20d",
        "ytd_return", "cagr", "annualized_volatility", "max_drawdown",
        "current_drawdown", "sharpe_ratio", "sortino_ratio", "profit_factor",
        "volume_ratio", "observations", "data_quality",
    ]:
        assert key in payload
    assert payload["observations"] >= 31
    assert payload["data_quality"]["missing_values"] == 0
    assert payload["data_quality"]["duplicate_dates"] == 0
    assert payload["data_quality"]["date_order_valid"] is True


def test_metrics_match_calculated_source():
    df = load_data()
    metrics = build_metrics(df)
    assert metrics["observations"] == len(df)
    assert metrics["last_close"] == round(float(df["Close"].iloc[-1]), 2)
    assert metrics["max_drawdown"] == round(float(df["Drawdown"].min() * 100), 2)


def test_data_endpoint():
    client = app.test_client()
    response = client.get("/api/data")
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert 1 <= len(payload) <= 90
    assert {
        "Date", "Close", "Daily_Return_Pct", "MA_20", "MA_50",
        "Rolling_Volatility_20D", "Volume_Ratio", "Drawdown", "Range_Pct",
    }.issubset(payload[-1])
