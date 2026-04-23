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
    
    # LIFO: sell 1.0 vs buy 2.0 (most recent, buy_2 at 150). Partial: match_qty=1.0.
    # PnL gross = (200-150)*1 = 50. Net = 50 - fee_share_buy - fee_sell.
    matched = tracker.match_trades_lifo(fills)
    print("LIFO Matched trades:")
    for t in matched:
        print(f"PnL: {t['pnl_net']:.4f}, Entry Price: {t['entry_price']}, Exit Price: {t['exit_price']}")
    assert len(matched) == 1, f"LIFO expected 1 trade, got {len(matched)}"
    assert matched[0]['entry_price'] == 150.0, f"LIFO should pick buy@150, got {matched[0]['entry_price']}"
    assert matched[0]['pnl_net'] > 0, "LIFO trade should be profitable"

    fills_fifo = [
        Fill(trade_id="1", symbol="TEST/USDT", side="buy", amount=1.0, price=100.0, cost=100.0, fee=0.1, fee_currency="USDT", timestamp=1000, datetime=datetime.fromtimestamp(1)),
        Fill(trade_id="2", symbol="TEST/USDT", side="buy", amount=2.0, price=150.0, cost=300.0, fee=0.2, fee_currency="USDT", timestamp=2000, datetime=datetime.fromtimestamp(2)),
        Fill(trade_id="3", symbol="TEST/USDT", side="sell", amount=1.0, price=200.0, cost=200.0, fee=0.3, fee_currency="USDT", timestamp=3000, datetime=datetime.fromtimestamp(3)),
    ]

    matched_fifo = tracker.match_trades_fifo(fills_fifo)
    print("\nFIFO Matched trades:")
    for t in matched_fifo:
        print(f"PnL: {t['pnl_net']:.4f}, Entry Price: {t['entry_price']}, Exit Price: {t['exit_price']}")
    assert len(matched_fifo) == 1, f"FIFO expected 1 trade, got {len(matched_fifo)}"
    assert matched_fifo[0]['entry_price'] == 100.0, f"FIFO should pick buy@100, got {matched_fifo[0]['entry_price']}"
    assert matched_fifo[0]['pnl_net'] > 0, "FIFO trade should be profitable"
    print("\nAll assertions passed ✓")

if __name__ == "__main__":
    run_test()
