
import asyncio
import os
from app.core.exchange import exchange_manager

async def main():
    symbol = "1000PEPE/USDC:USDC"
    exchange = await exchange_manager.get_exchange()
    await exchange.load_markets()
    market = exchange.market(symbol)
    print(f"Market Info for {symbol}:")
    print(f"  Precision: {market['precision']}")
    print(f"  Limits: {market['limits']}")
    
    amount = 1302.0
    price = 0.0038441
    qty_str = exchange.amount_to_precision(symbol, amount)
    print(f"  amount_to_precision({amount}) -> {qty_str}")
    
    # Try with direct CCXT logic
    print(f"  Manual calc: {amount} / {price} = {amount / price}")

if __name__ == "__main__":
    # Ensure env vars are set if needed, or rely on existing config
    asyncio.run(main())
