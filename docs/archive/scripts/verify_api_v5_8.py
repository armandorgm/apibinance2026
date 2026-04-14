import asyncio
import httpx
import json

async def main():
    # USANDO EL FORMATO ESTÁNDAR DE CCXT COMO ÚNICA FUENTE DE VERDAD
    symbol = '1000PEPE/USDC:USDC'
    order_id = '7387019449' # ID de ejemplo
    
    async with httpx.AsyncClient() as client:
        print(f"--- Verificando UCOE V5.8 (Standard Consistency) ---")
        try:
            url = f"http://localhost:8000/api/unified-counter-order-engine/preview?symbol={symbol}&order_id={order_id}&profit_pc=0.5"
            resp = await client.get(url)
            
            if resp.status_code != 200:
                print(f"Error {resp.status_code}: {resp.text}")
                return

            data = resp.json()
            print("Response Data:")
            print(f"- Pos Units: {data.get('pos_units')}")
            print(f"- Algo Units: {data.get('algo_units')}")
            print(f"- Basic Units: {data.get('basic_units')}")
            print(f"- Action Units: {data.get('action_units')}")
            print(f"- Expected Total (Units): {data.get('projected_net_pos', 0) * 1000}")
            
            # Verificación de que no hay campos 'pro' o metadata innecesaria en la superficie
            print("\nAudit de Limpieza:")
            if 'action_notional_est' in data:
                print("Nota: El backend aún calcula notional para el motor, pero el frontend lo ocultará.")
            
            print("--- Fin de Verificación ---")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
