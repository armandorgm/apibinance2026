import asyncio
import ccxt.pro as ccxt

async def test_ccxt_pro_binance():
    exchange = ccxt.binance({
        'apiKey': '', # No keys needed for ticker
        'secret': '',
        'enableRateLimit': True,
        'options': {'defaultType': 'future'},
    })
    
    symbol = '1000PEPE/USDC:USDC'
    print(f"Watching {symbol}...")
    
    try:
        # Test watch_ticker
        ticker = await exchange.watch_ticker(symbol)
        print("TICKER RECEIVED:")
        print(f"  Bid: {ticker.get('bid')}")
        print(f"  Ask: {ticker.get('ask')}")
        print(f"  Last: {ticker.get('last')}")
        
        # Test watch_bids_asks
        print("\nWatching Bids/Asks...")
        ba = await exchange.watch_bids_asks([symbol])
        print("BIDS/ASKS RECEIVED:")
        print(ba[symbol])
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(test_ccxt_pro_binance())
