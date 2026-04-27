import ccxt
import os
import json
from dotenv import load_dotenv

# Cargar llaves desde .env
load_dotenv()

# Configuración de Binance (USDT-M Futures)
exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'options': {'defaultType': 'future'} 
})

try:
    # 1. Obtener posiciones (Equivalente a risk_position en la API de Binance)
    # fetch_positions() devuelve todas, fetch_position(symbol) una específica
    positions = exchange.fetch_positions()
    
    # 2. Filtrar solo las que tienen tamaño (opcional, para limpieza)
    active_positions = [p for p in positions if float(p['contracts']) > 0]
    
    # Imprimir resultado formateado para análisis
    print(json.dumps(active_positions, indent=4))

    # Obtener los niveles de apalancamiento para el símbolo
    leverage_data = exchange.fetch_leverage_tiers(['1000PEPE/USDC:USDC'])
    print(leverage_data)
except Exception as e:
    print(f"Error: {e}")