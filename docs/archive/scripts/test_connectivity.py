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
    })

    print(f"--- Probando fapiPrivateGetOpenOrders (estándar) ---")
    try:
        res = await exchange.fapiPrivateGetOpenOrders()
        print(f"Success! Encontradas {len(res)} órdenes abiertas estándar.")
    except Exception as e:
        print(f"Error en fapiPrivateGetOpenOrders: {e}")

    print(f"\n--- Probando fapiPrivateGetAlgoOpenOrders ---")
    try:
        # Algunos CCXT mapean fapi/v1/algo/openOrders -> fapiPrivateGetAlgoOpenOrders
        res = await exchange.fapiPrivateGetAlgoOpenOrders()
        print(f"Success! Encontradas {len(res)} órdenes algo.")
    except Exception as e:
        print(f"Error en fapiPrivateGetAlgoOpenOrders: {e}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
