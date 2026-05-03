import asyncio
import sys
import os

# Set up paths
backend_path = os.path.abspath(os.path.join(os.getcwd(), 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.exchange import exchange_manager

async def diagnose():
    try:
        print("--- BINANCE ASSET & HISTORY CHECK ---")
        # ExchangeManager doesn't have initialize(), get_exchange() handles it
        await exchange_manager.get_exchange() 
        
        # 1. Check Balance (Futures)
        try:
            balance = await exchange_manager.fetch_balance()
            total_bal = {k: v for k, v in balance['total'].items() if v > 0}
            print(f"Active Account Assets: {total_bal}")
            
            if not total_bal:
                print("WARNING: Account balance is 0 for all assets. No trades possible?")
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return

        # 2. Check Positions
        try:
            positions = await exchange_manager.get_open_positions()
            print(f"Active Positions: {[p['symbol'] for p in positions]}")
        except Exception as e:
            print(f"Error fetching positions: {e}")

        # 3. Check for RECENT TRADES on ANY symbol (if possible)
        # We'll check the top 5 assets with balance
        assets = sorted(total_bal.items(), key=lambda x: x[1], reverse=True)[:5]
        for asset, val in assets:
            if asset in ['USDT', 'USDC', 'BNB']: continue # These are currencies, not symbols
            
            symbol = f"{asset}/USDT:USDT"
            try:
                trades = await exchange_manager.fetch_my_trades(symbol, limit=20)
                print(f"  {symbol}: Found {len(trades)} trades.")
            except:
                pass

        # Also check common ones
        for sym in ['BTC/USDT:USDT', 'ETH/USDT:USDT', '1000PEPE/USDC:USDC']:
            try:
                trades = await exchange_manager.fetch_my_trades(sym, limit=20)
                if trades:
                    print(f"  {sym}: Found {len(trades)} trades.")
            except:
                pass

        print("-" * 40)
        
    except Exception as e:
        print(f"DIAGNOSTIC FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
