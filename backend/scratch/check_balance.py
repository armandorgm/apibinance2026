
import asyncio
from app.core.binance_native import binance_native

async def main():
    print("Fetching balance...")
    try:
        # We use a large recvWindow to avoid sync issues during this debug
        balance = await binance_native.get_available_balance("USDC")
        print(f"Available USDC Balance: {balance}")
        
        balance_usdt = await binance_native.get_available_balance("USDT")
        print(f"Available USDT Balance: {balance_usdt}")
        
        # Raw response for more info
        res = await binance_native._execute_with_retry(binance_native.client.balance, recvWindow=10000)
        print("Raw Balance Response:")
        for b in res:
            if float(b.get('balance', 0)) > 0:
                print(f"  {b.get('asset')}: balance={b.get('balance')}, available={b.get('availableBalance')}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
