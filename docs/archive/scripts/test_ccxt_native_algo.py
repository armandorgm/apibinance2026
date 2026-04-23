import asyncio
import ccxt.async_support as ccxt
import json
import os
from dotenv import load_dotenv

# Load env from backend directory
load_dotenv('f:/apibinance2026/backend/.env')

async def main():
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'future'}
    })
    
    symbol = '1000PEPE/USDC:USDC'
    try:
        print(f"--- Probando CCXT fetch_open_orders NATIVO con params ---")
        # Algunos exchanges en CCXT mapean automáticamente si pasas el tipo correcto
        params = {'algoType': 'CONDITIONAL'}
        # Intentamos obtener las órdenes que el usuario dice que desaparecieron
        orders = await exchange.fetch_open_orders(symbol, params=params)
        
        print(f"Encontradas {len(orders)} órdenes.")
        if orders:
            print("Primer orden mapeada por CCXT:")
            print(json.dumps(orders[0], indent=2))
        
    except Exception as e:
        print(f"Error en prueba nativa: {e}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
