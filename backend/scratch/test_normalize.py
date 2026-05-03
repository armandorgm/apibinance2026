
import asyncio
import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def test_normalize():
    symbol = "{{symbol}}"
    print(f"Testing normalization for: {symbol}")
    try:
        norm = await exchange_manager.normalize_symbol(symbol)
        print(f"Normalized: {norm}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_normalize())
