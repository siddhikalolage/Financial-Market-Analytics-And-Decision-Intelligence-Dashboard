import os
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)

DATA_PATH = Path(__file__).resolve().parent / "data" / "stock_data.csv"
TRADING_DAYS = 252


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
    if (df[numeric_cols] < 0).any().any():
        raise ValueError("OHLCV data contains negative values.")
    if (df["Close"] == 0).any():
        raise ValueError("Close prices must be non-zero for return calculations.")
    if (df["High"] < df[["Open", "Close"]].max(axis=1)).any():
        raise ValueError("High price is below Open or Close for at least one row.")
    if (df["Low"] > df[["Open", "Close"]].min(axis=1)).any():
        raise ValueError("Low price is above Open or Close for at least one row.")

    # Analyst-ready derived metrics. All rolling calculations use historical rows only.
    df["Daily_Return"] = df["Close"].pct_change()
    df["Daily_Return_Pct"] = df["Daily_Return"] * 100
    df["Cumulative_Return"] = df["Close"] / df["Close"].iloc[0] - 1
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_50"] = df["Close"].rolling(50).mean()
    df["MA_200"] = df["Close"].rolling(200).mean()
    df["Rolling_Volatility_20D"] = df["Daily_Return"].rolling(20).std() * np.sqrt(TRADING_DAYS)
    df["Rolling_Avg_Volume_20D"] = df["Volume"].rolling(20).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Rolling_Avg_Volume_20D"]
    df["Drawdown"] = df["Close"] / df["Close"].cummax() - 1
    df["Volume_Change"] = df["Volume"].pct_change()
    df["Range_Pct"] = (df["High"] - df["Low"]) / df["Close"]

    return df


def _safe_ratio(numerator, denominator):
    return float(numerator / denominator) if denominator not in (0, 0.0) and pd.notna(denominator) else None


