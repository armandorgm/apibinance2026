import asyncio
import json
from app.core.exchange import exchange_manager

async def main():
    print("Iniciando conexión con Binance...")
    exchange = await exchange_manager.get_exchange()
    
    symbol_raw = "1000PEPEUSDC" 
    # CCXT expected ID or param
    params = {
        'symbol': symbol_raw,
        # Si queremos solo condicionales: 'algoType': 'CONDITIONAL'
    }
    
    print(f"Buscando openAlgoOrders para {symbol_raw}...")
    
    try:
        # endpoint: GET /fapi/v1/openAlgoOrders
        res = await exchange.request('openAlgoOrders', 'fapiPrivate', 'GET', params)
        orders = res if isinstance(res, list) else res.get('orders', res)
        
        # Filtramos por las fechas que mencionó el usuario: del 15_FEB al 04_ABR 2026.
        # En realidad si están "open" (pendientes), están devueltas sí o sí por este endpoint, sin importar la fecha de creación.
        print(f"Encontradas {len(orders)} órdenes algo pendientes:")
        for o in orders:
            print(json.dumps(o, indent=2))
    except Exception as e:
        print(f"Error consultando openAlgoOrders: {e}")

if __name__ == "__main__":
    asyncio.run(main())
