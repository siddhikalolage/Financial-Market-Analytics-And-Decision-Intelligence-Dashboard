import os
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

DATA_PATH = Path(__file__).resolve().parent / "data" / "stock_data.csv"


def load_data():
    """Load, validate, and prepare the historical OHLCV dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=list(required)).drop_duplicates(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    if len(df) < 31:
        raise ValueError("At least 31 valid observations are required for rolling analytics.")
    if (df[["Open", "High", "Low", "Close", "Volume"]] < 0).any().any():
        raise ValueError("OHLCV data contains negative values.")

    # Analyst-ready derived metrics.
    df["Daily_Return"] = df["Close"].pct_change() * 100
    df["Cumulative_Return"] = (df["Close"] / df["Close"].iloc[0] - 1) * 100
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_50"] = df["Close"].rolling(50).mean()
    df["Rolling_Volatility_20D"] = df["Daily_Return"].rolling(20).std() * (252 ** 0.5)
    df["Rolling_Avg_Volume_20D"] = df["Volume"].rolling(20).mean()
    df["Drawdown"] = (df["Close"] / df["Close"].cummax() - 1) * 100
    df["Volume_Change"] = df["Volume"].pct_change() * 100
    df["Range_Pct"] = ((df["High"] - df["Low"]) / df["Close"]) * 100

    return df


def build_metrics(df):
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    daily_return = float(latest["Daily_Return"])
    period_return = float(latest["Cumulative_Return"])
    volatility = float(df["Daily_Return"].dropna().std() * (252 ** 0.5))
    max_drawdown = float(df["Drawdown"].min())
    avg_volume = float(df["Volume"].tail(30).mean())
    up_days = int((df["Daily_Return"] > 0).sum())
    down_days = int((df["Daily_Return"] < 0).sum())

    return {
        "last_close": round(float(latest["Close"]), 2),
        "price_change": round(float(latest["Close"] - previous["Close"]), 2),
        "percent_change": round(daily_return, 2),
        "period_return": round(period_return, 2),
        "annualized_volatility": round(volatility, 2),
        "max_drawdown": round(max_drawdown, 2),
        "avg_volume": int(avg_volume),
        "up_days": up_days,
        "down_days": down_days,
        "observations": int(len(df)),
        "start_date": df["Date"].iloc[0].strftime("%Y-%m-%d"),
        "end_date": df["Date"].iloc[-1].strftime("%Y-%m-%d"),
    }


def build_insights(df):
    latest = df.iloc[-1]
    insights = []
    if pd.notna(latest["MA_20"]):
        direction = "above" if latest["Close"] >= latest["MA_20"] else "below"
        insights.append(f"Latest close is {direction} the 20-day moving average, indicating the current short-term price position.")
    insights.append(f"Maximum historical drawdown is {df['Drawdown'].min():.2f}%, highlighting the largest peak-to-trough decline in the dataset.")
    insights.append(f"Annualized historical volatility is approximately {df['Daily_Return'].dropna().std() * (252 ** 0.5):.2f}%, providing a risk context for the observed returns.")
    if pd.notna(latest["Volume_Change"]):
        volume_direction = "higher" if latest["Volume_Change"] > 0 else "lower"
        insights.append(f"The latest trading volume is {abs(latest['Volume_Change']):.1f}% {volume_direction} than the previous observation, useful for monitoring participation changes.")
    return insights


def chart_payload(df):
    recent = df.tail(90).copy()
    return {
        "dates": recent["Date"].dt.strftime("%Y-%m-%d").tolist(),
        "prices": recent["Close"].round(2).tolist(),
        "ma20": recent["MA_20"].round(2).where(recent["MA_20"].notna(), None).tolist(),
        "volumes": recent["Volume"].astype(int).tolist(),
        "returns": recent["Daily_Return"].round(2).where(recent["Daily_Return"].notna(), None).tolist(),
        "volatility": recent["Rolling_Volatility_20D"].round(2).where(recent["Rolling_Volatility_20D"].notna(), None).tolist(),
        "drawdown": recent["Drawdown"].round(2).tolist(),
    }


@app.route("/")
def index():
    df = load_data()
    metrics = build_metrics(df)
    latest = df.iloc[-1]
    trend = "UP" if latest["Daily_Return"] > 0 else "DOWN" if latest["Daily_Return"] < 0 else "FLAT"
    trend_class = "positive" if trend == "UP" else "negative" if trend == "DOWN" else "neutral"

    return render_template(
        "index.html",
        metrics=metrics,
        trend=trend,
        trend_class=trend_class,
        chart_data=chart_payload(df),
        insights=build_insights(df),
    )


@app.route("/api/data")
def api_data():
    """Return the latest 90 observations and derived analytical fields."""
    df = load_data().tail(90)
    records = df[["Date", "Open", "High", "Low", "Close", "Volume", "Daily_Return", "Drawdown"]].copy()
    records["Date"] = records["Date"].dt.strftime("%Y-%m-%d")
    return jsonify(records.round(4).to_dict(orient="records"))


@app.route("/api/metrics")
def api_metrics():
    return jsonify(build_metrics(load_data()))


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "dataset": str(DATA_PATH.name)})


if __name__ == "__main__":
    # Production deployments should use a WSGI server and DEBUG disabled.
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
