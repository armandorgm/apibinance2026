import pytest
from datetime import datetime, timedelta
from app.services.tracker_logic import TradeTracker, Fill

class MockTracker(TradeTracker):
    def __init__(self):
        self.symbol = "BTC/USDT"
    
    def _group_fills_by_order(self, fills, session=None):
        # Mini mock of grouping logic
        orders = {}
        for f in fills:
            if f.order_id not in orders:
                orders[f.order_id] = {
                    'order_id': f.order_id,
                    'side': f.side,
                    'amount': 0,
                    'price': f.price,
                    'timestamp': f.timestamp,
                    'datetime': f.datetime,
                    'fee': 0,
                    'order_type': getattr(f, 'order_type', 'LIMIT'),
                    'can_be_entry': True
                }
            orders[f.order_id]['amount'] += f.amount
        return list(orders.values())

def test_intent_match_logic():
    from app.services.tracker_logic import IntentMatchStrategy
    
    tracker = MockTracker()
    strategy = IntentMatchStrategy()
    
    now = int(datetime.utcnow().timestamp() * 1000)
    
    # SETUP:
    # 1. Buy 1.0 BTC (Entry)
    # 2. Stop Loss 1.0 BTC (Should be ignored by Intent)
    # 3. Take Profit 1.0 BTC (Should be matched)
    fills = [
        Fill(trade_id="1", symbol="BTC/USDT", side="buy", amount=1.0, price=50000, timestamp=now, order_id="B1"),
        Fill(trade_id="2", symbol="BTC/USDT", side="sell", amount=1.0, price=49000, timestamp=now+1000, order_id="S_SL"),
        Fill(trade_id="3", symbol="BTC/USDT", side="sell", amount=1.0, price=51000, timestamp=now+2000, order_id="S_TP"),
    ]
    
    # Manually add order_type to mock objects
    fills[0].order_type = "LIMIT"
    fills[1].order_type = "STOP_LOSS_MARKET"
    fills[2].order_type = "TAKE_PROFIT_MARKET"
    
    trades = strategy.match(tracker, fills)
    
    assert len(trades) == 1
    assert trades[0]['entry_order_id'] == "B1"
    assert trades[0]['exit_order_id'] == "S_TP" # Matched TP, ignored SL
    assert trades[0]['pnl_net'] > 0

def test_intent_match_chronological_and_atomic():
    from app.services.tracker_logic import IntentMatchStrategy
    tracker = MockTracker()
    strategy = IntentMatchStrategy()
    now = int(datetime.utcnow().timestamp() * 1000)
    
    # 1. Buy 0.5 (E1)
    # 2. Buy 0.5 (E2)
    # 3. Sell 0.5 (X1) -> should match E1
    # 4. Sell 0.5 (X2) -> should match E2
    fills = [
        Fill(trade_id="1", symbol="BTC/USDT", side="buy", amount=0.5, price=50000, timestamp=now, order_id="E1"),
        Fill(trade_id="2", symbol="BTC/USDT", side="buy", amount=0.5, price=50000, timestamp=now+1, order_id="E2"),
        Fill(trade_id="3", symbol="BTC/USDT", side="sell", amount=0.5, price=51000, timestamp=now+10, order_id="X1"),
        Fill(trade_id="4", symbol="BTC/USDT", side="sell", amount=0.5, price=51000, timestamp=now+20, order_id="X2"),
    ]
    for f in fills: f.order_type = "LIMIT"
    
    trades = strategy.match(tracker, fills)
    assert len(trades) == 2
    assert trades[0]['entry_order_id'] == "E1"
    assert trades[0]['exit_order_id'] == "X1"
    assert trades[1]['entry_order_id'] == "E2"
    assert trades[1]['exit_order_id'] == "X2"

if __name__ == "__main__":
    # Simple manual run
    test_intent_match_logic()
    test_intent_match_chronological_and_atomic()
    print("All Intent Matcher tests passed!")
