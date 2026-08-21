"""
Decision Intelligence Engine

Combines:
- Technical trend
- Momentum
- Volatility
- Drawdown
- Volume activity
- ML forecast
- ML model reliability

into an explainable analytical decision-support signal.

This system is NOT financial advice.
It is intended for research and analytical decision support.
"""

from __future__ import annotations

from typing import Any


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Keep a numeric value inside a defined range."""
    return max(minimum, min(value, maximum))


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_model_reliability(
    model_mae: float,
    baseline_mae: float,
    model_r2: float,
    baseline_r2: float,
) -> dict[str, Any]:
    """
    Evaluate ML model reliability against a persistence baseline.

    The model receives stronger influence only when validation
    performance justifies it.
    """

    model_mae = _safe_float(model_mae)
    baseline_mae = _safe_float(baseline_mae)
    model_r2 = _safe_float(model_r2)
    baseline_r2 = _safe_float(baseline_r2)

    if baseline_mae > 0:
        improvement = (
            (baseline_mae - model_mae)
            / baseline_mae
        ) * 100
    else:
        improvement = 0.0

    score = 50.0

    # MAE comparison
    if model_mae < baseline_mae:
        score += 25.0
    else:
        score -= 25.0

    # R² quality
    if model_r2 > 0:
        score += 15.0
    else:
        score -= 15.0

    # Comparison with baseline R²
    if model_r2 >= baseline_r2:
        score += 10.0
    else:
        score -= 10.0

    score = _clamp(score, 0.0, 100.0)

    if score >= 70:
        rating = "High"
    elif score >= 45:
        rating = "Moderate"
    else:
        rating = "Low"

    return {
        "score": round(score, 2),
        "rating": rating,
        "mae_improvement_vs_baseline_pct": round(
            improvement,
            2,
        ),
        "model_mae": round(model_mae, 4),
        "baseline_mae": round(baseline_mae, 4),
        "model_r2": round(model_r2, 4),
        "baseline_r2": round(baseline_r2, 4),
    }


def generate_decision(
    metrics: dict[str, Any],
    prediction: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate an explainable analytical decision-support assessment.

    Market analytics and ML predictions are evaluated separately
    before being combined. Weak ML models are deliberately prevented
    from dominating the final signal.
    """

    price = metrics.get("price", {})
    performance = metrics.get("performance", {})
    trend = metrics.get("trend", {})
    risk = metrics.get("risk", {})
    volume = metrics.get("volume", {})

    daily_change_pct = _safe_float(
        price.get("daily_change_pct")
    )

    return_20d = _safe_float(
        performance.get("return_20d")
    )

    volatility = _safe_float(
        risk.get("annualized_volatility")
    )

    max_drawdown = _safe_float(
        risk.get("maximum_drawdown")
    )

    current_price = _safe_float(
        prediction.get("current_close")
    )

    predicted_price = _safe_float(
        prediction.get("predicted_next_close")
    )

    predicted_change = _safe_float(
        prediction.get("predicted_change_percent")
    )

    # ============================================================
    # ML MODEL RELIABILITY
    # ============================================================

    reliability = calculate_model_reliability(
        model_mae=_safe_float(
            metadata.get("model_mae")
        ),
        baseline_mae=_safe_float(
            metadata.get("baseline_mae")
        ),
        model_r2=_safe_float(
            metadata.get("model_r2")
        ),
        baseline_r2=_safe_float(
            metadata.get("baseline_r2")
        ),
    )

    # ============================================================
    # MARKET EVIDENCE
    # ============================================================

    market_score = 50.0
    evidence = []

    # ------------------------------------------------------------
    # Daily movement
    # ------------------------------------------------------------

    if daily_change_pct > 1:
        market_score += 8

        evidence.append({
            "type": "positive",
            "category": "Daily Movement",
            "message": (
                "Recent daily price movement is positive."
            ),
        })

    elif daily_change_pct < -1:
        market_score -= 8

        evidence.append({
            "type": "negative",
            "category": "Daily Movement",
            "message": (
                "Recent daily price movement is negative."
            ),
        })

    # ------------------------------------------------------------
    # 20-day momentum
    # ------------------------------------------------------------

    if return_20d > 5:
        market_score += 15

        evidence.append({
            "type": "positive",
            "category": "Momentum",
            "message": (
                "20-day momentum is positive."
            ),
        })

    elif return_20d < -5:
        market_score -= 15

        evidence.append({
            "type": "negative",
            "category": "Momentum",
            "message": (
                "20-day momentum is negative."
            ),
        })

    else:
        evidence.append({
            "type": "neutral",
            "category": "Momentum",
            "message": (
                "20-day momentum is relatively neutral."
            ),
        })

    # ------------------------------------------------------------
    # Moving-average trend
    # ------------------------------------------------------------

    price_above_ma20 = trend.get(
        "price_above_ma20"
    )

    if price_above_ma20 is True:
        market_score += 12

        evidence.append({
            "type": "positive",
            "category": "Trend",
            "message": (
                "Price is trading above the 20-day "
                "moving average."
            ),
        })

    elif price_above_ma20 is False:
        market_score -= 12

        evidence.append({
            "type": "negative",
            "category": "Trend",
            "message": (
                "Price is trading below the 20-day "
                "moving average."
            ),
        })

    # ------------------------------------------------------------
    # MA50 confirmation
    # ------------------------------------------------------------

    price_above_ma50 = trend.get(
        "price_above_ma50"
    )

    if price_above_ma50 is True:
        market_score += 5

        evidence.append({
            "type": "positive",
            "category": "Trend",
            "message": (
                "Price remains above the 50-day "
                "moving average."
            ),
        })

    elif price_above_ma50 is False:
        market_score -= 5

        evidence.append({
            "type": "negative",
            "category": "Trend",
            "message": (
                "Price is below the 50-day "
                "moving average."
            ),
        })

    # ============================================================
    # VOLUME ANALYSIS
    # ============================================================

    volume_ratio = _safe_float(
        volume.get("ratio")
    )

    if volume_ratio >= 1.5:

        evidence.append({
            "type": "warning",
            "category": "Volume",
            "message": (
                "Trading activity is significantly "
                "above its recent average."
            ),
        })

    elif volume_ratio > 1.2:

        evidence.append({
            "type": "warning",
            "category": "Volume",
            "message": (
                "Trading activity is above its recent average."
            ),
        })

    elif volume_ratio < 0.8:

        evidence.append({
            "type": "neutral",
            "category": "Volume",
            "message": (
                "Trading activity is below its recent average."
            ),
        })

    # ============================================================
    # RISK SCORE
    # ============================================================

    risk_score = 20.0

    # Volatility
    if volatility >= 40:
        risk_score += 35
    elif volatility >= 25:
        risk_score += 20
    elif volatility >= 15:
        risk_score += 10

    # Maximum drawdown
    if max_drawdown <= -30:
        risk_score += 30
    elif max_drawdown <= -20:
        risk_score += 20
    elif max_drawdown <= -10:
        risk_score += 10

    risk_score = _clamp(
        risk_score,
        0,
        100,
    )

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 45:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # ============================================================
    # ML SIGNAL
    # ============================================================

    ml_weight = reliability["score"] / 100

    if predicted_change > 0.5:
        ml_signal = "Bullish"

    elif predicted_change < -0.5:
        ml_signal = "Bearish"

    else:
        ml_signal = "Neutral"

    # Weak ML models receive less influence.
    ml_contribution = (
        predicted_change
        * 2.0
        * ml_weight
    )

    combined_score = (
        market_score
        + ml_contribution
    )

    combined_score = _clamp(
        combined_score,
        0,
        100,
    )

    # ============================================================
    # FINAL DECISION
    # ============================================================

    if risk_level == "High":

        if combined_score >= 65:
            decision = "WATCH"
        else:
            decision = "AVOID"

    elif combined_score >= 65:
        decision = "BULLISH"

    elif combined_score <= 35:
        decision = "BEARISH"

    else:
        decision = "NEUTRAL"

    # ============================================================
    # CONFIDENCE
    # ============================================================

    market_confidence = abs(
        market_score - 50
    ) * 2

    agreement_penalty = 0

    if (
        ml_signal == "Bullish"
        and market_score < 50
    ):
        agreement_penalty = 20

    elif (
        ml_signal == "Bearish"
        and market_score > 50
    ):
        agreement_penalty = 20

    confidence = (
        40
        + market_confidence * 0.35
        + reliability["score"] * 0.25
        - agreement_penalty
        - risk_score * 0.15
    )

    confidence = _clamp(
        confidence,
        0,
        100,
    )

    if confidence >= 70:
        confidence_label = "High"

    elif confidence >= 45:
        confidence_label = "Moderate"

    else:
        confidence_label = "Low"

    # ============================================================
    # EXPLANATION
    # ============================================================

    if decision == "BULLISH":

        explanation = (
            "Market evidence currently supports a positive "
            "directional signal. The result should be interpreted "
            "alongside model reliability and market risk."
        )

    elif decision == "BEARISH":

        explanation = (
            "Market evidence currently indicates downside pressure. "
            "Negative momentum and trend conditions outweigh "
            "positive signals."
        )

    elif decision == "WATCH":

        explanation = (
            "The market contains potentially positive evidence, "
            "but elevated risk or conflicting signals reduce "
            "decision confidence."
        )

    elif decision == "AVOID":

        explanation = (
            "Downside pressure combined with elevated risk "
            "reduces the strength of the current analytical setup."
        )

    else:

        explanation = (
            "Market signals are mixed and do not provide enough "
            "evidence for a strong directional conclusion."
        )

    # ============================================================
    # ML WARNING
    # ============================================================

    if reliability["rating"] == "Low":

        ml_warning = (
            "ML reliability is low because the model currently "
            "underperforms the persistence baseline."
        )

    elif reliability["rating"] == "Moderate":

        ml_warning = (
            "ML reliability is moderate. The model should be "
            "treated as supporting evidence rather than a "
            "standalone signal."
        )

    else:

        ml_warning = (
            "ML validation indicates sufficient reliability for "
            "the model to contribute meaningfully to the signal."
        )

    return {
        "decision": decision,

        "decision_score": round(
            combined_score,
            2,
        ),

        "confidence": round(
            confidence,
            2,
        ),

        "confidence_label": confidence_label,

        "market_score": round(
            market_score,
            2,
        ),

        "ml_signal": ml_signal,

        "ml_weight": round(
            ml_weight,
            3,
        ),

        "risk_score": round(
            risk_score,
            2,
        ),

        "risk_level": risk_level,

        "predicted_change_percent": round(
            predicted_change,
            2,
        ),

        "current_price": round(
            current_price,
            2,
        ),

        "predicted_price": round(
            predicted_price,
            2,
        ),

        "model_reliability": reliability,

        "evidence": evidence,

        "explanation": explanation,

        "ml_warning": ml_warning,

        "disclaimer": (
            "This system provides analytical decision support "
            "for research purposes and is not financial advice."
        ),
    }
