import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("prices.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            price REAL,
            scraped_at TEXT
        )
    """)
    conn.commit()
    return conn

def insert_price(conn, title, url, price):
    conn.execute(
        "INSERT INTO price_history (title, url, price, scraped_at) VALUES (?, ?, ?, ?)",
        (title, url, price, datetime.now().isoformat())
    )
    conn.commit()

def get_last_price(conn, url):
    row = conn.execute(
        "SELECT price FROM price_history WHERE url = ? ORDER BY scraped_at DESC LIMIT 1",
        (url,)
    ).fetchone()
    return row[0] if row else None