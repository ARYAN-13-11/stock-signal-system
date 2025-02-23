import os
import tensorflow as tf
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tech_indicators import add_technical_indicators
import warnings

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
tf.get_logger().setLevel("ERROR")
warnings.simplefilter(action='ignore', category=UserWarning)

MODEL_PATH = "backend/models/lstm_model.keras"
SCALER_PATH = "backend/models/scaler.pkl"

try:
    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ LSTM Model & Scaler Loaded Successfully!")
except Exception as e:
    print(f"❌ Error loading model/scaler: {e}")
    model = None
    scaler = None

def ml_predict_signal(df, threshold=0.000005):
    """
    This function is now mostly for aggregator usage:
    It checks if df has >= 50 rows. If not, return HOLD.
    We'll do minimal debug prints to avoid flooding.
    """
    if model is None or scaler is None:
        return "HOLD"
    if len(df) < 50:
        return "HOLD"

    # Try to do the same steps as in backtest: scale last 50 rows, predict once
    try:
        df = add_technical_indicators(df)
        df = df.dropna()
        if len(df) < 50:
            return "HOLD"

        feature_columns = ["Close", "RSI", "MACD", "VWAP", "ATR"]
        if any(col not in df.columns for col in feature_columns):
            return "HOLD"

        # Build last 50 rows
        last_50 = df[feature_columns].values[-50:]
        last_50_scaled = scaler.transform(last_50)
        last_50_scaled = np.array([last_50_scaled])  # shape (1, 50, 5)

        # Predict
        pred_scaled = model.predict(last_50_scaled, verbose=0)[0][0]

        # Inverse transform
        combined = np.array([[pred_scaled, 0, 0, 0, 0]])  # shape (1,5)
        pred_close = scaler.inverse_transform(combined)[0][0]

        last_price = df["Close"].iloc[-1]
        pct_change = (pred_close - last_price) / last_price

        # Minimal debug print:
        # print(f"🔎 LSTM: Last={last_price:.2f}, Pred={pred_close:.2f}, Δ={pct_change:.5f}")

        if pct_change > threshold:
            return "BUY"
        elif pct_change < -threshold:
            return "SELL"
        else:
            return "HOLD"

    except Exception as e:
        print(f"❌ Prediction Error in ml_predict_signal: {e}")
        return "HOLD"

if __name__ == "__main__":
    # Quick test
    import pandas as pd

    filepath = "data/AAPL.csv"
    if os.path.exists(filepath):
        df_test = pd.read_csv(filepath, parse_dates=["Date"], index_col="Date")
        signal = ml_predict_signal(df_test)
        print(f"Test signal for AAPL: {signal}")
    else:
        print("No data for AAPL.")