def build_metrics(df):
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    returns = df["Daily_Return"].dropna()
    positive_returns = returns[returns > 0]
    negative_returns = returns[returns < 0]

    periods = {
        "5d_return": df["Close"].pct_change(5).iloc[-1] * 100,
        "20d_return": df["Close"].pct_change(20).iloc[-1] * 100,
    }
    latest_year = int(latest["Date"].year)
    ytd_start = df.loc[df["Date"].dt.year == latest_year, "Close"].iloc[0]
    periods["ytd_return"] = (latest["Close"] / ytd_start - 1) * 100

    years = max((df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25, 1 / 365.25)
    cagr = (latest["Close"] / df["Close"].iloc[0]) ** (1 / years) - 1
    annualized_volatility = returns.std() * np.sqrt(TRADING_DAYS)
    downside = returns[returns < 0].std() * np.sqrt(TRADING_DAYS)
    sharpe = _safe_ratio(returns.mean() * TRADING_DAYS, annualized_volatility)
    sortino = _safe_ratio(returns.mean() * TRADING_DAYS, downside)
    max_drawdown = float(df["Drawdown"].min())
    calmar = _safe_ratio(cagr, abs(max_drawdown))
    profit_factor = _safe_ratio(positive_returns.sum(), abs(negative_returns.sum()))

    return {
        "last_close": round(float(latest["Close"]), 2),
        "price_change": round(float(latest["Close"] - previous["Close"]), 2),
        "percent_change": round(float(latest["Daily_Return_Pct"]), 2),
        "period_return": round(float(latest["Cumulative_Return"] * 100), 2),
        "return_5d": round(float(periods["5d_return"]), 2),
        "return_20d": round(float(periods["20d_return"]), 2),
        "ytd_return": round(float(periods["ytd_return"]), 2),
        "cagr": round(float(cagr * 100), 2),
        "annualized_volatility": round(float(annualized_volatility * 100), 2),
        "downside_volatility": round(float(downside * 100), 2) if pd.notna(downside) else None,
        "sharpe_ratio": round(float(sharpe), 2) if sharpe is not None else None,
        "sortino_ratio": round(float(sortino), 2) if sortino is not None else None,
        "calmar_ratio": round(float(calmar), 2) if calmar is not None else None,
        "profit_factor": round(float(profit_factor), 2) if profit_factor is not None else None,
        "max_drawdown": round(max_drawdown * 100, 2),
        "current_drawdown": round(float(latest["Drawdown"] * 100), 2),
        "avg_volume": int(df["Volume"].tail(30).mean()),
        "volume_ratio": round(float(latest["Volume_Ratio"]), 2) if pd.notna(latest["Volume_Ratio"]) else None,
        "up_days": int((returns > 0).sum()),
        "down_days": int((returns < 0).sum()),
        "observations": int(len(df)),
        "start_date": df["Date"].iloc[0].strftime("%Y-%m-%d"),
        "end_date": df["Date"].iloc[-1].strftime("%Y-%m-%d"),
        "data_quality": {
            "missing_values": int(df[["Date", "Open", "High", "Low", "Close", "Volume"]].isna().sum().sum()),
            "duplicate_dates": int(df["Date"].duplicated().sum()),
            "date_order_valid": bool(df["Date"].is_monotonic_increasing),
        },
    }


def build_insights(df):
    latest = df.iloc[-1]
    insights = []
    if pd.notna(latest["MA_20"]):
        distance = (latest["Close"] / latest["MA_20"] - 1) * 100
        direction = "above" if distance >= 0 else "below"
        insights.append(f"Latest close is {abs(distance):.2f}% {direction} the 20-day moving average, providing short-term trend context.")
    insights.append(f"The asset is currently {df['Drawdown'].iloc[-1] * 100:.2f}% below its historical peak; maximum drawdown is {df['Drawdown'].min() * 100:.2f}%.")
    volatility = df["Daily_Return"].dropna().std() * np.sqrt(TRADING_DAYS) * 100
    insights.append(f"Annualized historical volatility is {volatility:.2f}%, which quantifies the observed return variability rather than predicting future risk.")
    if pd.notna(latest["Volume_Ratio"]):
        activity = "above" if latest["Volume_Ratio"] >= 1 else "below"
        insights.append(f"Latest volume is {latest['Volume_Ratio']:.2f}x the 20-day average, indicating participation {activity} its recent baseline.")
    if pd.notna(latest["Daily_Return_Pct"]):
        magnitude = abs(latest["Daily_Return_Pct"])
        direction = "gain" if latest["Daily_Return_Pct"] > 0 else "decline" if latest["Daily_Return_Pct"] < 0 else "flat move"
        insights.append(f"The latest session recorded a {magnitude:.2f}% {direction}; review this observation alongside the longer-term return and risk KPIs.")
    return insights


def chart_payload(df):
    recent = df.tail(90).copy()
    return {
        "dates": recent["Date"].dt.strftime("%Y-%m-%d").tolist(),
        "prices": recent["Close"].round(2).tolist(),
        "ma20": recent["MA_20"].round(2).where(recent["MA_20"].notna(), None).tolist(),
        "ma50": recent["MA_50"].round(2).where(recent["MA_50"].notna(), None).tolist(),
        "volumes": recent["Volume"].astype(int).tolist(),
        "avg_volume": recent["Rolling_Avg_Volume_20D"].round(0).where(recent["Rolling_Avg_Volume_20D"].notna(), None).tolist(),
        "returns": (recent["Daily_Return"] * 100).round(2).where(recent["Daily_Return"].notna(), None).tolist(),
        "volatility": (recent["Rolling_Volatility_20D"] * 100).round(2).where(recent["Rolling_Volatility_20D"].notna(), None).tolist(),
        "drawdown": (recent["Drawdown"] * 100).round(2).tolist(),
    }


@app.route("/")
def index():
    df = load_data()
    metrics = build_metrics(df)
    latest = df.iloc[-1]
    trend = "UP" if latest["Daily_Return"] > 0 else "DOWN" if latest["Daily_Return"] < 0 else "FLAT"
    trend_class = "positive" if trend == "UP" else "negative" if trend == "DOWN" else "neutral"
    return render_template("index.html", metrics=metrics, trend=trend, trend_class=trend_class, chart_data=chart_payload(df), insights=build_insights(df))


@app.route("/api/data")
def api_data():
    """Return the latest 90 observations and derived analytical fields."""
    df = load_data().tail(90)
    columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Daily_Return_Pct", "MA_20", "MA_50", "Rolling_Volatility_20D", "Volume_Ratio", "Drawdown", "Range_Pct"]
    records = df[columns].copy()
    records["Date"] = records["Date"].dt.strftime("%Y-%m-%d")
    return jsonify(records.round(4).replace({np.nan: None}).to_dict(orient="records"))


@app.route("/api/metrics")
def api_metrics():
    return jsonify(build_metrics(load_data()))


@app.route("/api/health")
def health():
    df = load_data()
    return jsonify({"status": "ok", "dataset": DATA_PATH.name, "observations": len(df), "start_date": df["Date"].iloc[0].strftime("%Y-%m-%d"), "end_date": df["Date"].iloc[-1].strftime("%Y-%m-%d")})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
