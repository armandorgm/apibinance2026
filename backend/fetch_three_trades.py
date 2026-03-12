import ccxt
from app.core.config import settings

exchange = ccxt.binance({
    'apiKey': settings.BINANCE_API_KEY or '',
    'secret': settings.BINANCE_API_SECRET or '',
    'enableRateLimit': True,
    'options': {'defaultType': 'future', 'adjustForTimeDifference': True},
})
exchange.load_markets()

# try the normalized future symbol and id forms
symbols = ['1000PEPE/USDC:USDC', '1000PEPE/USDC', '1000PEPEUSDC']
for sym in symbols:
    try:
        trades = exchange.fetch_my_trades(sym, limit=1000)
        print(f"{sym}: {len(trades)} trades")
        for t in trades:
            print("  id=", t.get('id'), "timestamp=", t.get('timestamp'))
    except Exception as e:
        print(sym, 'error', type(e).__name__, str(e))
