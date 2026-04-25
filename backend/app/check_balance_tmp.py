
import asyncio
from app.core.binance_native import binance_native

async def main():
    print("Checking Position Risk for 1000PEPEUSDC...")
    try:
        res = await binance_native.get_position_risk("1000PEPEUSDC")
        print(f"Position Risk: {res}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
