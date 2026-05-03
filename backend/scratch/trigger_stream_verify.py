import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.stream_service import stream_manager

async def trigger_subscription():
    print("Triggering subscription for 1000PEPEUSDC...")
    stream_manager.subscribe("1000PEPEUSDC")
    await stream_manager.start()
    
    # Wait for some ticks
    for i in range(20):
        print(f"Cycle {i}...")
        await asyncio.sleep(1)
        # Check current_prices
        prices = stream_manager.current_prices
        if prices:
            print(f"LATEST PRICES: {prices}")
            break
    
    await stream_manager.stop()

if __name__ == "__main__":
    asyncio.run(trigger_subscription())
