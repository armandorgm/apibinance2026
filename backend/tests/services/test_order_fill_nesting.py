import pytest
from app.services.tracker_logic import TradeTracker
from app.db.database import Fill
from datetime import datetime

def test_group_fills_by_order_includes_nested_fills():
    """
    TDD Test: Verify that grouping fills by order results in a 
    dictionary that contains the list of original fills.
    """
    tracker = TradeTracker(symbol="BTC/USDT")
    
    # Create two mock fills for the same Order ID
    f1 = Fill(
        trade_id="trade_1",
        order_id="order_A",
        symbol="BTC/USDT",
        side="buy",
        price=50000.0,
        amount=0.1,
        fee=0.0001,
        timestamp=1700000000,
        datetime=datetime.now()
    )
    
    f2 = Fill(
        trade_id="trade_2",
        order_id="order_A",
        symbol="BTC/USDT",
        side="buy",
        price=50100.0,
        amount=0.1,
        fee=0.0001,
        timestamp=1700000001,
        datetime=datetime.now()
    )
    
    # Run the internal grouping logic
    orders_list = tracker._group_fills_by_order([f1, f2])
    
    # Assertions
    assert len(orders_list) == 1
    order = orders_list[0]
    assert order["order_id"] == "order_A"
    
    # Check that it contains a list of fills
    assert "fills" in order, "The grouped order must contain a 'fills' key"
    assert len(order["fills"]) == 2
    
    # Verify fill data identity
    assert order["fills"][0]["trade_id"] == "trade_1"
    assert order["fills"][1]["trade_id"] == "trade_2"
    assert "fee" in order["fills"][0], "Individual fees must be present for total transparency"

def test_match_trades_propagates_fills_to_trade_objects():
    """
    TDD Test: Verify that match_trades output includes the nested fills for UI use.
    """
    tracker = TradeTracker(symbol="BTC/USDT")
    
    # 1. Entry Order (2 fills)
    entry_f1 = Fill(trade_id="e1", order_id="buy_A", symbol="BTC/USDT", side="buy", price=100.0, amount=1.0, fee=0.1, timestamp=100, datetime=datetime.now())
    entry_f2 = Fill(trade_id="e2", order_id="buy_A", symbol="BTC/USDT", side="buy", price=100.0, amount=1.0, fee=0.1, timestamp=101, datetime=datetime.now())
    
    # 2. Exit Order (1 fill)
    exit_f1 = Fill(trade_id="x1", order_id="sell_B", symbol="BTC/USDT", side="sell", price=110.0, amount=2.0, fee=0.2, timestamp=200, datetime=datetime.now())
    
    # Match using standard FIFO
    trades = tracker.match_trades([entry_f1, entry_f2, exit_f1], strategy_name="fifo")
    
    assert len(trades) == 1
    trade = trades[0]
    
    # Verify nested info for UI expansion
    assert "entry_fills" in trade, "Trade must contain the list of entries that formed it"
    assert "exit_fills" in trade, "Trade must contain the list of exits that formed it"
    
    assert len(trade["entry_fills"]) == 2
    assert len(trade["exit_fills"]) == 1
    assert trade["entry_fills"][0]["order_id"] == "buy_A"
