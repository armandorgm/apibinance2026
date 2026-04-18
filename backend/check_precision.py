import asyncio
from app.core.exchange import exchange_manager

async def check():
    ex = await exchange_manager.get_exchange()
    await ex.load_markets()
    m = ex.market('1000PEPE/USDC:USDC')
    print(f"Symbol: {m['symbol']}")
    print(f"Precision: {m['precision']}")
    print(f"Limits: {m['limits']}")

if __name__ == "__main__":
    asyncio.run(check())
