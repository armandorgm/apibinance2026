"""
Tests for LifecycleNettingStrategy (Binance Netting Mode).
Focuses on the 0-balance to 0-balance requirement.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from datetime import datetime
from app.services.tracker_logic import TradeTracker, LifecycleNettingStrategy
from app.db.database import Fill

BASE_TS = 1700000000000

def make_fill(tid, side, amount, price, ts_offset, order_id=None):
    ts = BASE_TS + ts_offset
    return Fill(
        trade_id=tid,
        symbol="NET/USDT",
        side=side,
        amount=amount,
        price=price,
        cost=amount * price,
        fee=0.1,
        fee_currency="USDT",
        timestamp=ts,
        datetime=datetime.fromtimestamp(ts / 1000),
        order_id=order_id or tid,
    )

def test_single_complete_lifecycle():
    tracker = TradeTracker("NET/USDT")
    fills = [
        make_fill("f1", "buy",  1.0, 100.0, 0),
        make_fill("f2", "buy",  1.0, 110.0, 1000),
        make_fill("f3", "sell", 2.0, 120.0, 2000), # Returns to 0
    ]
    
    trades = tracker.match_trades(fills, "binance_netting")
    assert len(trades) == 1
    t = trades[0]
    assert t['entry_amount'] == 2.0
    assert t['entry_price'] == 105.0 # (100+110)/2
    assert t['exit_price'] == 120.0
    assert t['pnl_net'] > 0

def test_multiple_lifecycles():
    tracker = TradeTracker("NET/USDT")
    fills = [
        make_fill("f1", "buy",  1.0, 100.0, 0),
        make_fill("f2", "sell", 1.0, 110.0, 1000), # End Cycle 1
        make_fill("f3", "buy",  1.0, 120.0, 2000), 
        make_fill("f4", "sell", 1.0, 130.0, 3000), # End Cycle 2
    ]
    
    trades = tracker.match_trades(fills, "binance_netting")
    assert len(trades) == 2
    assert trades[0]['entry_price'] == 100.0
    assert trades[1]['entry_price'] == 120.0

def test_temporal_integrity_no_mixing():
    tracker = TradeTracker("NET/USDT")
    # Order f4 (buy) arrives after cycle 1 is closed. It should start a new cycle.
    fills = [
        make_fill("f1", "buy",  1.0, 100.0, 0),
        make_fill("f2", "sell", 1.0, 110.0, 1000), # Closed
        make_fill("f3", "buy",  1.0, 150.0, 2000), # Open
    ]
    
    # match_trades only returns CLOSED cycles
    closed = tracker.match_trades(fills, "binance_netting")
    assert len(closed) == 1
    assert closed[0]['exit_price'] == 110.0
    
    # compute_open_positions should return the active cycle
    open_pos = tracker.compute_open_positions(logic="binance_netting", fills=fills)
    assert len(open_pos) == 1
    assert open_pos[0]['entry_price'] == 150.0
    assert open_pos[0]['entry_amount'] == 1.0

def test_partial_reductions_stay_in_block():
    tracker = TradeTracker("NET/USDT")
    fills = [
        make_fill("f1", "buy",  2.0, 100.0, 0),
        make_fill("f2", "sell", 1.0, 110.0, 1000), # Balance still 1.0
        make_fill("f3", "sell", 1.0, 120.0, 2000), # Returns to 0
    ]
    
    trades = tracker.match_trades(fills, "binance_netting")
    assert len(trades) == 1 # 1 Cycle Block
    assert trades[0]['entry_amount'] == 2.0
    assert trades[0]['exit_price'] == 115.0 # (110+120)/2
