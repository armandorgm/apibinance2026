import asyncio
from app.core.exchange import exchange_manager
import json

async def main():
    try:
        exchange = await exchange_manager.get_exchange()
        print("Checking Open Positions...")
        positions = await exchange_manager.get_open_positions()
        active_symbols = [p.get('symbol') for p in positions]
        print(f"Active Symbols: {active_symbols}")
        
        if not active_symbols:
            # Fallback to the symbol from user screenshot if no positions
            active_symbols = ["1000PEPE/USDC:USDC"]
            
        print("\nInvestigating orders...")
        
        tp_total = 0
        sl_total = 0
        
        for symbol in active_symbols:
            orders = await exchange_manager.fetch_open_orders(symbol)
            print(f"\n--- Symbol: {symbol} ({len(orders)} orders) ---")
            
            for o in orders:
                o_type = str(o.get('type', '')).upper()
                info = o.get('info', {})
                o_algo_type = str(info.get('algoType', '')).upper()
                raw_order_type = str(info.get('orderType', '')).upper()
                side = o.get('side')
                amount = o.get('amount')
                price = o.get('price')
                
                is_tp = "TAKE_PROFIT" in o_type or "TAKE_PROFIT" in o_algo_type or "TAKE_PROFIT" in raw_order_type
                is_sl = ("STOP" in o_type or "STOP" in o_algo_type or "STOP" in raw_order_type) and "TRAILING" not in o_type and "TRAILING" not in raw_order_type
                
                status = "BASIC"
                if is_tp: 
                    tp_total += 1
                    status = "TP"
                elif is_sl: 
                    sl_total += 1
                    status = "SL"
                elif "TRAILING" in o_type or "TRAILING" in raw_order_type:
                    status = "TRAILING"
                
                print(f"[{status}] {side} {amount} @ {price} | Algo: {o_algo_type} | Raw: {raw_order_type}")

        print("\n--- FINAL AUDIT FOR ACCOUNT ---")
        print(f"Total Take Profit (TP): {tp_total}")
        print(f"Total Stop Loss (SL): {sl_total}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if exchange_manager._exchange:
            await exchange_manager._exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
