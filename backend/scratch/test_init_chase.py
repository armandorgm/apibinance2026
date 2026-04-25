
import asyncio
import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.services.chase_v2_service import chase_v2_service
from app.core.exchange import exchange_manager

async def test_init_chase():
    symbol = "1000PEPE/USDC:USDC"
    side = "buy"
    amount = 5.01
    print(f"Testing init_chase for: {symbol}")
    try:
        # We need to ensure stream_manager is started because init_chase depends on it
        from app.core.stream_service import stream_manager
        await stream_manager.start()
        
        res = await chase_v2_service.init_chase(
            symbol=symbol,
            side=side,
            amount=amount,
            profit_pc=0.005
        )
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await exchange_manager.close()
        from app.core.stream_service import stream_manager
        await stream_manager.stop()

if __name__ == "__main__":
    asyncio.run(test_init_chase())
