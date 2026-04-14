import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def main():
    # Cargar .env desde backend
    load_dotenv(dotenv_path='backend/.env')
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key:
        print("API Key no encontrada en backend/.env")
        return

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {
            'defaultType': 'future',
        }
    })

    print(f"--- Buscando métodos 'algo' en CCXT Binance ---")
    methods = [m for m in dir(exchange) if 'algo' in m.lower()]
    for m in methods:
        print(f" - {m}")

    print(f"\n--- Probando fapiPrivateGetAlgoOpenOrders ---")
    try:
        # Endpoint: GET /fapi/v1/algo/openOrders
        # CCXT pattern: api + Method + Path
        res = await exchange.fapiPrivateGetAlgoOpenOrders()
        print(f"Resultado fapiPrivateGetAlgoOpenOrders (primero de {len(res)}):")
        if res:
            # El resultado suele tener una clave 'orders' o ser una lista directa
            print(res)
    except Exception as e:
        print(f"Error en fapiPrivateGetAlgoOpenOrders: {e}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
