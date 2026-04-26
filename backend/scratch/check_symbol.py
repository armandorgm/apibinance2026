import asyncio
import ccxt.pro as ccxt
from app.core.config import settings

async def main():
    exchange = ccxt.binanceusdm({
        'apiKey': settings.BINANCE_API_KEY,
        'secret': settings.BINANCE_API_SECRET,
    })
    try:
        markets = await exchange.load_markets()
        symbol = '1000PEPE/USDC:USDC'
        if symbol in markets:
            market = markets[symbol]
            print(f"Symbol: {symbol}")
            print(f"ID: {market['id']}")
            print(f"Base: {market['base']}")
            print(f"Quote: {market['quote']}")
            print(f"Settlement: {market['settle']}")
        else:
            print(f"Symbol {symbol} not found in markets.")
            # Search for similar
            for s in markets.keys():
                if '1000PEPE' in s and 'USDC' in s:
                    print(f"Found similar: {s} -> ID: {markets[s]['id']}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    import os
    import sys
    # Add backend to path
    sys.path.append(os.getcwd())
    asyncio.run(main())
