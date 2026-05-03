import asyncio
import ccxt.async_support as ccxt
import json
import os
from dotenv import load_dotenv

# Load env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def main():
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'future'}
    })
    
    symbol = '1000PEPE/USDC:USDC'
    try:
        # Load markets
        await exchange.load_markets()
        market_id = exchange.market(symbol)['id']
        
        # 1. Fetch raw Algo orders using direct request
        params = {'algoType': 'CONDITIONAL', 'symbol': market_id}
        res_algo = await exchange.request('openAlgoOrders', 'fapiPrivate', 'GET', params)
        
        # 2. Fetch standard open orders
        res_std = await exchange.fetch_open_orders(symbol)
        
        output = {
            "symbol": symbol,
            "fapi_algo_raw": res_algo,
            "ccxt_standard": res_std
        }
        print(json.dumps(output, indent=2))
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
