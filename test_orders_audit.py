import asyncio
import time
from datetime import datetime
from app.core.exchange import exchange_manager

async def test_orders_audit():
    print(f"--- [AUDIT] Inciando Test de Órdenes Abiertas vs Documento Técnico ---")
    
    try:
        # 1. Server Time Sync Check
        exchange = await exchange_manager.get_exchange()
        server_time_res = await exchange.fapiPublicGetTime()
        server_time = server_time_res['serverTime']
        local_time = int(time.time() * 1000)
        diff = server_time - local_time
        
        print(f"[TIME] Server Time: {server_time}")
        print(f"[TIME] Local Time:  {local_time}")
        print(f"[TIME] Desfase:     {diff}ms (Umbral recvWindow: 5000ms)")
        
        # 2. Fetch Standard Open Orders (v1/openOrders)
        print("\n[FETCH] Solicitando Open Orders estándar (v1/openOrders)...")
        standard_orders = await exchange.fetch_open_orders()
        print(f"[FETCH] Recibidas: {len(standard_orders)} órdenes.")
        
        # 3. Check for Algo Service (v1/openAlgoOrders)
        # Based on the document, conditional orders might be missing in standard fetch
        print("\n[FETCH] Solicitando Open Algo Orders (v1/openAlgoOrders)...")
        try:
            # We try the private implicit method for Binance USD-M Algo orders
            algo_orders_res = await exchange.fapiPrivateGetOpenAlgoOrders()
            # The structure of algo orders might differ, normally it has a 'orders' key or is directly a list
            algo_orders = algo_orders_res if isinstance(algo_orders_res, list) else algo_orders_res.get('orders', [])
            print(f"[FETCH] Recibidas: {len(algo_orders)} órdenes de algoritmo.")
        except Exception as e:
            print(f"[FETCH] Error consultando Algo Orders: {e}")
            algo_orders = []

        # 4. Token Efficiency Audit (Payload Analysis)
        all_orders = standard_orders + algo_orders
        if all_orders:
            sample = all_orders[0]
            print(f"\n[TOKEN] Auditoría de eficiencia de campos (Objeto Muestra):")
            essential_fields = ['symbol', 'side', 'price', 'amount', 'type', 'stopPrice']
            waste_fields = ['clientOrderId', 'cumBase', 'executedQty', 'avgPrice', 'workingType']
            
            found_essentials = [f for f in essential_fields if f in sample or (isinstance(sample, dict) and (f in sample or (f == 'stopPrice' and 'stopPrice' in sample.get('info', {}))))]
            found_waste = [f for f in waste_fields if f in sample or (isinstance(sample, dict) and (f in sample or f in sample.get('info', {})))]
            
            print(f" - Campos Críticos hallados: {found_essentials}")
            print(f" - Campos Ineficientes (Desperdicio): {found_waste}")
        else:
            print("\n[RESULT] No hay órdenes abiertas en la cuenta para analizar el payload.")

        # Summary of gaps
        if len(algo_orders) > 0 and len(standard_orders) == 0:
            print("\n[RECOMENDACIÓN] Se detectó que usas Algo Orders pero el fetch_open_orders estándar NO las devolvió. Debes integrar v1/openAlgoOrders.")
        elif len(all_orders) > 0:
            print(f"\n[RESULTADO FINAL] Resumen de Órdenes Abiertas:")
            for i, o in enumerate(all_orders):
                symbol = o.get('symbol') or o.get('symbol') # handle raw or ccxt
                side = o.get('side') or o.get('side')
                price = o.get('price', 0)
                print(f"  {i+1}. {symbol} | {side.upper()} | {price}")

    except Exception as e:
        print(f"[ERROR] Fallo crítico durante el test: {e}")
    finally:
        await exchange_manager.close()

if __name__ == "__main__":
    asyncio.run(test_orders_audit())
