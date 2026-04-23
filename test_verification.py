import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.tracker_logic import TradeTracker
from app.db.database import Fill

def test_exact_match_and_time_ordering():
    tracker = TradeTracker("BTC/USDT")
    
    # Mock some fills
    t = 1647900000000 # Base timestamp
    
    fills = [
        # Match 1: Normal Buy before Sell
        Fill(trade_id="1", symbol="BTC/USDT", side="buy", amount=1.0, price=50000, cost=50000, fee=5, timestamp=t, datetime=datetime.fromtimestamp(t/1000), order_id="buy_1"),
        Fill(trade_id="2", symbol="BTC/USDT", side="sell", amount=1.0, price=51000, cost=51000, fee=5, timestamp=t+1000, datetime=datetime.fromtimestamp((t+1000)/1000), order_id="sell_1"),
        
        # Orphan Sell: Sell before Buy (T-500)
        Fill(trade_id="3", symbol="BTC/USDT", side="sell", amount=0.5, price=52000, cost=26000, fee=2, timestamp=t-500, datetime=datetime.fromtimestamp((t-500)/1000), order_id="orphan_sell"),
        
        # Match 2: Fragmented Buy matched with single Sell
        Fill(trade_id="4a", symbol="BTC/USDT", side="buy", amount=0.4, price=50000, cost=20000, fee=2, timestamp=t+2000, datetime=datetime.fromtimestamp((t+2000)/1000), order_id="order_X"),
        Fill(trade_id="4b", symbol="BTC/USDT", side="buy", amount=0.6, price=50000, cost=30000, fee=3, timestamp=t+2001, datetime=datetime.fromtimestamp((t+2001)/1000), order_id="order_X"),
        Fill(trade_id="5", symbol="BTC/USDT", side="sell", amount=1.0, price=53000, cost=53000, fee=5, timestamp=t+3000, datetime=datetime.fromtimestamp((t+3000)/1000), order_id="sell_order_X"),
        
        # Unmatched Buy (Open)
        Fill(trade_id="6", symbol="BTC/USDT", side="buy", amount=2.0, price=49000, cost=98000, fee=9, timestamp=t+4000, datetime=datetime.fromtimestamp((t+4000)/1000), order_id="open_buy"),
    ]
    
    # 1. Test Matching
    matched = tracker.match_trades(fills, strategy_name="fifo")
    
    print(f"Total matched trades: {len(matched)}")
    for i, m in enumerate(matched):
        print(f"Trade {i+1}: {m['entry_amount']} {m['symbol']} @ {m['entry_price']} -> {m['exit_price']} (PnL: {m['pnl_net']})")
    
    assert len(matched) == 2, f"Expected 2 matches, got {len(matched)}"
    # Match 1: Buy 1.0 (buy_1) vs Sell 1.0 (sell_1)
    # Match 2: Buy 1.0 (order_X sum) vs Sell 1.0 (sell_order_X)
    
    # 2. Test Open Positions
    open_pos = tracker.compute_open_positions(logic="fifo", fills=fills)
    print(f"Total open/orphan positions: {len(open_pos)}")
    for op in open_pos:
        side = op['entry_side']
        status = "Orphan" if op.get('is_orphan') else "Open"
        print(f"[{status}] {op['entry_amount']} {side} @ {op['entry_price']}")
        
    # Expecting: 
    # 1 orphan sell (orphan_sell, 0.5)
    # 1 open buy (open_buy, 2.0)
    assert len(open_pos) == 2
    orphan_sells = [o for o in open_pos if o.get('is_orphan')]
    open_buys = [o for o in open_pos if not o.get('is_orphan')]
    assert len(orphan_sells) == 1
    assert len(open_buys) == 1
    
    print("VERIFICATION SUCCESSFUL")

if __name__ == "__main__":
    try:
        test_exact_match_and_time_ordering()
    except Exception as e:
        print(f"TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
