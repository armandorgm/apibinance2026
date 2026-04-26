import asyncio
import os
import sys

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("app").setLevel(logging.DEBUG)
logging.getLogger("test_leverage").setLevel(logging.DEBUG)
logger = logging.getLogger("test_leverage")

from dotenv import load_dotenv

# Load .env from backend folder
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.exchange import exchange_manager
from app.core.config import settings

async def test_leverage():
    print("--- Testing Leverage Detection ---")
    # Test with a symbol that likely has a position or at least exists
    symbol = "1000PEPE/USDT:USDT" 
    notional = 100.0
    
    print(f"Testing symbol: {symbol}")
    result = await exchange_manager.check_margin_availability(symbol, notional)
    print(f"Result: {result}")
    print("----------------------------------")

if __name__ == "__main__":
    asyncio.run(test_leverage())
