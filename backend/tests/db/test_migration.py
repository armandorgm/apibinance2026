import os
import sqlite3
import shutil
from app.db.database import create_db_and_tables
from app.core.config import settings

def test_migration_robustness():
    print("\n--- Testing Migration Robustness ---")
    
    # 1. Prepare temp DB path
    temp_db = "migration_test.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)
        
    # 2. Create DB with incomplete bot_signals table
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE bot_signals (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            rule_triggered TEXT,
            action_taken TEXT,
            params_snapshot TEXT,
            success BOOLEAN,
            error_message TEXT,
            timestamp INTEGER,
            created_at DATETIME
        );
    """)
    conn.commit()
    conn.close()
    print(f"Created {temp_db} without exchange columns.")
    
    # 3. Patch settings.DATABASE_URL temporarily
    old_url = settings.DATABASE_URL
    settings.DATABASE_URL = f"sqlite:///./{temp_db}"
    
    # I also need to make sure the database.py's 'engine' uses this new URL.
    # Since 'engine' is global, it might have been initialized.
    # But 'create_db_and_tables' extracts DB name from settings.DATABASE_URL directly.
    
    try:
        # 4. Run migration
        create_db_and_tables()
        print("Migration logic executed.")
        
        # 5. Verify columns
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(bot_signals);")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()
        
        if "exchange_request" in columns and "exchange_response" in columns:
            print("SUCCESS: Columns were added through migration.")
        else:
            print(f"FAILURE: Columns missing. Current columns: {columns}")
            
    finally:
        # Restore settings
        settings.DATABASE_URL = old_url
        if os.path.exists(temp_db):
             os.remove(temp_db)

if __name__ == "__main__":
    test_migration_robustness()
