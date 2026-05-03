import asyncio
import json
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def debug_order():
    symbol = '1000PEPE/USDC:USDC'
    order_id = '7420911304'
    print(f"--- FETCHING ORDER {order_id} ---")
    
    # CCXT version
    order = await exchange_manager.fetch_order_raw(symbol, order_id)
    print("CCXT RAW Status:", order.get('status'))
    print("CCXT RAW Info Status:", order.get('info', {}).get('status'))
    print("CCXT Filled:", order.get('filled'))
    
    # Let's see the full 'info'
    print(json.dumps(order.get('info', {}), indent=2))

if __name__ == "__main__":
    asyncio.run(debug_order())
