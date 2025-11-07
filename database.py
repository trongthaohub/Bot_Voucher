import sqlite3
from contextlib import contextmanager

DB_FILE = "vouchers.db"

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_vouchers (
                code TEXT PRIMARY KEY,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def is_voucher_sent(code: str) -> bool:
    with get_db() as conn:
        cur = conn.execute("SELECT 1 FROM sent_vouchers WHERE code = ?", (code,))
        return cur.fetchone() is not None

def mark_voucher_sent(code: str):
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO sent_vouchers (code) VALUES (?)", (code,))
        conn.commit()