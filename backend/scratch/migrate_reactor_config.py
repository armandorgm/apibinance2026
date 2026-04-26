import sqlite3
import os

db_path = "binance_tracker_v3.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Adding total_cycles to reactor_bot_config...")
        cursor.execute("ALTER TABLE reactor_bot_config ADD COLUMN total_cycles INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        print(f"Skipping total_cycles: {e}")

    try:
        print("Adding last_duration to reactor_bot_config...")
        cursor.execute("ALTER TABLE reactor_bot_config ADD COLUMN last_duration FLOAT DEFAULT 0.0")
    except sqlite3.OperationalError as e:
        print(f"Skipping last_duration: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
