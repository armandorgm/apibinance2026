import sqlite3
import os

def check_fills():
    # Try multiple common paths for the database
    paths = ['binance_tracker.db', '../backend/binance_tracker.db', 'backend/binance_tracker.db', '../binance_tracker.db']
    db_path = None
    for p in paths:
        if os.path.exists(p):
            db_path = p
            break
            
    if not db_path:
        print(f"Error: Database not found in {os.getcwd()} or typical child/parent paths.")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for empty or null order_id
        cursor.execute("SELECT trade_id, symbol, side, order_id, datetime FROM fills WHERE order_id IS NULL OR order_id = ''")
        rows = cursor.fetchall()
        
        print(f"Database used: {os.path.abspath(db_path)}")
        print(f"Total Fills in DB: {cursor.execute('SELECT COUNT(*) FROM fills').fetchone()[0]}")
        print(f"Fills with empty order_id: {len(rows)}")
        
        if rows:
            print("\nExample Fills with missing ID:")
            for r in rows[:10]:
                print(f"Trade ID: {r[0]} | Symbol: {r[1]} | Side: {r[2]} | Date: {r[4]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_fills()
