
import asyncio
import os
import sys
# Add backend to path
sys.path.append(os.getcwd())

from sqlmodel import Session, select
from app.db.database import engine, Fill, Trade
from app.services.tracker_logic import TradeTracker

async def find_orphans():
    print("--- Finding Orphan Sells ---")
    # We'll check for a few common symbols or all of them
    symbols = ["1000PEPEUSDC", "PEPE/USDT", "BTC/USDT"] # Add more as needed
    
    with Session(engine) as session:
        # Get all distinct symbols from fills
        all_symbols = session.exec(select(Fill.symbol).distinct()).all()
        print(f"Checking symbols: {all_symbols}")
        
        for symbol in all_symbols:
            tracker = TradeTracker(symbol)
            open_positions = tracker.compute_open_positions()
            
            orphans = [op for op in open_positions if op.get('is_orphan')]
            if orphans:
                print(f"\nSymbol: {symbol}")
                for o in orphans:
                    print(f"  Orphan Sell Found:")
                    print(f"    Timestamp: {o['entry_timestamp']}")
                    print(f"    DateTime: {o['entry_datetime']}")
                    print(f"    Price: {o['entry_price']}")
                    print(f"    Amount: {o['entry_amount']}")
                    print(f"    Order ID: {o.get('entry_order_id')}")

if __name__ == "__main__":
    asyncio.run(find_orphans())
