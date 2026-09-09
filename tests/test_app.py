import pandas as pd

from app import app, load_data


def test_dataset_contract():
    df = load_data()
    required = {'Date', 'Open', 'High', 'Low', 'Close', 'Volume'}
    assert required.issubset(df.columns)
    assert df['Date'].is_monotonic_increasing
    assert not df['Date'].duplicated().any()
    assert (df[['Open', 'High', 'Low', 'Close', 'Volume']] >= 0).all().all()
    assert {'Daily_Return', 'Cumulative_Return', 'MA_20', 'MA_50', 'Drawdown'}.issubset(df.columns)


def test_health_endpoint():
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_metrics_endpoint():
    client = app.test_client()
    response = client.get('/api/metrics')
    assert response.status_code == 200
    payload = response.get_json()
    for key in ['last_close', 'period_return', 'annualized_volatility', 'max_drawdown', 'observations']:
        assert key in payload
    assert payload['observations'] >= 31


def test_data_endpoint():
    client = app.test_client()
    response = client.get('/api/data')
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert 1 <= len(payload) <= 90
    assert {'Date', 'Close', 'Daily_Return', 'MA_20', 'MA_50'}.issubset(payload[-1])
