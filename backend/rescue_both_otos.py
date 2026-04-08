import asyncio
import os
import sys

# Set up paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def rescue():
    try:
        from app.core.exchange import exchange_manager
        
        orders_to_rescue = ["7367522874", "7367565574"]
        symbol = "1000PEPEUSDC"
        
        for order_id in orders_to_rescue:
            print(f"\n--- Rescuing Order {order_id} ---")
            order = await exchange_manager.fetch_order_raw(symbol, order_id)
            
            if not order:
                print(f"Order {order_id} not found.")
                continue
            
            status = order.get('status')
            side = order.get('side')
            amount = order.get('amount')
            avg_price = order.get('average') or order.get('price')
            
            print(f"Status: {status}, Side: {side}, Amount: {amount}, Entry: {avg_price}")
            
            if status != 'closed':
                print(f"Order {order_id} is still {status}. Not filling TP yet.")
                continue
            
            # Calculate TP
            tp_side = "sell" if side == "buy" else "buy"
            tp_price = float(avg_price) * 1.01 if side == "buy" else float(avg_price) * 0.99
            
            # Format
            qty_str = await exchange_manager.amount_to_precision(symbol, float(amount))
            price_str = await exchange_manager.price_to_precision(symbol, tp_price)
            
            print(f"Placing TP: {tp_side} {qty_str} at {price_str}")
            
            # Check for existing TP
            open_orders = await exchange_manager.fetch_open_orders(symbol)
            already_placed = False
            for oo in open_orders:
                if oo['side'] == tp_side and abs(float(oo['amount']) - float(amount)) < 1.0:
                    print(f"TP already appears to be placed: ID={oo['id']}")
                    already_placed = True
                    break
            
            if not already_placed:
                new_tp = await exchange_manager.create_order(
                    symbol=symbol,
                    side=tp_side,
                    amount=qty_str,
                    price=price_str,
                    order_type="limit"
                )
                print(f"TP PLACED! ID: {new_tp['id']}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(rescue())
