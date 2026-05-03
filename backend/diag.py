import asyncio
import sys
import os

# This script is intended to be run from f:\apibinance2026\backend
# It will use the local .env

from app.core.exchange import exchange_manager

async def test():
    try:
        print("Initializing exchange...")
        exchange = await exchange_manager.get_exchange()
        
        print("Checking account history for ANY symbol...")
        # Since we can't fetch all trades at once easily with CCXT binance,
        # we check the most likely ones.
        targets = ['1000PEPE/USDC:USDC', 'BTC/USDT:USDT', 'ETH/USDT:USDT']
        
        for symbol in targets:
            try:
                print(f"Checking {symbol}...")
                trades = await exchange.fetch_my_trades(symbol, limit=20)
                if trades:
                    print(f"SUCCESS: Found {len(trades)} trades for {symbol}")
                    return
                else:
                    print(f"No trades for {symbol}")
            except Exception as e:
                print(f"Error checking {symbol}: {e}")
                
        print("No trades found in common symbols.")
        
        # Check positions as a fallback
        print("Checking positions...")
        pos = await exchange.fetch_positions()
        active = [p['symbol'] for p in pos if float(p.get('entryPrice', 0)) > 0]
        if active:
            print(f"Active positions found: {active}")
        else:
            print("No active positions found.")
            
    except Exception as e:
        print(f"Critical Diagnostic Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
