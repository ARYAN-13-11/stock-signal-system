import pandas as pd
from ml_predict import ml_predict_signal
from arima_model import arima_predict_signal
from garch_model import garch_predict_signal
from tech_indicators import rsi_signal

def aggregate_signals(stock_data):
    """
    Combines signals from multiple models (LSTM, ARIMA, GARCH, RSI).
    Uses a weighted voting mechanism for the final signal:
    LSTM=3, ARIMA=2, GARCH=2, RSI=1
    """
    if stock_data.empty:
        return "HOLD"  # Fallback if no data

    # NOTE: Lowering threshold for LSTM to generate more signals if needed
    # Adjust if signals are still always HOLD
    signals = {
        "LSTM": ml_predict_signal(stock_data, threshold=0.000005),
        "ARIMA": arima_predict_signal(stock_data),
        "GARCH": garch_predict_signal(stock_data),
        "RSI": rsi_signal(stock_data)
    }

    print(f"📊 Model Predictions: {signals}")

    # ✅ Weighted Voting System
    weights = {"LSTM": 3, "ARIMA": 2, "GARCH": 2, "RSI": 1}

    buy_score = sum(
        weights[model] for model, sig in signals.items() if sig == "BUY"
    )
    sell_score = sum(
        weights[model] for model, sig in signals.items() if sig == "SELL"
    )

    if buy_score > sell_score:
        return "BUY"
    elif sell_score > buy_score:
        return "SELL"
    return "HOLD"

# ✅ Demo Testing
if __name__ == "__main__":
    stock_symbol = "AAPL"
    df = pd.read_csv(f"data/{stock_symbol}.csv", parse_dates=["Date"], index_col="Date")
    # In practice, might want the last 50-100 rows for LSTM
    df = df.tail(100)

    final_signal = aggregate_signals(df)
    print(f"📢 Final Aggregated Signal for {stock_symbol}: {final_signal}")
