import asyncio
import sys
import os

# Set up paths
backend_path = os.path.abspath(os.path.join(os.getcwd(), 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.exchange import exchange_manager
from app.db.database import Fill, engine
from sqlmodel import Session, select

async def diagnose():
    try:
        print("--- BINANCE CONNECTIVITY DIAGNOSTIC ---")
        await exchange_manager.initialize()
        
        # 1. Check Balance (Futures)
        try:
            balance = await exchange_manager.exchange.fetch_balance({'type': 'future'})
            total_bal = {k: v for k, v in balance['total'].items() if v > 0}
            print(f"Active Account Assets: {total_bal}")
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return

        # 2. Check Positions
        try:
            positions = await exchange_manager.exchange.fetch_positions()
            active_pos = [p['symbol'] for p in positions if float(p.get('entryPrice', 0)) > 0]
            print(f"Active Positions: {active_pos}")
        except Exception as e:
            print(f"Error fetching positions: {e}")

        # 3. Check recent trades for a few symbols
        # If no symbol specified, check common ones or ones with balance
        symbols_to_check = ['BTC/USDT:USDT', 'ETH/USDT:USDT', '1000PEPE/USDC:USDC', '1000PEPE/USDT:USDT']
        if active_pos:
            symbols_to_check.extend(active_pos)
            
        print(f"Checking trade history for symbols: {list(set(symbols_to_check))}")
        
        for symbol in set(symbols_to_check):
            try:
                # Direct CCXT call to see raw data
                trades = await exchange_manager.exchange.fetch_my_trades(symbol, limit=50)
                print(f"  {symbol}: Found {len(trades)} recent trades on Binance.")
                if trades:
                    print(f"    Example: {trades[0]['side']} {trades[0]['amount']} @ {trades[0]['price']} on {trades[0]['datetime']}")
            except Exception as e:
                print(f"  {symbol}: Error or no data ({e})")

        print("-" * 40)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
