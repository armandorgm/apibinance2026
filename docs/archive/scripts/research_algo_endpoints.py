import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.exchange import exchange_manager

async def main():
    try:
        print("--- RESEARCH: BINANCE ALGO ENDPOINTS ---")
        ex = await exchange_manager.get_exchange()
        
        # 1. Look for dynamic methods
        algo_methods = [m for m in dir(ex) if 'Algo' in m]
        print(f"Potential Algo Methods: {algo_methods}")
        
        # 2. Try native fetch_open_orders with different params
        print("\n--- Testing fetch_open_orders with experimental params ---")
        symbols = ["1000PEPE/USDC:USDC", None]
        params_list = [
            {'algoType': 'CONDITIONAL'},
            {'algoType': 'STOP_LOSS'},
            {'type': 'algo'},
            {'method': 'algo'}
        ]
        
        for sym in symbols:
            for p in params_list:
                try:
                    print(f"Calling fetch_open_orders(symbol={sym}, params={p})...")
                    orders = await ex.fetch_open_orders(sym, params=p)
                    if orders:
                        print(f"SUCCESS! Found {len(orders)} orders.")
                        for o in orders[:2]:
                            print(f"  - Order ID: {o.get('id')} | Type: {o.get('type')}")
                    else:
                        print("  (Empty)")
                except Exception as e:
                    print(f"  FAILED: {e}")

        # 3. List ALL methods that start with fapi or contain Algo
        print("\n--- Listing ALL fapi and algo methods ---")
        fapi_methods = [m for m in dir(ex) if m.startswith('fapi')]
        print(f"Fapi Methods: {fapi_methods[:10]}... (Total: {len(fapi_methods)})")
        
        algo_methods = [m for m in dir(ex) if 'Algo' in m]
        print(f"Algo Methods: {algo_methods}")

        # 4. Search for specific keywords
        target_methods = [m for m in dir(ex) if ('Algo' in m and ('Open' in m or 'Orders' in m))]
        print(f"Targeted Algo Methods (Open/Orders): {target_methods}")

        # 5. Try calling the targeted once
        for method_name in target_methods:
            print(f"\n--- Testing targeted method: {method_name} ---")
            try:
                raw_response = await getattr(ex, method_name)()
                print(f"SUCCESS! {method_name} returned data.")
                print(f"Data: {json.dumps(raw_response, indent=2)[:500]}...")
            except Exception as e:
                print(f"  FAILED: {e}")
                try:
                    print(f"  Retrying {method_name} with symbol='1000PEPEUSDC'...")
                    raw_response = await getattr(ex, method_name)({'symbol': '1000PEPEUSDC'})
                    print(f"  SUCCESS with symbol! Data: {json.dumps(raw_response, indent=2)[:500]}...")
                except Exception as e2:
                    print(f"  FAILED with symbol: {e2}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        if exchange_manager._exchange:
            await exchange_manager._exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
