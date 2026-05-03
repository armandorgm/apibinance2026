import pytest
from app.services.unified_counter_order_service import UnifiedCounterOrderService

def test_ucoe_profit_calculation():
    # Test 0.5% profit on a Buy order at 50000
    # Sell target should be 50000 * 1.005 = 50250
    target_price = UnifiedCounterOrderService.calculate_target_price('buy', 50000.0, 0.5)
    assert target_price == 50250.0

    # Test 0.5% profit on a Sell order at 50000
    # Buy target should be 50000 * 0.995 = 49750
    target_price = UnifiedCounterOrderService.calculate_target_price('sell', 50000.0, 0.5)
    assert target_price == 49750.0

def test_ucoe_reduce_only_logic():
    # Net position is +1.0 (Long)
    # Ref order was Buy -> We want to Sell. 
    # Since we are Long, selling reduces position -> reduceOnly = True
    assert UnifiedCounterOrderService.determine_reduce_only(current_net_pos=1.0, ref_order_side='buy') is True

    # Net position is -1.0 (Short)
    # Ref order was Sell -> We want to Buy.
    # Since we are Short, buying reduces position -> reduceOnly = True
    assert UnifiedCounterOrderService.determine_reduce_only(current_net_pos=-1.0, ref_order_side='sell') is True

    # Net position is 0.0 (Flat)
    # Any order is an opening -> reduceOnly = False
    assert UnifiedCounterOrderService.determine_reduce_only(current_net_pos=0.0, ref_order_side='buy') is False
    assert UnifiedCounterOrderService.determine_reduce_only(current_net_pos=0.0, ref_order_side='sell') is False

    # Net position is -1.0 (Short)
    # Ref order was Buy -> We want to Sell.
    # Selling when short INCREASES short -> reduceOnly = False (or not helpful for closing)
    assert UnifiedCounterOrderService.determine_reduce_only(current_net_pos=-1.0, ref_order_side='buy') is False

def test_ucoe_scaling_notional():
    # If amount * price < 5.0, it should scale to at least 5.05 / price
    price = 0.5
    amount = 5.0 # Nocional = 2.5
    scaled_amount, needs_scaling = UnifiedCounterOrderService.scale_to_min_notional(amount, price)
    assert needs_scaling is True
    assert scaled_amount * price >= 5.05

    # If amount * price > 5.0, no change
    amount = 20.0 # Nocional = 10.0
    scaled_amount, needs_scaling = UnifiedCounterOrderService.scale_to_min_notional(amount, price)
    assert needs_scaling is False
    assert scaled_amount == 20.0
