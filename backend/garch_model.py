import pandas as pd
import numpy as np
from arch import arch_model

# ✅ GARCH-Based Volatility Prediction
def garch_predict_signal(stock_data):
    if len(stock_data) < 60:  # Need at least 60 data points
        return "HOLD"

    series = stock_data["Close"].values
    returns = 100 * np.diff(np.log(series))  # Log Returns

    try:
        model = arch_model(returns, vol="Garch", p=1, q=1).fit(disp="off")
        forecast = model.forecast(horizon=1)
        next_vol = forecast.variance.values[-1, 0]

        # ✅ If volatility is high, SELL. If low, BUY.
        if next_vol > 5:
            return "SELL"
        else:
            return "BUY"
    except Exception as e:
        print(f"❌ GARCH Model Error: {e}")
        return "HOLD"
