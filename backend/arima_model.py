import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# ✅ ARIMA-Based Price Prediction
def arima_predict_signal(stock_data):
    if len(stock_data) < 60:  # Need enough data
        return "HOLD"

    series = stock_data["Close"].values

    try:
        model = ARIMA(series, order=(1, 1, 1)).fit()
        forecast = model.forecast(steps=1)[0]  # Predict next step
        current_price = series[-1]

        # ✅ Predict BUY or SELL
        if forecast > current_price:
            return "BUY"
        elif forecast < current_price:
            return "SELL"
        else:
            return "HOLD"
    except Exception as e:
        print(f"❌ ARIMA Model Error: {e}")
        return "HOLD"
