import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.unified_counter_order_service import UnifiedCounterOrderService

def test_ucoe_profit_calculation():
    print("Testing profit calculation...")
    target_price = UnifiedCounterOrderService.calculate_target_price('buy', 50000.0, 0.5)
    assert abs(target_price - 50250.0) < 1e-7
    print("  - Buy @ 50000 + 0.5% = 50250 [PASS]")

    target_price = UnifiedCounterOrderService.calculate_target_price('sell', 50000.0, 0.5)
    expected_sell = 50000.0 / 1.005
    assert abs(target_price - expected_sell) < 1e-7
    print(f"  - Sell @ 50000 + 0.5% = {target_price:.2f} [PASS]")

def test_ucoe_reduce_only_logic():
    print("Testing reduceOnly logic...")
    assert UnifiedCounterOrderService.determine_reduce_only(1.0, 'buy') is True
    print("  - Long + Ref Buy -> Sell (ReduceOnly=True) [PASS]")
    
    assert UnifiedCounterOrderService.determine_reduce_only(-1.0, 'sell') is True
    print("  - Short + Ref Sell -> Buy (ReduceOnly=True) [PASS]")
    
    assert UnifiedCounterOrderService.determine_reduce_only(0.0, 'buy') is False
    print("  - Flat + Any -> (ReduceOnly=False) [PASS]")

def test_ucoe_scaling_notional():
    print("Testing scaling logic...")
    price = 0.5
    amount = 5.0 # Notional 2.5
    scaled, needs = UnifiedCounterOrderService.scale_to_min_notional(amount, price)
    assert needs is True
    assert scaled * price >= 5.05
    print(f"  - Notional $2.5 scaled to ${scaled * price:.2f} [PASS]")

if __name__ == "__main__":
    try:
        test_ucoe_profit_calculation()
        test_ucoe_reduce_only_logic()
        test_ucoe_scaling_notional()
        print("\nALL UCOE TESTS PASSED SUCCESSFULLY!")
    except Exception:
        import traceback
        print("\nTEST FAILED:")
        traceback.print_exc()
        sys.exit(1)
