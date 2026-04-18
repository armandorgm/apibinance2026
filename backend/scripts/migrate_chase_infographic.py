import sqlite3
import os

db_path = "f:/apibinance2026/backend/binance_tracker_v3.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add sub_status column
    try:
        cursor.execute("ALTER TABLE bot_pipeline_processes ADD COLUMN sub_status TEXT DEFAULT 'INIT'")
        print("Column sub_status added to bot_pipeline_processes")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column sub_status already exists.")
        else:
            print(f"Error adding sub_status: {e}")

    # Add finished_at column
    try:
        cursor.execute("ALTER TABLE bot_pipeline_processes ADD COLUMN finished_at DATETIME")
        print("Column finished_at added to bot_pipeline_processes")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column finished_at already exists.")
        else:
            print(f"Error adding finished_at: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
