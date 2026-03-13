import json

import ccxt
from app.core.config import settings

exchange = ccxt.binance({
    'apiKey': settings.BINANCE_API_KEY or '',
    'secret': settings.BINANCE_API_SECRET or '',
    'enableRateLimit': True,
    'options': {'defaultType': 'future', 'adjustForTimeDifference': True},
})
exchange.load_markets()
for sym in ['1000PEPE/USDC:USDC']:#, '1000PEPE/USDC', '1000PEPEUSDC']:
    try:
        #exchange.verbose = True
        trades = exchange.fetch_my_trades(sym, 1772299261725-(2*4*7*24*60*60*1000),limit=1000)
        exchange.verbose = False
        print(sym, '->', len(trades))
        if trades:
            for trade in trades:
                trade['datetime'] = exchange.iso8601(trade['timestamp'])
                #print(trade['order'], trade['side'])
                print(json.dumps(trade, indent=2))
    except Exception as e:
        print(sym, 'error', type(e).__name__, str(e))
