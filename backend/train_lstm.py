import os
import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from tech_indicators import add_technical_indicators  

# -------------------------------------
# 1. Load your AAPL dataset
# -------------------------------------
df = pd.read_csv("data/AAPL.csv", parse_dates=["Date"], index_col="Date")

# -------------------------------------
# 2. Add Technical Indicators
# -------------------------------------
df = add_technical_indicators(df)

# Select only relevant columns (make sure they exist after .dropna() in add_technical_indicators)
feature_columns = ["Close", "RSI", "MACD", "VWAP", "ATR"]
df = df[feature_columns].dropna()

# -------------------------------------
# 3. Fit MinMaxScaler and Save
# -------------------------------------
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df)
os.makedirs("backend/models", exist_ok=True)
joblib.dump(scaler, "backend/models/scaler.pkl")

# -------------------------------------
# 4. Build Sequences (X) and Labels (y)
# -------------------------------------
X, y = [], []

# We'll predict next day's CLOSE value for the model
sequence_length = 50
for i in range(sequence_length, len(df_scaled)):
    # Past 50 timesteps
    X.append(df_scaled[i-sequence_length:i])
    # Current row's 'Close' (index 0 in df_scaled after we selected 5 columns)
    y.append(df_scaled[i, 0])

X = np.array(X)
y = np.array(y)

print(f"X shape: {X.shape}, y shape: {y.shape}")

# -------------------------------------
# 5. Define Improved LSTM Model
# -------------------------------------
model = Sequential([
    # We remove `return_sequences=True` since we only have 1 LSTM layer
    LSTM(128, input_shape=(sequence_length, len(feature_columns))),
    Dropout(0.2),
    Dense(64, activation="relu"),
    Dropout(0.2),
    Dense(1)  # Final linear output for next day's scaled close
])

# -------------------------------------
# 6. Compile & Train Model
# -------------------------------------
model.compile(
    optimizer=Adam(learning_rate=0.0005),
    loss="mse"
)

# Increase epochs for deeper training
history = model.fit(
    X, y,
    epochs=100,         # Try 100+ for better learning
    batch_size=32,
    validation_split=0.1,
    verbose=1
)

# -------------------------------------
# 7. Save Model
# -------------------------------------
model.save("backend/models/lstm_model.keras")
print("✅ LSTM Model Saved Successfully!")
