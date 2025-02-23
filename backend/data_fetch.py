import requests
import os
import pandas as pd
import time
import random
import threading  # 🔥 Added for background execution

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "cuqsbd9r01qhaag3aqd0cuqsbd9r01qhaag3aqdg")  # 🔥 Use env variable for security
FINNHUB_BASE_URL = "https://finnhub.io/api/v1/quote"

TRACKED_STOCKS = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "NVDA", "META", "NFLX", "AMD", "INTC"]

os.makedirs("live_data", exist_ok=True)

def get_live_stock_price(symbol):
    try:
        r = requests.get(f"{FINNHUB_BASE_URL}?symbol={symbol}&token={FINNHUB_API_KEY}")
        data = r.json()
        if "c" in data and data["c"] > 0:
            new_price = data["c"] + random.uniform(-0.5, 0.5)  # 🔥 Random fluctuation
            return round(new_price, 2), round(data["pc"], 2)
        return None, None
    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")
        return None, None

def fetch_realtime_quotes():
    while True:
        for s in TRACKED_STOCKS:
            price, prev_close = get_live_stock_price(s)
            if price:
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                file_path = f"live_data/{s}.csv"
                
                df = pd.DataFrame([[s, price, prev_close, ts]], columns=["Symbol", "Price", "Prev_Close", "Timestamp"])
                df.to_csv(file_path, index=False, mode="w")  # 🔥 "w" mode ensures fresh data
                
                print(f"✅ {s} => {price} (Prev Close={prev_close}) at {ts}")

            time.sleep(1)  # Reduce API calls to avoid rate limits
        
        print("🔄 Prices Updated. Refreshing in 5 seconds...\n")
        time.sleep(5)

# 🔥 Start fetcher in a background thread
def start_fetcher():
    fetch_thread = threading.Thread(target=fetch_realtime_quotes, daemon=True)
    fetch_thread.start()

if __name__ == "__main__":
    start_fetcher()
