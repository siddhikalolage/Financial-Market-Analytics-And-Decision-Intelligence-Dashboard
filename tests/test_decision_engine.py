from analytics.decision_engine import (
    calculate_model_reliability,
    generate_decision,
)


def base_metrics():
    return {
        "price": {
            "daily_change_pct": -1.5,
        },
        "performance": {
            "return_20d": -7.5,
        },
        "trend": {
            "price_above_ma20": False,
            "price_above_ma50": False,
        },
        "risk": {
            "annualized_volatility": 27.0,
            "maximum_drawdown": -25.0,
        },
        "volume": {
            "ratio": 1.3,
        },
    }


def base_prediction():
    return {
        "current_close": 117.52,
        "predicted_next_close": 125.90,
        "predicted_change_percent": 7.13,
    }


def base_metadata():
    return {
        "model_mae": 15.4843,
        "baseline_mae": 2.0582,
        "model_r2": -17.3629,
        "baseline_r2": 0.6588,
    }


def test_low_reliability_when_model_underperforms_baseline():
    result = calculate_model_reliability(
        model_mae=15.4843,
        baseline_mae=2.0582,
        model_r2=-17.3629,
        baseline_r2=0.6588,
    )

    assert result["rating"] == "Low"
    assert result["score"] == 0.0
    assert result["model_mae"] > result["baseline_mae"]
    assert result["model_r2"] < result["baseline_r2"]


def test_reliable_model_receives_higher_score():
    result = calculate_model_reliability(
        model_mae=1.0,
        baseline_mae=2.0,
        model_r2=0.80,
        baseline_r2=0.65,
    )

    assert result["score"] > 50
    assert result["rating"] in {"Moderate", "High"}


def test_decision_contains_required_fields():
    result = generate_decision(
        base_metrics(),
        base_prediction(),
        base_metadata(),
    )

    required = {
        "decision",
        "decision_score",
        "confidence",
        "confidence_label",
        "market_score",
        "ml_signal",
        "ml_weight",
        "risk_score",
        "risk_level",
        "predicted_change_percent",
        "current_price",
        "predicted_price",
        "model_reliability",
        "evidence",
        "explanation",
        "ml_warning",
        "disclaimer",
    }

    assert required.issubset(result.keys())


def test_decision_scores_stay_within_valid_range():
    result = generate_decision(
        base_metrics(),
        base_prediction(),
        base_metadata(),
    )

    assert 0 <= result["decision_score"] <= 100
    assert 0 <= result["confidence"] <= 100
    assert 0 <= result["risk_score"] <= 100
    assert 0 <= result["ml_weight"] <= 1


def test_low_reliability_model_is_not_allowed_to_dominate():
    result = generate_decision(
        base_metrics(),
        base_prediction(),
        base_metadata(),
    )

    assert result["model_reliability"]["rating"] == "Low"
    assert result["ml_weight"] == 0
    assert "underperforms" in result["ml_warning"]


def test_decision_produces_evidence():
    result = generate_decision(
        base_metrics(),
        base_prediction(),
        base_metadata(),
    )

    assert isinstance(result["evidence"], list)
    assert len(result["evidence"]) >= 3

    for item in result["evidence"]:
        assert "type" in item
        assert "category" in item
        assert "message" in item
