import asyncio
import json
import time
from app.core.exchange import exchange_manager

async def main():
    """
    Fetches trades using the ExchangeManager and prints them.
    """
    # Symbols to check
    symbols = ['1000PEPE/USDC:USDC']
    
    # Get the exchange instance from the manager
    exchange = exchange_manager.get_exchange()
    
    # Ensure markets are loaded
    exchange.load_markets()
    
    for sym in symbols:
        try:
            # Use the exchange_manager to fetch trades
            # Calculate the timestamp for 15 days ago in milliseconds
            days_ago = 15
            since_timestamp = int((time.time() - (days_ago * 24 * 60 * 60)) * 1000)

            trades = await exchange_manager.fetch_my_trades(
                symbol=sym,
                since=since_timestamp,
                limit=1000
            )
            
            print(f"{sym} -> Found {len(trades)} trades.")
            
            if trades:
                for trade in trades:
                    # Datetime is already included in the response from fetch_my_trades
                    print(json.dumps(trade, indent=2))
                    
        except Exception as e:
            print(f"Error fetching trades for {sym}: {type(e).__name__} - {e}")

if __name__ == "__main__":
    # Ensure the script can be run from the backend directory
    # For example: python check_trades.py
    # This setup assumes that the script is run from a context where the 'app' module is accessible.
    # If running from the root of the project, you might need to adjust PYTHONPATH.
    # export PYTHONPATH=$PYTHONPATH:./backend
    
    print("--- Starting trade check using ExchangeManager ---")
    asyncio.run(main())
    print("--- Trade check finished ---")
