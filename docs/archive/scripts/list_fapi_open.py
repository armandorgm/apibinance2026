import asyncio
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

async def main():
    load_dotenv(dotenv_path='backend/.env')
    exchange = ccxt.binance()
    
    print(f"--- Listando métodos que contienen 'fapi' y 'open' ---")
    methods = [m for m in dir(exchange) if ('fapi' in m.lower() and 'open' in m.lower())]
    for m in methods:
        print(f" - {m}")
        
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
