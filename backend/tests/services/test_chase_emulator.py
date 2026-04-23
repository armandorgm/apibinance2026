import pytest
from app.services.pipeline_engine.chase_emulator import ChaseEmulator
from datetime import datetime, timedelta

def test_emulator_lifecycle_buy():
    """
    Test a full BUY lifecycle: Initial -> Escape (Chase) -> Hit (Fill).
    """
    # 1. Initial State: BUY limit at 50000
    emulator = ChaseEmulator(side="buy", order_price=50000.0)
    assert emulator.status == "CHASING"
    assert emulator.order_price == 50000.0
    
    # 2. Price moves AWAY (Up for Buy) -> Should replace order
    # Skip cooldown by setting last_update in the past
    emulator.last_update = datetime.utcnow() - timedelta(seconds=10)
    
    res = emulator.on_tick(50100.0)
    assert res["status"] == "CHASING"
    assert res["action"] == "REPLACED"
    assert res["new_price"] == 50100.0
    assert emulator.order_price == 50100.0
    
    # 3. Price moves TOWARDS (Down for Buy) but not enough to fill
    res = emulator.on_tick(50110.0) # Escaping more
    # (Note: cooldown will prevent 50110 from replacing 50100 immediately)
    assert res["action"] == "WAITING" 
    
    # 4. Price HITS the order (50100 or below) -> FILL
    res = emulator.on_tick(50090.0)
    assert res["status"] == "FILLED"
    assert emulator.status == "FILLED"

def test_emulator_lifecycle_sell():
    """
    Test a full SELL lifecycle: Initial -> Escape (Chase) -> Hit (Fill).
    """
    # 1. Initial State: SELL limit at 50000
    emulator = ChaseEmulator(side="sell", order_price=50000.0)
    
    # 2. Price moves AWAY (Down for Sell) -> Should replace order
    emulator.last_update = datetime.utcnow() - timedelta(seconds=10)
    res = emulator.on_tick(49900.0)
    assert res["status"] == "CHASING"
    assert res["action"] == "REPLACED"
    assert emulator.order_price == 49900.0
    
    # 3. Price HITS the order (49900 or above) -> FILL
    res = emulator.on_tick(49950.0)
    assert res["status"] == "FILLED"
