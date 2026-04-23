import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def debug_ticker():
    symbol = "1000PEPEUSDC"
    print(f"DEBUG: Fetching ticker for {symbol}...")
    try:
        ticker = await exchange_manager.fetch_ticker(symbol)
        print(f"DEBUG: Ticker keys: {list(ticker.keys())}")
        print(f"DEBUG: Ask: {ticker.get('ask')}")
        print(f"DEBUG: Bid: {ticker.get('bid')}")
        print(f"DEBUG: Last: {ticker.get('last')}")
        
        norm = await exchange_manager.normalize_symbol(symbol)
        print(f"DEBUG: Normalized: {norm}")
        
    except Exception as e:
        print(f"DEBUG: Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_ticker())
