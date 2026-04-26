
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from backend.app.core.exchange import exchange_manager

async def check_limits():
    symbol = "1000PEPE/USDC:USDC"
    await exchange_manager.get_exchange()
    exchange = await exchange_manager.get_exchange()
    await exchange.load_markets()
    
    market = exchange.markets.get(symbol)
    if not market:
        print(f"Market {symbol} not found")
        return
        
    print(f"Limits for {symbol}:")
    print(f"Precision: {market.get('precision')}")
    print(f"Limits: {market.get('limits')}")
    
    price = 0.003887
    min_safe = await exchange_manager.get_safe_min_notional_qty(symbol, price)
    print(f"Price: {price}")
    print(f"Min Safe Qty: {min_safe}")
    print(f"Calculated Notional: {min_safe * price}")

if __name__ == "__main__":
    asyncio.run(check_limits())
