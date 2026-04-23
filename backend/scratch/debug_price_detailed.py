import asyncio
import os
import sys
import json

# Add backend to path
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def debug_ticker_detailed():
    symbols = ["1000PEPEUSDC", "BTCUSDT"]
    print(f"--- DETAILED TICKER DEBUG ---")
    
    try:
        exchange = await exchange_manager.get_exchange()
        print(f"Exchange Instance: {type(exchange)}")
        print(f"Options: {exchange.options}")
        
        for symbol in symbols:
            print(f"\n[SYMBOL: {symbol}]")
            norm = await exchange_manager.normalize_symbol(symbol)
            print(f"Normalized: {norm}")
            
            ticker = await exchange.fetch_ticker(norm)
            
            print(f"Unified Format:")
            print(f"  Ask:  {ticker.get('ask')}")
            print(f"  Bid:  {ticker.get('bid')}")
            print(f"  Last: {ticker.get('last')}")
            
            print(f"Raw Response (info):")
            # Usually info contains 'askPrice', 'bidPrice', 'lastPrice' etc from Binance
            info = ticker.get('info', {})
            print(json.dumps(info, indent=2))
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        # Closing is good practice
        # await exchange.close()
        pass

if __name__ == "__main__":
    asyncio.run(debug_ticker_detailed())
