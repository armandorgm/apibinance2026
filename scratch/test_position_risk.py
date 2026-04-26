import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.binance_native import BinanceNativeEngine

async def test_position_risk():
    load_dotenv("backend/.env")
    engine = BinanceNativeEngine()
    
    print("Fetching ALL position risks (symbol=None)...")
    risks = await engine.get_position_risk(None)
    print(f"Total entries: {len(risks)}")
    
    pepe_risks = [r for r in risks if "PEPE" in r['symbol']]
    for r in pepe_risks:
        print(f"Symbol: {r['symbol']}, Leverage: {r['leverage']}, MarginType: {r['marginType']}")

    print("\nFetching SPECIFIC position risk for 1000PEPEUSDC...")
    try:
        risk = await engine.get_position_risk("1000PEPEUSDC")
        print(f"Result for 1000PEPEUSDC: {risk}")
    except Exception as e:
        print(f"Error for 1000PEPEUSDC: {e}")

if __name__ == "__main__":
    asyncio.run(test_position_risk())
