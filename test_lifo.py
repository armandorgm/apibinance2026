import asyncio
import os
import sys

# Add the project directory to sys.path
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backend'))

from datetime import datetime
from app.services.tracker_logic import TradeTracker
from app.db.database import Fill

def run_test():
    tracker = TradeTracker("TEST/USDT")
    fills = [
        Fill(trade_id="1", symbol="TEST/USDT", side="buy", amount=1.0, price=100.0, cost=100.0, fee=0.1, fee_currency="USDT", timestamp=1000, datetime=datetime.fromtimestamp(1)),
        Fill(trade_id="2", symbol="TEST/USDT", side="buy", amount=2.0, price=150.0, cost=300.0, fee=0.2, fee_currency="USDT", timestamp=2000, datetime=datetime.fromtimestamp(2)),
        Fill(trade_id="3", symbol="TEST/USDT", side="sell", amount=1.0, price=200.0, cost=200.0, fee=0.3, fee_currency="USDT", timestamp=3000, datetime=datetime.fromtimestamp(3)),
    ]
    
    # LIFO: Sell 1.0 vs Buy 2.0 (most recent). Cost basis = 1.0 * 150 = 150. Revenue = 1.0 * 200 = 200. Profit = 50.
    matched = tracker.match_trades_lifo(fills)
    print("LIFO Matched trades:")
    for t in matched:
        print(f"PnL: {t['pnl_net']}, Entry Price: {t['entry_price']}, Exit Price: {t['exit_price']}")

    fills_fifo = [
        Fill(trade_id="1", symbol="TEST/USDT", side="buy", amount=1.0, price=100.0, cost=100.0, fee=0.1, fee_currency="USDT", timestamp=1000, datetime=datetime.fromtimestamp(1)),
        Fill(trade_id="2", symbol="TEST/USDT", side="buy", amount=2.0, price=150.0, cost=300.0, fee=0.2, fee_currency="USDT", timestamp=2000, datetime=datetime.fromtimestamp(2)),
        Fill(trade_id="3", symbol="TEST/USDT", side="sell", amount=1.0, price=200.0, cost=200.0, fee=0.3, fee_currency="USDT", timestamp=3000, datetime=datetime.fromtimestamp(3)),
    ]
    # FIFO: Sell 1.0 vs Buy 1.0 (oldest). Cost basis = 1.0 * 100 = 100. Revenue = 1.0 * 200 = 200. Profit = 100.
    matched_fifo = tracker.match_trades_fifo(fills_fifo)
    print("\nFIFO Matched trades:")
    for t in matched_fifo:
        print(f"PnL: {t['pnl_net']}, Entry Price: {t['entry_price']}, Exit Price: {t['exit_price']}")

if __name__ == "__main__":
    run_test()
