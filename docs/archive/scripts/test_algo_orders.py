import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {
            'defaultType': 'future',
        }
    })

    symbol = '1000PEPE/USDC:USDC'
    
    print(f"--- Probando fetch_open_orders con algoType=CONDITIONAL ---")
    try:
        orders = await exchange.fetch_open_orders(symbol, params={'algoType': 'CONDITIONAL'})
        print(f"Encontradas {len(orders)} órdenes con fetch_open_orders(algoType=CONDITIONAL)")
        if orders:
            print(orders[0])
    except Exception as e:
        print(f"Error en fetch_open_orders: {e}")

    print(f"\n--- Probando método implícito fapiAlgoGetOpenOrders ---")
    try:
        # El endpoint es /fapi/v1/algo/openOrders
        # En CCXT los métodos implícitos siguen el patrón: apiName + Method + Path
        # fapi + Algo + Get + OpenOrders -> fapiAlgoGetOpenOrders
        res = await exchange.fapiAlgoGetOpenOrders()
        print(f"Encontradas {len(res)} órdenes con fapiAlgoGetOpenOrders")
        if res:
            print(res[0])
    except Exception as e:
        print(f"Error en fapiAlgoGetOpenOrders: {e}")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
