import requests
import json
import time

BASE_URL = "http://localhost:8000/api"
SYMBOL = "BTC/USDT"

def test_historical_sync():
    print(f"--- Verificando Sincronización Histórica para {SYMBOL} ---")
    
    try:
        # 1. Primera llamada sin end_time
        print("\n[1] Llamando a /sync/historical sin end_time...")
        resp1 = requests.post(f"{BASE_URL}/sync/historical?symbol={SYMBOL}")
        print(f"Status 1: {resp1.status_code}")
        
        data1 = resp1.json()
        print(f"Respuesta completa 1: {json.dumps(data1, indent=2)}")
        
        s1 = data1.get('start_time')
        e1 = data1.get('end_time')
        
        if s1 is None or e1 is None:
            print("Error: No se recibió start_time o end_time. ¿Recargó la API?")
            return

        # 2. Segunda llamada con end_time = start_time_1 - 1
        target_end_time = s1 - 1
        print(f"\n[2] Llamando a /sync/historical con end_time={target_end_time}...")
        resp2 = requests.post(f"{BASE_URL}/sync/historical?symbol={SYMBOL}&end_time={target_end_time}")
        print(f"Status 2: {resp2.status_code}")
        
        data2 = resp2.json()
        print(f"Respuesta completa 2: {json.dumps(data2, indent=2)}")
        
        if data2.get('end_time') == target_end_time:
            print("\n--- [ÉXITO] Sincronización secuencial funciona correctamente. ---")
        else:
            print(f"\n--- [FALLO] Se esperaba end_time {target_end_time}, se recibió {data2.get('end_time')} ---")

    except Exception as e:
        print(f"Error durante el test: {str(e)}")

if __name__ == "__main__":
    test_historical_sync()
