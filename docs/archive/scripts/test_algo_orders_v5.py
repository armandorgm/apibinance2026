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

    print(f"--- Probando petición manual via exchange.request ---")
    try:
        # Endpoint: GET /fapi/v1/algo/openOrders
        # En CCXT: request(path, type, method, params, headers, body, config)
        # El path 'algo/openOrders' se une con el prefijo de la sección (v1)
        res = await exchange.request('algo/openOrders', 'fapi', 'GET', {}, None, None, {'api-type': 'private'})
        print(f"Resultado exchange.request:")
        print(res)
    except Exception as e:
        print(f"Error en exchange.request: {e}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
