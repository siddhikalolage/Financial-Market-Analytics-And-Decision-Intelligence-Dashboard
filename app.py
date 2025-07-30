import pandas as pd
from flask import Flask, render_template, jsonify
import numpy as np
import os

app = Flask(__name__)

def load_data():
    """Load stock data from CSV file"""
    try:
        df = pd.read_csv("data/stock_data.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        # Fallback to current directory if data folder doesn't exist
        df = pd.read_csv("stock_data.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df

def simple_prediction(df, days=5):
    """Simple moving average prediction"""
    # Calculate moving averages
    df['MA_10'] = df['Close'].rolling(window=10).mean()
    df['MA_30'] = df['Close'].rolling(window=30).mean()
    
    # Simple trend analysis
    recent_prices = df['Close'].tail(10)
    price_change = recent_prices.iloc[-1] - recent_prices.iloc[0]
    avg_change = price_change / 10
    
    # Predict next few days based on trend
    last_price = df['Close'].iloc[-1]
    predictions = []
    for i in range(1, days + 1):
        predicted_price = last_price + (avg_change * i)
        # Add some randomness to make it more realistic
        noise = np.random.normal(0, df['Close'].std() * 0.01)
        predicted_price += noise
        predictions.append(round(predicted_price, 2))
    
    return predictions

@app.route("/")
def index():
    """Main dashboard page"""
    df = load_data()
    
    # Calculate key metrics
    last_close = round(df['Close'].iloc[-1], 2)
    prev_close = round(df['Close'].iloc[-2], 2)
    price_change = round(last_close - prev_close, 2)
    percent_change = round((price_change / prev_close) * 100, 2)
    avg_volume = int(df['Volume'].tail(30).mean())
    
    # Determine trend
    trend = "UP" if price_change > 0 else "DOWN" if price_change < 0 else "FLAT"
    trend_color = "green" if trend == "UP" else "red" if trend == "DOWN" else "gray"
    
    # Get recent data for chart (last 30 days)
    recent_data = df.tail(30)
    chart_data = {
        'dates': recent_data['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'prices': recent_data['Close'].tolist(),
        'volumes': recent_data['Volume'].tolist()
    }
    
    # Get predictions
    predictions = simple_prediction(df)
    
    return render_template("index.html", 
                         last_close=last_close,
                         price_change=price_change,
                         percent_change=percent_change,
                         avg_volume=avg_volume,
                         trend=trend,
                         trend_color=trend_color,
                         chart_data=chart_data,
                         predictions=predictions)

@app.route("/api/data")
def api_data():
    """API endpoint to get stock data as JSON"""
    df = load_data()
    recent_data = df.tail(50)  # Last 50 days
    return jsonify({
        'dates': recent_data['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'open': recent_data['Open'].tolist(),
        'high': recent_data['High'].tolist(),
        'low': recent_data['Low'].tolist(),
        'close': recent_data['Close'].tolist(),
        'volume': recent_data['Volume'].tolist()
    })

@app.route("/api/prediction")
def api_prediction():
    """API endpoint to get price predictions"""
    df = load_data()
    predictions = simple_prediction(df, days=7)
    return jsonify({
        'predictions': predictions,
        'current_price': round(df['Close'].iloc[-1], 2)
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)