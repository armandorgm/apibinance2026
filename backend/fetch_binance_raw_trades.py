import ccxt
import json
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv('.env')

def fetch_raw_binance_trades():
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'adjustForTimeDifference': True,
            'recvWindow': 10000,
        }
    })
    
    symbol = '1000PEPEUSDC'
    print(f"Fetching raw trades for {symbol} directly from Binance API...")
    
    try:
        # fetch_my_trades returns a list of trades normalized by CCXT
        # trade['info'] contains the RAW JSON from Binance
        trades = exchange.fetch_my_trades(symbol, limit=5)
        
        if not trades:
            print("No trades found on Binance for this symbol.")
            return

        print("\n=== RAW BINANCE JSON (info field) ===\n")
        raw_list = [t['info'] for t in trades]
        print(json.dumps(raw_list, indent=2))
        
        print("\n=== CCXT NORMALIZED JSON (top level) ===\n")
        print(json.dumps(trades[0], indent=2, sort_keys=True, default=str))

    except Exception as e:
        print(f"Error fetching Binance trades: {e}")

if __name__ == "__main__":
    fetch_raw_binance_trades()
