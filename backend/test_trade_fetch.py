
import asyncio
from app.core.exchange import exchange_manager
import os

# This test will fail if the .env file is not configured with API keys.
# We will assume it is for the purpose of this test.
# We also need a symbol that is likely to have trades.
TEST_SYMBOL = 'BTC/USDT' 

async def main():
    """
    Tests the fetch_my_trades method from the ExchangeManager.
    This is a simple test to ensure the method executes without raising
    a timestamp-related error.
    """
    print(f"--- [TEST] Testing fetch_my_trades for symbol {TEST_SYMBOL} ---")
    try:
        # Use the global exchange_manager instance
        trades = await exchange_manager.fetch_my_trades(symbol=TEST_SYMBOL, limit=10)
        
        print(f"--- [SUCCESS] fetch_my_trades executed successfully.")
        print(f"--- Found {len(trades)} trades for {TEST_SYMBOL}.")
        
        if trades:
            # Print some info about the first trade to show it worked
            first_trade = trades[0]
            print(f"--- First trade details: ID={first_trade.get('id')}, Datetime={first_trade.get('datetime')}")

    except Exception as e:
        print(f"--- [ERROR] An error occurred during the test: {e}")
        # Re-raise the exception to make it clear the test failed
        raise e


if __name__ == "__main__":
    # Setup asyncio event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
