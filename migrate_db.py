import sqlite3
import os

db_path = "f:/apibinance2026/binance_tracker.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check current columns in bot_signals
    cursor.execute("PRAGMA table_info(bot_signals);")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")

    # Add exchange_request if missing
    if "exchange_request" not in columns:
        print("Adding exchange_request column...")
        cursor.execute("ALTER TABLE bot_signals ADD COLUMN exchange_request TEXT;")
    
    # Add exchange_response if missing
    if "exchange_response" not in columns:
        print("Adding exchange_response column...")
        cursor.execute("ALTER TABLE bot_signals ADD COLUMN exchange_response TEXT;")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
