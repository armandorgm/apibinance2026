import sqlite3
import os

db_path = "f:/apibinance2026/backend/binance_tracker_v3.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Checking for column 'custom_profit_pc' in 'bot_pipeline_processes'...")
        cursor.execute("PRAGMA table_info(bot_pipeline_processes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'custom_profit_pc' not in columns:
            print("Adding column 'custom_profit_pc'...")
            cursor.execute("ALTER TABLE bot_pipeline_processes ADD COLUMN custom_profit_pc REAL")
            print("Column added successfully.")
        else:
            print("Column 'custom_profit_pc' already exists.")
            
        conn.commit()
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
