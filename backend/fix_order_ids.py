import sqlite3
import os
from datetime import datetime

def fix_order_ids():
    db_path = 'backend/binance_tracker.db'
    if not os.path.exists(db_path):
        db_path = 'binance_tracker.db'  # fallback
        
    print(f"--- [CLEANUP] Using database: {os.path.abspath(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Nullify 'None' or empty strings in fills
        cursor.execute("UPDATE fills SET order_id = NULL WHERE order_id = 'None' OR order_id = ''")
        fills_changed = cursor.rowcount
        
        # 2. Nullify 'None' or empty strings in trades
        cursor.execute("UPDATE trades SET entry_order_id = NULL WHERE entry_order_id = 'None' OR entry_order_id = ''")
        cursor.execute("UPDATE trades SET exit_order_id = NULL WHERE exit_order_id = 'None' OR exit_order_id = ''")
        trades_changed = cursor.rowcount
        
        conn.commit()
        print(f"--- [CLEANUP] Updated {fills_changed} fills and {trades_changed} rows in trades table.")
        
        # 3. Trigger enrichment to regenerate IDs correctly
        # We can't import the app easily here, so we just set them to NULL and let the next sync handle it
        # Actually, if we set them to NULL, at runtime the Tracker will see 'None' (the Python value)
        # and trigger the fallback manual_... ID.
        
        conn.close()
        print("--- [CLEANUP] Success. Please refresh the dashboard.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    fix_order_ids()
