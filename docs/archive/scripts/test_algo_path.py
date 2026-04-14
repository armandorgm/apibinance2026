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

    print(f"--- Probando fapiPrivateGet('algo/openOrders') ---")
    try:
        # El endpoint completo es GET /fapi/v1/algo/openOrders
        # En CCXT fapiPrivateGet suele inyectar /fapi/v1/ automáticamente
        res = await exchange.fapiPrivateGetAlgoOpenOrders()
    except Exception as e:
        print(f"Falló el directo, intentando vía fapiPrivateGet('algo/openOrders')...")
        try:
            res = await exchange.fapiPrivateGet('algo/openOrders')
            print(f"Success! Resultado:")
            print(res)
        except Exception as e2:
            print(f"Error en fapiPrivateGet('algo/openOrders'): {e2}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
