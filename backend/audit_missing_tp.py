import asyncio
import os
import sys

# Set up paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    try:
        from app.core.exchange import exchange_manager

        symbol = "1000PEPEUSDC"
        order_id = "7367522874"

        print(f"Auditing order {order_id} for {symbol}...")
        order = await exchange_manager.fetch_order_raw(symbol, order_id)
        
        if not order:
            print("Order not found on Binance.")
            return

        entry_price = order.get('average') or order.get('price')
        amount = order.get('amount')
        side = order.get('side')
        status = order.get('status')

        print(f"--- ORDER AUDIT ---")
        print(f"Status: {status}")
        print(f"Side: {side}")
        print(f"Amount: {amount}")
        print(f"Avg Entry Price: {entry_price}")
        
        # Calculate 1% TP target
        target_tp = float(entry_price) * 1.01 if side == 'buy' else float(entry_price) * 0.99
        print(f"Suggested 1% TP Price: {target_tp}")
        
        # Check current open orders for this symbol
        print("Checking for existing TP orders...")
        open_orders = await exchange_manager.fetch_open_orders(symbol)
        
        if open_orders:
            for oo in open_orders:
                print(f"Found Open Order: ID={oo['id']} Side={oo['side']} Qty={oo['amount']} Price={oo['price']}")
        else:
            print("No open orders found for this symbol.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
