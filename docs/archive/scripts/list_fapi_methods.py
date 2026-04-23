import asyncio
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.core.exchange import exchange_manager

async def main():
    ex = await exchange_manager.get_exchange()
    print("--- SEARCH: ALGO + ORDER/OPEN ---")
    
    all_methods = dir(ex)
    found = [m for m in all_methods if 'algo' in m.lower() and ('order' in m.lower() or 'open' in m.lower())]
    found.sort()
    
    print(f"Total methods found: {len(found)}")
    for m in found:
        print(f"  {m}")
    
    await ex.close()

if __name__ == "__main__":
    asyncio.run(main())
