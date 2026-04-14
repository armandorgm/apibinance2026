import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.exchange import exchange_manager

async def main():
    try:
        print("Checking positions...")
        p = await exchange_manager.get_open_positions()
        print(f"Active Positions: {len(p)}")
        for pos in p:
            print(f"Symbol: {pos.get('symbol')} | Contracts: {pos.get('contracts')} | Side: {pos.get('side')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if exchange_manager._exchange:
            await exchange_manager._exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
