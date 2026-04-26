import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.exchange import exchange_manager

async def test_margin_check():
    load_dotenv("backend/.env")
    symbol = "1000PEPE/USDC:USDC"
    current_price = 0.00001 # Dummy
    notional_usd = 20.0 # 20 USD notional
    
    print(f"Testing margin check for {symbol} with {notional_usd} USD notional...")
    try:
        margin_info = await exchange_manager.check_margin_availability(symbol, notional_usd)
        print(f"Margin Info: {margin_info}")
        
        # Verify normalization
        native = exchange_manager.get_native_symbol(symbol)
        print(f"Native symbol: {native}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_margin_check())
