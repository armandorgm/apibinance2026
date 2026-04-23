import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.exchange import exchange_manager

async def test():
    try:
        e = await exchange_manager.get_exchange()
        await e.load_markets()
        
        # Search for 1000PEPE symbols
        pepe_symbols = [s for s in e.symbols if '1000PEPE' in s]
        print(f"Found PEPE symbols: {pepe_symbols}")
        
        if not pepe_symbols:
            print("No 1000PEPE symbols found!")
            return

        # Use the exact name provided by the user
        target = '1000PEPEUSDC'
        
        print(f"Testing with: {target}")
        
        # Trigger Manual Action via standard API (Internal Call simulation)
        from app.services.pipeline_engine.actions import AdaptiveOTOScalingAction
        action = AdaptiveOTOScalingAction()
        
        # We need context_params with current price
        ticker = await e.fetch_ticker(target)
        current_price = ticker['last']
        
        params = {"side": "buy", "amount": 5.01} # $5.01 is enough for PEPE
        context = {"current_price": current_price}
        
        print(f"Executing Adaptive OTO for {target} at {current_price}...")
        res = await action.execute(target, params, context)
        
        print(f"RESULT: {res}")
        
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        print(traceback.format_exc())
    finally:
        await (await exchange_manager.get_exchange()).close()

if __name__ == "__main__":
    asyncio.run(test())
