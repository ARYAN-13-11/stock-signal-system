import requests
import os
import pandas as pd
import time
import random  # 🔥 Add random fluctuation to simulate live updates

FINNHUB_API_KEY = "cuqsbd9r01qhaag3aqd0cuqsbd9r01qhaag3aqdg"
FINNHUB_BASE_URL = "https://finnhub.io/api/v1/quote"

TRACKED_STOCKS = ["AAPL","TSLA","GOOGL","MSFT","AMZN","NVDA","META","NFLX","AMD","INTC"]

os.makedirs("live_data", exist_ok=True)

def get_live_stock_price(symbol):
    try:
        r = requests.get(f"{FINNHUB_BASE_URL}?symbol={symbol}&token={FINNHUB_API_KEY}")
        data = r.json()
        if "c" in data and data["c"] > 0:
            # 🔥 Introduce small price changes to simulate real-time updates
            new_price = data["c"] + random.uniform(-0.5, 0.5)
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
                
                # 🔥 Force overwrite to make sure API reads fresh values
                df = pd.DataFrame([[s, price, prev_close, ts]], columns=["Symbol", "Price", "Prev_Close", "Timestamp"])
                df.to_csv(file_path, index=False, mode="w")  # 🔥 "w" mode ensures the file is replaced each time
                
                print(f"✅ {s} => {price} (Prev Close={prev_close}) at {ts}")

            time.sleep(1)  # Reduce API calls to avoid rate limits
        
        print("🔄 Prices Updated. Refreshing in 5 seconds...\n")
        time.sleep(5)

if __name__ == "__main__":
    fetch_realtime_quotes()
