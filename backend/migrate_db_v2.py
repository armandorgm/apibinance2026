import sqlite3
import os

def migrate():
    # Try different common paths for the DB
    db_paths = [
        "backend/binance_tracker_v3.db",
        "binance_tracker_v3.db",
        "backend/app/db/binance_tracker_v3.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
            
    if not db_path:
        print(f"Database not found in common locations. Checked: {db_paths}")
        return

    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(bot_pipeline_processes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "handler_type" not in columns:
            print("Adding handler_type column to bot_pipeline_processes...")
            cursor.execute("ALTER TABLE bot_pipeline_processes ADD COLUMN handler_type VARCHAR(50)")
            
            # Backfill based on sub_status or originator
            print("Backfilling handler_type for existing records...")
            cursor.execute("UPDATE bot_pipeline_processes SET handler_type = 'CHASE_V2' WHERE originator = 'CHASE_V2_SERVICE'")
            cursor.execute("UPDATE bot_pipeline_processes SET handler_type = 'NATIVE_OTO' WHERE sub_status LIKE '%NATIVE%'")
            cursor.execute("UPDATE bot_pipeline_processes SET handler_type = 'ADAPTIVE_OTO' WHERE handler_type IS NULL")
            
            conn.commit()
            print("Migration successful.")
        else:
            print("Column handler_type already exists.")

    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
