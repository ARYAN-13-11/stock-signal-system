import os
import pandas as pd
import numpy as np
import yfinance as yf
from tech_indicators import add_technical_indicators

import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib

# ------------------------------
# GLOBAL: Load LSTM + Scaler once
# ------------------------------
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


def run_backtest(symbol, initial_cash=100000, threshold=0.000005):
    """
    Performs a single-pass backtest:
    1. Loads data
    2. Adds indicators
    3. Scales & builds 3D array of shape (N-50, 50, 5) for LSTM
    4. Single model.predict() call
    5. Derives signals by comparing predicted vs. last actual close
    6. Simulates trades
    """
    os.makedirs("data", exist_ok=True)
    data_file = f"data/{symbol}.csv"

    # 1) Download if needed
    if not os.path.exists(data_file):
        df_downloaded = yf.download(symbol, start="2019-01-01", end="2025-12-31", progress=False)
        df_downloaded.to_csv(data_file)

    df = pd.read_csv(data_file, parse_dates=["Date"], index_col="Date")
    df = df.loc["2022-01-01":"2024-12-31"].ffill().dropna()

    if df.empty:
        print(f"❌ No data for {symbol}")
        return None

    # 2) Add indicators & drop NaNs
    df = add_technical_indicators(df)
    df.dropna(inplace=True)

    if df.empty or len(df) < 50:
        print(f"❌ Not enough data after indicators for {symbol}")
        return None

    # 3) Build 3D array: (N-50, 50, 5)
    feature_cols = ["Close", "RSI", "MACD", "VWAP", "ATR"]
    missing_feats = [f for f in feature_cols if f not in df.columns]
    if missing_feats:
        print(f"❌ Missing features in DF: {missing_feats}")
        return None

    # Slice only the needed columns
    data = df[feature_cols].values
    scaled_data = scaler.transform(data)  # shape (N, 5)

    sequence_length = 50
    X = []
    # We will store predicted prices aligned with the index of df
    # So the first predicted day is at df index [50]
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i - sequence_length : i])

    X = np.array(X)  # shape (N-50, 50, 5)

    # 4) Single predict call
    predictions_scaled = model.predict(X, verbose=0).flatten()  # shape (N-50,)

    # We have predictions for [indices 50..N-1]
    # We'll align them with df index:
    df_idx = df.index[sequence_length:]  # skip first 50 rows
    df_pred = pd.DataFrame({
        "PredictedScaled": predictions_scaled
    }, index=df_idx)

    # 5) Convert scaled predictions back to actual prices
    # We'll feed dummy zeros for the other 4 features (RSI, MACD, VWAP, ATR) to the inverse_transform
    dummy = np.zeros((len(df_pred), 4))
    # build array shape (N-50, 5)
    combined = np.column_stack([df_pred["PredictedScaled"].values, dummy])
    inverted = scaler.inverse_transform(combined)
    # The predicted close is the first column after inverse_transform
    df_pred["PredictedClose"] = inverted[:, 0]

    # Merge back with actual data
    df_merged = df.merge(df_pred, left_index=True, right_index=True, how="left")

    # 6) Generate signals
    # We'll define: if (PredictedClose - last Close)/last Close > threshold => BUY
    # else if < -threshold => SELL, else HOLD
    signals = []
    for idx, row in df_merged.iterrows():
        if pd.isna(row.get("PredictedClose", np.nan)):
            # For the first 50 rows, no prediction => HOLD
            signals.append("HOLD")
        else:
            last_price = row["Close"]
            predicted_price = row["PredictedClose"]
            pct_change = (predicted_price - last_price) / last_price

            if pct_change > threshold:
                signals.append("BUY")
            elif pct_change < -threshold:
                signals.append("SELL")
            else:
                signals.append("HOLD")

    df_merged["Signal"] = signals

    # Debug distribution
    print(f"\nSignal Distribution for {symbol}:")
    print(df_merged["Signal"].value_counts())

    # 7) Trading simulation
    cash = initial_cash
    position = 0
    trades = 0
    winning_trades = 0
    returns = []
    entry_price = None

    for i, (idx, row) in enumerate(df_merged.iterrows()):
        close = row["Close"]
        signal = row["Signal"]

        if position == 0:  # no open position
            if signal == "BUY":
                position = cash / close
                cash = 0
                entry_price = close
                trades += 1
            elif signal == "SELL":
                position = -cash / close
                cash = 0
                entry_price = close
                trades += 1

        elif position > 0:  # long
            if signal == "SELL":
                cash = position * close
                position = 0
                trade_return = ((close / entry_price) - 1) * 100
                returns.append(trade_return)
                if trade_return > 0:
                    winning_trades += 1

        elif position < 0:  # short
            if signal == "BUY":
                cash = -position * close
                position = 0
                trade_return = ((entry_price / close) - 1) * 100
                returns.append(trade_return)
                if trade_return > 0:
                    winning_trades += 1

    if position != 0:
        final_close = df_merged["Close"].iloc[-1]
        if position > 0:
            cash = position * final_close
        else:
            cash = -position * final_close
        position = 0

    final_value = cash
    win_rate = (winning_trades / trades) * 100 if trades else 0
    sharpe_ratio = 0
    if len(returns) > 1:
        sharpe_ratio = (np.mean(returns) / (np.std(returns) + 1e-9)) * np.sqrt(len(returns))

    print("\n" + "=" * 50)
    print(f"🚀 Backtest Summary for {symbol}")
    print(f"💰 Final Value: ${final_value:,.2f}")
    print(f"📊 Trades: {trades} | Wins: {winning_trades} | Win Rate: {win_rate:.1f}%")
    print(f"📈 Sharpe Ratio: {sharpe_ratio:.2f}")
    print("=" * 50)

    return {
        "final_value": final_value,
        "total_trades": trades,
        "win_rate": win_rate,
        "sharpe_ratio": sharpe_ratio
    }

if __name__ == "__main__":
    for stock in ["AAPL", "META", "AMD"]:
        print(f"\n🔥 Running Backtest for {stock}...")
        _result = run_backtest(stock)
