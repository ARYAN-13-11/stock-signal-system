import os
import sqlite3
import csv
import glob
import requests
import pandas as pd
import time
import yfinance as yf

from flask import Flask, jsonify, request, session, g
from flask_cors import CORS
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from ml_predict import ml_predict_signal
from backtest import run_backtest

#####################################
# CONFIGURATION
#####################################
app = Flask(__name__)

# Enable CORS with credentials for React frontend
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

# Polygon.io API Key (Replace with your API key)
POLYGON_API_KEY = "28Nfu2UJbj_paH2ac0Gg6q0C8c23yM8M"

# Cache to store API responses for rate limiting
candlestick_cache = {}

# Configure Flask Session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True  
app.config["SESSION_USE_SIGNER"] = True  
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True  
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production
app.config["SECRET_KEY"] = "your_secret_key_here"

Session(app)

# Ensure session folder exists
if not os.path.exists("./flask_session"):
    os.makedirs("./flask_session")

DATABASE = "users.db"
DATA_PATH = "data"

#####################################
# DATABASE HELPERS
#####################################
def get_db():
    if "_database" not in g:
        g._database = sqlite3.connect(DATABASE, check_same_thread=False)
        g._database.row_factory = sqlite3.Row
    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        db.commit()

init_db()

#####################################
# AUTHENTICATION & USER MANAGEMENT
#####################################

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        username, email, password, confirm_password = (
            data.get("username"), data.get("email"), data.get("password"), data.get("confirmPassword")
        )
        if not all([username, email, password, confirm_password]):
            return jsonify({"error": "Missing fields"}), 400
        if "@" not in email or "." not in email:
            return jsonify({"error": "Invalid email format"}), 400
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400
        hashed_password = generate_password_hash(password)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_password))
            conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session.modified = True
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": "Server error. Please try again."}), 500
    
@app.route("/refresh_token", methods=["POST"])
def refresh_token():
    if "user_id" in session:
        session.modified = True
        return jsonify({"token": "NEW_REFRESHED_TOKEN"}), 200
    return jsonify({"error": "Session expired"}), 401
    
@app.route("/check_login", methods=["GET"])
def check_login():
    if "user_id" in session:
        return jsonify({"logged_in": True, "user_id": session["user_id"]})
    return jsonify({"logged_in": False}), 401



@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200



#####################################
# STOCK PRICES & LIVE DATA
#####################################

@app.route("/live_prices", methods=["GET"])
def live_prices():
    stock_data = []
    for file_path in glob.glob("live_data/*.csv"):
        try:
            with open(file_path, "r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if not rows:
                    continue
                last_row = rows[-1]
                symbol, price, prev_close, timestamp = last_row
                stock_data.append({
                    "symbol": symbol,
                    "price": round(float(price), 2),
                    "prev_close": round(float(prev_close), 2),
                    "timestamp": timestamp
                })
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            continue
    return jsonify(stock_data), 200, {'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'}

#####################################
# MACHINE LEARNING SIGNAL API
#####################################
@app.route("/signal/<symbol>", methods=["GET"])
def get_stock_signal(symbol):
    """
    Predicts a trading signal using LSTM & other models.
    Ensures the latest live price is used for predictions.
    """
    historical_path = os.path.join(DATA_PATH, f"{symbol}.csv")
    live_path = os.path.join("live_data", f"{symbol}.csv")

    if not os.path.exists(historical_path):
        return jsonify({"error": f"Historical data for {symbol} not found"}), 404

    df = pd.read_csv(historical_path, parse_dates=["Date"])

    # Merge latest live price if available
    if os.path.exists(live_path):
        try:
            live_df = pd.read_csv(live_path)
            latest_live_row = live_df.iloc[-1]  # Get latest live row
            latest_price = float(latest_live_row["Price"])

            # Create new row for live data
            new_row = pd.DataFrame({"Date": [latest_live_row["Timestamp"]], "Close": [latest_price]})

            # Append new live data using concat (replaces deprecated append)
            df = pd.concat([df, new_row], ignore_index=True)

        except Exception as e:
            print(f"⚠️ Error reading live data for {symbol}: {e}")

    # Ensure we have enough data for LSTM
    if len(df) < 50:
        return jsonify({"error": "Not enough data to generate signal"}), 400

    # Use last 50 rows for LSTM prediction
    df = df.tail(50)
    signal = ml_predict_signal(df)

    # Use latest price (live if available, else historical)
    latest_price = df["Close"].iloc[-1]
    recommended_entry = round(latest_price * 0.98, 2)
    stop_loss = round(latest_price * 0.95, 2)
    take_profit = round(latest_price * 1.05, 2)

    response = {
        "ticker": symbol,
        "signal": signal,
        "currentPrice": round(latest_price, 2),
        "recommendedEntry": recommended_entry,
        "stopLoss": stop_loss,
        "takeProfit": take_profit,
        "explanation": "Generated using LSTM prediction model with live price integration"
    }

    return jsonify(response)

#####################################
# BACKTESTING METRICS API
#####################################
@app.route('/metrics/<symbol>', methods=['GET'])
def get_stock_metrics(symbol):
    """
    API to return backtest performance metrics for a given stock.
    """
    try:
        print(f"📈 Fetching Metrics for {symbol}...")

        initial_cash = 100000  # Use the same value as in `backtest.py`
        results = run_backtest(symbol)

        if results is None:
            return jsonify({"error": "No backtest data found"}), 500

        # ✅ Ensure API returns correct keys
        metrics = {
            "Final Value": results.get("final_value", 0.0),
            "Total PnL": results.get("final_value", 0.0) - initial_cash,  # PnL Calculation
            "Num Trades": results.get("total_trades", 0),
            "Win Rate": results.get("win_rate", 0.0),
            "Sharpe Ratio": results.get("sharpe_ratio", 0.0),
        }

        return jsonify(metrics)

    except Exception as e:
        print(f"❌ Error fetching metrics: {e}")
        return jsonify({"error": "Error fetching metrics. Check API."}), 500
    
#####################################
# CANDLESTICK CHART DATA (Alpha Vantage)
#####################################

@app.route('/candlestick/<symbol>', methods=['GET'])
def get_candlestick_data(symbol):
    """
    API to return historical candlestick data using Polygon.io.
    """
    try:
        timeframe = request.args.get("timeframe", "1d")
        interval_map = {
            "1min": "minute",
            "5min": "minute",
            "1hr": "hour",
            "1d": "day"
        }
        interval = interval_map.get(timeframe, "day")

        if symbol in candlestick_cache:
            last_fetch_time, cached_data = candlestick_cache[symbol]
            if time.time() - last_fetch_time < 300:  # Cache for 5 minutes
                print(f"✅ Returning cached data for {symbol}")
                return jsonify(cached_data)

        # Fetch data from Polygon.io
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{interval}/2024-02-01/2024-02-23?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
        
        response = requests.get(url)
        data = response.json()

        if "results" not in data:
            return jsonify({"error": "No data available or rate limit exceeded."}), 500

        # Process & format data
        chart_data = [
            {
                "date": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(candle["t"] / 1000)),
                "ohlc": [candle["o"], candle["h"], candle["l"], candle["c"]]
            }
            for candle in data["results"]
        ]

        # Cache response
        candlestick_cache[symbol] = (time.time(), chart_data)

        return jsonify(chart_data)

    except Exception as e:
        print(f"❌ Error fetching candlestick data: {e}")
        return jsonify({"error": "API Error. Try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
