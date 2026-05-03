import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def main():
    load_dotenv(dotenv_path='backend/.env')
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {
            'defaultType': 'future',
        }
    })

    print(f"--- Probando fetch_open_orders(SYMBOL=None, algoType=CONDITIONAL) ---")
    try:
        # Algunos CCXT usan el presence de algoType para switchar al endpoint de Algo
        orders = await exchange.fetch_open_orders(symbol=None, params={'algoType': 'CONDITIONAL'})
        print(f"Encontradas {len(orders)} órdenes.")
        if orders:
            print(orders[0])
    except Exception as e:
        print(f"Error: {e}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
