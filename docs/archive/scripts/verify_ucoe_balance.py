import asyncio
import sys
import os
from dotenv import load_dotenv

# Cargar variables antes de cualquier import de app
load_dotenv(dotenv_path='backend/.env')

# Añadir el path del backend para importar app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.unified_counter_order_service import UnifiedCounterOrderService
from app.core.exchange import exchange_manager

async def verify_ucoe():
    try:
        symbol = '1000PEPEUSDC'
        print(f"--- Verificando UCOE Balance (Factor 1000) para {symbol} ---")
        
        # 1. Obtener balance detallado
        balance = await UnifiedCounterOrderService.get_detailed_open_balance(symbol)
        
        print(f"Factor detectado: {balance.get('factor')}")
        print(f"Algo Units: {balance['algo_units']}")
        print(f"Basic Units: {balance['basic_units']}")
        print(f"Algo Contracts: {balance['algo_contracts']}")
        print(f"Basic Contracts: {balance['basic_contracts']}")
        
        # 2. Verificar si hay órdenes
        open_orders = await exchange_manager.fetch_open_orders(symbol)
        print(f"\nTotal órdenes fetch_open_orders: {len(open_orders)}")
        for o in open_orders:
            print(f" - ID: {o['id']} | Tipo: {o['type']} | Amount: {o['amount']} | IsAlgo: {o.get('is_algo')}")

        print("\n--- Verificación Exitosa de Balance ---")
        
    except Exception as e:
        print(f"\n--- ERROR DURANTE LA VERIFICACIÓN ---")
        import traceback
        traceback.print_exc()
    finally:
        # Cerrar conexión
        try:
            exchange = await exchange_manager.get_exchange()
            await exchange.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(verify_ucoe())
