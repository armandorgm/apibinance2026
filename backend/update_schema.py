import sqlite3
import os

db_path = "backend/binance_tracker.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(bot_pipeline_processes)")
    columns = [c[1] for c in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add new columns if missing
    new_cols = [
        ("side", "TEXT DEFAULT 'buy'"),
        ("amount", "REAL DEFAULT 0.0"),
        ("last_order_price", "REAL")
    ]
    
    for col_name, col_type in new_cols:
        if col_name not in columns:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE bot_pipeline_processes ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    conn.close()
    print("Migration finished.")
else:
    print("DB not found at root, check backend/binance_tracker.db")
