import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.binance_native import BinanceNativeEngine

async def list_native_symbols():
    load_dotenv("backend/.env")
    engine = BinanceNativeEngine()
    
    # Use exchangeInfo to get all symbols
    try:
        # We can use the low-level client if accessible, or just try to fetch something broad
        # BinanceNativeEngine has self.client
        info = engine.client.exchange_info()
        symbols = [s['symbol'] for s in info['symbols']]
        
        pepe_symbols = [s for s in symbols if "PEPE" in s]
        print(f"PEPE related symbols in Binance Native: {pepe_symbols}")
        
        # Also check for USDC settlement
        usdc_symbols = [s for s in symbols if "USDC" in s]
        print(f"Total USDC symbols: {len(usdc_symbols)}")
        if usdc_symbols:
            print(f"Sample USDC symbols: {usdc_symbols[:5]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_native_symbols())
