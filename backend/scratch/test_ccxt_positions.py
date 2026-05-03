import asyncio
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.exchange import exchange_manager

async def test():
    try:
        # Initialize exchange
        await exchange_manager.get_exchange()
        
        symbol = "1000PEPE/USDC:USDC"
        print(f"Fetching positions for {symbol} via CCXT...")
        positions = await exchange_manager.get_open_positions(symbol)
        
        if positions:
            for p in positions:
                print(f"Symbol: {p.get('symbol')}")
                print(f"Contracts: {p.get('contracts')}")
                print(f"Leverage: {p.get('leverage')}")
                print(f"Side: {p.get('side')}")
                print(f"Raw info keys: {list(p.get('info', {}).keys())}")
                if 'leverage' not in p:
                    print("WARNING: 'leverage' field missing in CCXT parsed response.")
                    # Check info
                    info = p.get('info', {})
                    print(f"Leverage in info: {info.get('leverage')}")
        else:
            print("No open positions found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
