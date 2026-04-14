import asyncio
import sys
import os

# Añadir el path del backend para importar app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.exchange import exchange_manager
from dotenv import load_dotenv

async def verify():
    load_dotenv(dotenv_path='backend/.env')
    
    symbol = '1000PEPEUSDC'
    print(f"--- Verificando fetch_open_orders para {symbol} (Strict CCXT Native) ---")
    
    orders = await exchange_manager.fetch_open_orders(symbol)
    
    print(f"Total órdenes encontradas: {len(orders)}")
    for o in orders:
        is_algo = o.get('is_algo', False)
        o_type = o.get('type')
        o_id = o.get('id')
        print(f" - [{ 'ALGO' if is_algo else 'STD' }] ID: {o_id} | Tipo: {o_type} | Cantidad: {o.get('amount')}")

    if not any(o.get('is_algo') for o in orders):
        print("\n¡ALERTA!: No se encontraron órdenes ALGO. Verifica que existan en Binance.")
        
    # Cerrar conexión
    exchange = await exchange_manager.get_exchange()
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(verify())
