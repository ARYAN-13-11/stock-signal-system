import sqlite3

DB_FILE = "users.db"

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ✅ Users Table (Already Exists)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ✅ Portfolios Table (Virtual Trading Balance)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 100000.0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # ✅ Transactions Table (Buy/Sell Records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stock_symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            trade_type TEXT CHECK( trade_type IN ('BUY', 'SELL') ) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database setup complete!")

def get_db_connection():
    return sqlite3.connect(DB_FILE)

# ✅ Run this file once to create tables
if __name__ == "__main__":
    create_tables()
