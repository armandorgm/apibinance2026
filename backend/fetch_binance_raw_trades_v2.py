import asyncio
import json
import sys
import os

# Ensure the backend/app directory is in path
sys.path.append(os.path.join(os.getcwd(), 'app'))
sys.path.append(os.getcwd())

from app.core.exchange import exchange_manager

async def fetch_raw_trades():
    print("Iniciando conexión segura con Binance (vía ExchangeManager)...")
    try:
        symbol = "1000PEPEUSDC"
        # Usamos el manager del proyecto que ya tiene lógica de sincronización de tiempo (load_time_difference)
        trades = await exchange_manager.fetch_my_trades(symbol, limit=2)
        
        if not trades:
            print(f"No se encontraron trades para {symbol}")
            return

        print("\n" + "="*50)
        print("RAW BINANCE JSON (info field) - Source of Truth")
        print("="*50)
        
        # Extraemos el 'info' que contiene el JSON exacto devuelto por Binance
        raw_info = [t['info'] for t in trades]
        print(json.dumps(raw_info, indent=2))
        
        print("\n" + "="*50)
        print("CCXT NORMALIZED JSON (Top Level)")
        print("="*50)
        # Mostramos cómo CCXT normaliza este JSON
        print(json.dumps(trades[0], indent=2, sort_keys=True, default=str))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await exchange_manager.close()

if __name__ == "__main__":
    asyncio.run(fetch_raw_trades())
