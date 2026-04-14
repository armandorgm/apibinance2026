import asyncio
import httpx
import json

async def main():
    symbol = '1000PEPEUSDC'
    # Probando con una orden de compra conocida (basado en el screenshot anterior)
    order_id = '7387019449' # ID que vimos en el test de CCXT
    
    async with httpx.AsyncClient() as client:
        print(f"--- Probando API Preview V5.6 ---")
        try:
            url = f"http://localhost:8000/api/unified-counter-order-engine/preview?symbol={symbol}&order_id={order_id}&profit_pc=0.5"
            resp = await client.get(url)
            data = resp.json()
            
            print(f"Status: {resp.status_code}")
            print("Response Analysis:")
            print(f"- Pos Units: {data.get('pos_units')}")
            print(f"- Algo Units: {data.get('algo_units')}") # Debería ser != 0
            print(f"- Basic Units: {data.get('basic_units')}")
            print(f"- Action Units: {data.get('action_units')}")
            print(f"- Action Notional USDC: {data.get('action_notional_est')}")
            print(f"- Projected Net Pos (Contracts): {data.get('projected_net_pos')}")
            
            if data.get('algo_units') != 0:
                print("✅ TEST PASADO: Las órdenes Algo se están clasificando correctamente.")
            else:
                print("❌ TEST FALLIDO: Algo Units sigue siendo 0.")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
