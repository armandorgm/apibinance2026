import asyncio
import os
import sys
# Add backend to path to import app modules
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def check_order():
    symbol = "1000PEPEUSDC"
    order_id = "7378054921"
    try:
        print(f"Checking order {order_id} for {symbol} on Binance...")
        order = await exchange_manager.fetch_order_raw(symbol, order_id)
        print(f"Status: {order.get('status')}")
        print(f"Filled: {order.get('filled')}")
        print(f"Remaining: {order.get('remaining')}")
        print(f"Price: {order.get('price')}")
        print(f"Full Response: {order}")
    except Exception as e:
        print(f"Error checking order: {e}")

if __name__ == "__main__":
    asyncio.run(check_order())
