import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def test():
    symbol = "1000PEPEUSDC"
    norm = await exchange_manager.normalize_symbol(symbol)
    print(f"Raw: {symbol} -> Norm: {norm}")
    
    market_id = await exchange_manager.get_market_id(norm)
    print(f"Norm: {norm} -> Market ID: {market_id}")

if __name__ == "__main__":
    asyncio.run(test())
