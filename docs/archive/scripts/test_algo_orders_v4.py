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

    print(f"--- Probando sapi_get_algo_futures_openorders ---")
    try:
        res = await exchange.sapi_get_algo_futures_openorders()
        print(f"Resultado sapi_get_algo_futures_openorders:")
        print(res)
    except Exception as e:
        print(f"Error en sapi_get_algo_futures_openorders: {e}")

    print(f"\n--- Probando fapiPrivateGetAlgoOpenOrders con bypass ---")
    # Intentemos llamar al endpoint manualmente vía CCXT request si el método no existe
    try:
        # endpoint: algo/openOrders
        # api: fapi
        # method: GET
        res = await exchange.fapiPrivateGetAlgoOpenOrders()
        print(f"Resultado fapiPrivateGetAlgoOpenOrders:")
        print(res)
    except Exception as e:
        print(f"Error en fapiPrivateGetAlgoOpenOrders (bypass): {e}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
