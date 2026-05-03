import sys
import os

# Ensure backend directory is in the path
backend_path = os.path.abspath(os.path.join(os.getcwd(), 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.database import Fill, Trade, engine
from sqlmodel import Session, select

def main():
    try:
        with Session(engine) as session:
            fills = session.exec(select(Fill)).all()
            trades = session.exec(select(Trade)).all()
            
            print(f"--- DATABASE REPORT ---")
            print(f"Total Fills in DB: {len(fills)}")
            print(f"Total Trades in DB (Matched): {len(trades)}")
            
            if fills:
                symbols = sorted(list(set(f.symbol for f in fills)))
                print(f"Symbols found in Fills: {symbols}")
                
                # Check for a specific recent fill
                latest = sorted(fills, key=lambda x: x.timestamp, reverse=True)[0]
                print(f"Latest Fill: {latest.symbol} {latest.side} {latest.amount} at {latest.timestamp}")
            else:
                print("!!! Fills table is empty. Sync is required !!!")
                
            if trades:
                strategies = set(t.originator for t in trades) # Actually trades don't store strategy well, but let's see
                print(f"Total Matches: {len(trades)}")
            else:
                print("No matches (trades) found. This could mean logic didn't pair anything.")
            print("-" * 25)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
