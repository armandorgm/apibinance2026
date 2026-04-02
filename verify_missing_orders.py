import asyncio
import json
import os
import sys
from datetime import datetime

# Adjust sys.path to include app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.exchange import exchange_manager

async def verify_orders():
    print(f"--- [DEBUG] Inciando Verificación de Órdenes a las {datetime.utcnow()} ---")
    
    try:
        exchange = await exchange_manager.get_exchange()
        
        # 1. Fetch Standard Open Orders
        print("[VERIFY] Solicitando /v1/openOrders (Implementado)...")
        std_orders = await exchange.fapiPrivateGetOpenOrders()
        print(f"[RESULT] /v1/openOrders retornó {len(std_orders)} órdenes.")
        if std_orders:
            for o in std_orders:
                print(f"  - [{o['symbol']}] ID: {o['orderId']} | Type: {o['type']} | Side: {o['side']} | P: {o['price']}")
        
        # 2. Fetch Algo Open Orders (New documented endpoint)
        print("\n[VERIFY] Solicitando /v1/openAlgoOrders (Documentado)...")
        try:
            algo_res = await exchange.fapiPrivateGetOpenAlgoOrders()
            # Extract orders from response
            algo_orders = algo_res if isinstance(algo_res, list) else algo_res.get('orders', [])
            print(f"[RESULT] /v1/openAlgoOrders retornó {len(algo_orders)} órdenes.")
            if algo_orders:
                for o in algo_orders:
                    # Algo order structure might differ
                    o_id = o.get('algoId') or o.get('orderId')
                    print(f"  - [{o['symbol']}] ID: {o_id} | Type: {o.get('type') or 'ALGO'} | Side: {o['side']} | SL/TP: {o.get('stopPrice') or o.get('triggerPrice')}")
        except Exception as e:
            print(f"[ERROR] Error al consultar Algo Orders: {e}")
            
    except Exception as e:
        print(f"[ERROR] Fallo general de conexión: {e}")
    finally:
        await exchange_manager.close()

if __name__ == "__main__":
    asyncio.run(verify_orders())
