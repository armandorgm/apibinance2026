import sqlite3
import os

db_path = os.path.join('backend', 'binance_tracker_v3.db')

def diagnose():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # List all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        print(f"Tables in DB: {tables}")
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table}: {count} rows")
            
            if count > 0 and table.lower() in ['fill', 'trade', 'fills', 'trades']:
                # Show sample data
                cur.execute(f"SELECT * FROM {table} LIMIT 1")
                print(f"    Sample from {table}: {cur.fetchone()}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
