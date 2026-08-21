def generate_insights(metrics: dict) -> list[dict]:
    """
    Generate deterministic, neutral analytical insights.

    These are analytical observations, not investment recommendations.
    """

    insights = []

    price = metrics["price"]
    performance = metrics["performance"]
    trend = metrics["trend"]
    risk = metrics["risk"]
    volume = metrics["volume"]

    # -----------------------------
    # Momentum
    # -----------------------------

    return_20d = performance.get("return_20d")

    if return_20d is not None:
        if return_20d >= 5:
            insights.append({
                "category": "Momentum",
                "severity": "positive",
                "title": "Strong positive momentum",
                "message": (
                    f"The asset gained {return_20d:.2f}% "
                    "over the last 20 trading days."
                ),
            })
        elif return_20d <= -5:
            insights.append({
                "category": "Momentum",
                "severity": "negative",
                "title": "Negative momentum",
                "message": (
                    f"The asset declined {abs(return_20d):.2f}% "
                    "over the last 20 trading days."
                ),
            })
        else:
            insights.append({
                "category": "Momentum",
                "severity": "neutral",
                "title": "Moderate momentum",
                "message": (
                    f"The 20-day return is {return_20d:.2f}%, "
                    "indicating relatively moderate price movement."
                ),
            })

    # -----------------------------
    # Moving-average trend
    # -----------------------------

    if trend["price_above_ma20"] is True:
        insights.append({
            "category": "Trend",
            "severity": "positive",
            "title": "Price above MA20",
            "message": (
                "The latest closing price is above its "
                "20-day moving average."
            ),
        })
    elif trend["price_above_ma20"] is False:
        insights.append({
            "category": "Trend",
            "severity": "negative",
            "title": "Price below MA20",
            "message": (
                "The latest closing price is below its "
                "20-day moving average."
            ),
        })

    if trend["price_above_ma50"] is True:
        insights.append({
            "category": "Trend",
            "severity": "positive",
            "title": "Price above MA50",
            "message": (
                "The price remains above the 50-day moving average, "
                "supporting a positive medium-term trend signal."
            ),
        })

    # -----------------------------
    # Risk
    # -----------------------------

    volatility = risk.get("annualized_volatility")

    if volatility is not None:
        if volatility >= 30:
            severity = "negative"
            title = "Elevated volatility"
        elif volatility >= 20:
            severity = "warning"
            title = "Moderate volatility"
        else:
            severity = "neutral"
            title = "Relatively contained volatility"

        insights.append({
            "category": "Risk",
            "severity": severity,
            "title": title,
            "message": (
                f"Annualized 20-day volatility is approximately "
                f"{volatility:.2f}%."
            ),
        })

    # -----------------------------
    # Drawdown
    # -----------------------------

    max_drawdown = risk.get("maximum_drawdown")

    if max_drawdown is not None and max_drawdown <= -10:
        insights.append({
            "category": "Risk",
            "severity": "negative",
            "title": "Significant historical drawdown",
            "message": (
                f"The asset experienced a maximum historical drawdown "
                f"of {max_drawdown:.2f}%."
            ),
        })

    # -----------------------------
    # Volume
    # -----------------------------

    volume_ratio = volume.get("ratio")

    if volume_ratio is not None:
        if volume_ratio >= 1.5:
            insights.append({
                "category": "Volume",
                "severity": "warning",
                "title": "Unusually high trading activity",
                "message": (
                    f"Current volume is {volume_ratio:.2f}× "
                    "the 20-day average."
                ),
            })
        elif volume_ratio <= 0.5:
            insights.append({
                "category": "Volume",
                "severity": "neutral",
                "title": "Low trading activity",
                "message": (
                    f"Current volume is only {volume_ratio:.2f}× "
                    "the 20-day average."
                ),
            })

    # -----------------------------
    # Daily movement
    # -----------------------------

    daily_change = price.get("daily_change_pct")

    if daily_change is not None:
        insights.append({
            "category": "Daily Movement",
            "severity": (
                "positive"
                if daily_change > 0
                else "negative"
                if daily_change < 0
                else "neutral"
            ),
            "title": "Latest session movement",
            "message": (
                f"The latest session changed by "
                f"{daily_change:.2f}%."
            ),
        })

    return insights