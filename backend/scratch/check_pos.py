import asyncio
import os
import sys
# Add backend to path
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def check_position():
    await exchange_manager.initialize()
    symbol = "1000PEPEUSDC"
    try:
        # Fetch positions
        exchange = await exchange_manager.get_exchange()
        positions = await exchange.fetch_positions([symbol])
        
        for pos in positions:
            if float(pos.get('contracts', 0)) != 0:
                print(f"[POS] {pos['symbol']}: {pos['contracts']} ({pos['side']}) UnPnL: {pos['unrealizedPnl']}")
            else:
                print(f"[POS] {pos['symbol']}: No position.")
                
        # Also check open orders
        orders = await exchange_manager.fetch_open_orders(symbol)
        print(f"[ORDERS] {len(orders)} open orders found.")
        for o in orders:
            print(f"  - {o['id']} {o['side']} @ {o['price']}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        await exchange_manager.close()

if __name__ == "__main__":
    asyncio.run(check_position())
