import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def main():
    load_dotenv(dotenv_path='backend/.env')
    exchange = ccxt.binance()
    
    print(f"--- Buscando métodos 'fapi' + 'algo' ---")
    methods = [m for m in dir(exchange) if ('fapi' in m.lower() and 'algo' in m.lower())]
    for m in methods:
        print(f" - {m}")
        
    print(f"\n--- Probando fapiPrivateGetAlgoOpenOrders con guiones o variaciones ---")
    # A veces CCXT usa guiones bajos o camelCase
    # Intentemos ver si hay fapiPrivateGetAlgoOpenOrders
    
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
