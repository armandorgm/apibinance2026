import asyncio
import os
import sys

# Setup paths for backend import
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
env_path = os.path.join(os.getcwd(), 'backend', '.env')
print(f"Loading env from: {env_path}")
load_dotenv(env_path)

from app.core.exchange import exchange_manager
from app.core.logger import logger

async def test_margin_check():
    print("--- TESTING MARGIN CHECK ---")
    symbol = "BTCUSDT"
    
    # 1. Test with small amount (should pass if account has balance)
    small_amount = 10.0
    print(f"Testing small amount: ${small_amount}")
    res_pass = await exchange_manager.check_margin_availability(symbol, small_amount)
    print(f"Result: {res_pass}")
    
    # 2. Test with ridiculous amount (should fail)
    huge_amount = 1000000.0
    print(f"\nTesting huge amount: ${huge_amount}")
    res_fail = await exchange_manager.check_margin_availability(symbol, huge_amount)
    print(f"Result: {res_fail}")
    
    if not res_fail.get("available") and res_pass.get("available"):
        print("\nSUCCESS: Margin check logic is working correctly.")
    else:
        print("\nWARNING: Margin check results unexpected. Verify account balance.")

if __name__ == "__main__":
    asyncio.run(test_margin_check())
