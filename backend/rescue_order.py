import asyncio
import os
import sys

# Set up paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    try:
        from app.core.exchange import exchange_manager
        from app.db.database import get_session_direct, BotPipelineProcess
        from datetime import datetime

        symbol = "1000PEPEUSDC"
        order_id = "7367522874"

        print(f"Checking order {order_id} for {symbol}...")
        order = await exchange_manager.fetch_order_raw(symbol, order_id)
        
        if not order:
            print("Order not found on Binance.")
            return

        print(f"Order Success! Status: {order.get('status')}, Side: {order.get('side')}, Amount: {order.get('amount')}")

        if order.get('status') == 'open':
            print("Order is OPEN. Inserting into DB to resume chase...")
            with get_session_direct() as session:
                # Check if already exists
                existing = session.query(BotPipelineProcess).filter(BotPipelineProcess.entry_order_id == order_id).first()
                if existing:
                    print(f"Process already exists for ID {order_id}. Doing nothing.")
                    return

                process = BotPipelineProcess(
                    symbol=symbol,
                    entry_order_id=order_id,
                    side=order.get('side'),
                    amount=float(order.get('amount')),
                    last_tick_price=float(order.get('price')),
                    last_order_price=float(order.get('price')),
                    status="CHASING",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(process)
                session.commit()
                print(f"Successfully inserted! Bot should now start chasing this order.")
        else:
            print(f"Order is not OPEN (Status: {order.get('status')}). No action taken.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
