import pandas as pd
import numpy as np
import talib  # Ensure TA-Lib is installed

# ✅ Compute RSI (Relative Strength Index) - Not used in final aggregator, but kept for reference
def compute_rsi(stock_data, period=14):
    if len(stock_data) < period:
        return pd.Series([None] * len(stock_data))  # Return NaNs if not enough data

    delta = stock_data["Close"].diff()
    up, down = delta.clip(lower=0), -delta.clip(upper=0)
    roll_up = up.rolling(period).mean()
    roll_down = down.rolling(period).mean()
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ✅ RSI Trading Signal
def rsi_signal(stock_data):
    """
    Returns a single signal (BUY, SELL, HOLD) based on the most recent RSI.
    Below 30 => BUY, Above 70 => SELL, else HOLD.
    """
    if len(stock_data) < 14:
        return "HOLD"

    stock_data["RSI"] = compute_rsi(stock_data)
    last_rsi = stock_data["RSI"].iloc[-1]

    if pd.isna(last_rsi):
        return "HOLD"

    if last_rsi < 30:
        return "BUY"
    elif last_rsi > 70:
        return "SELL"
    else:
        return "HOLD"

# ✅ Compute MACD (Moving Average Convergence Divergence)
def compute_macd(stock_data):
    if len(stock_data) < 26:
        # Not enough data for MACD
        return pd.Series([None] * len(stock_data)), pd.Series([None] * len(stock_data))

    macd, macd_signal, _ = talib.MACD(
        stock_data["Close"],
        fastperiod=12,
        slowperiod=26,
        signalperiod=9
    )
    return macd, macd_signal

# ✅ Compute VWAP (Volume Weighted Average Price) - Simple approximation
def compute_vwap(stock_data):
    if len(stock_data) < 1:
        return pd.Series([None] * len(stock_data))
    return (stock_data["High"] + stock_data["Low"] + stock_data["Close"]) / 3

# ✅ Compute ATR (Average True Range)
def compute_atr(stock_data, period=14):
    if len(stock_data) < period:
        return pd.Series([None] * len(stock_data))

    return talib.ATR(
        stock_data["High"],
        stock_data["Low"],
        stock_data["Close"],
        timeperiod=period
    )

# ✅ Compute Bollinger Bands Width
def compute_bollinger_bands(stock_data):
    if len(stock_data) < 20:
        return pd.Series([None] * len(stock_data))

    upper_band, middle_band, lower_band = talib.BBANDS(
        stock_data["Close"],
        timeperiod=20
    )
    return (upper_band - lower_band) / middle_band

# ✅ Add All Indicators to Stock Data
def add_technical_indicators(df):
    """
    Adds RSI, MACD, ATR, VWAP, and Bollinger Band Width columns to `df`.
    Drops rows with NaNs to ensure indicators are valid.
    """
    try:
        # RSI
        df["RSI"] = talib.RSI(df["Close"], timeperiod=14)

        # MACD
        df["MACD"], df["MACD_Signal"], _ = talib.MACD(
            df["Close"],
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )

        # ATR
        df["ATR"] = talib.ATR(
            df["High"],
            df["Low"],
            df["Close"],
            timeperiod=14
        )

        # VWAP (approximation)
        df["VWAP"] = (df["High"] + df["Low"] + df["Close"]) / 3

        # Bollinger Bands Width
        upper_band, _, lower_band = talib.BBANDS(df["Close"], timeperiod=20)
        df["BB_Width"] = (upper_band - lower_band) / (
            (upper_band + lower_band) / 2
        )

        # Drop rows with NaN indicator values
        df = df.dropna()

    except Exception as e:
        print(f"❌ Indicator Calculation Error: {e}")

    return df
