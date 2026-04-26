
import sqlite3
import os

DB_PATH = "f:/apibinance2026/backend/binance_tracker_v3.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Adding column exit_order_id to bot_pipeline_processes...")
        cursor.execute("ALTER TABLE bot_pipeline_processes ADD COLUMN exit_order_id TEXT;")
        conn.commit()
        print("Success!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
