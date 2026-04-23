import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def main():
    load_dotenv(dotenv_path='backend/.env')
    exchange = ccxt.binance()
    
    print("--- Buscando CUALQUIER método que contenga 'openorders' ---")
    methods = [m for m in dir(exchange) if 'openorders' in m.lower()]
    for m in methods:
        print(f" - {m}")

    print("\n--- Buscando CUALQUIER método que contenga 'algo' ---")
    methods = [m for m in dir(exchange) if 'algo' in m.lower()]
    for m in methods:
        # Filtrar los de minería para limpiar ruido
        if 'mining' not in m.lower():
            print(f" - {m}")
            
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
