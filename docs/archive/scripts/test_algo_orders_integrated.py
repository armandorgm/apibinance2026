import asyncio
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.exchange import exchange_manager
from app.domain.orders.order_factory import OrderFactory

async def test_algo_orders_integrated():
    print("--- Testing Algo Orders (Standardized) ---")
    symbol = "1000PEPEUSDC"
    print(f"Symbol: {symbol}")
    
    try:
        # Fetching combined open orders
        orders = await exchange_manager.fetch_open_orders(symbol)
        print(f"Total Combined Orders: {len(orders)}")
        
        for o in orders:
            # Create domain order using Factory
            domain_order = OrderFactory.create(o, set())
            
            print(f"ID: {domain_order.id} | Source: {domain_order.source.value} | Type: {getattr(domain_order, 'order_type', 'N/A')} | Side: {domain_order.side} | Qty: {domain_order.amount}")
            if hasattr(domain_order, 'conditional_kind'):
                print(f"  Kind: {domain_order.conditional_kind}")

        # Test UCOE balance service integration
        from app.services.unified_counter_order_service import UnifiedCounterOrderService
        
        balance = await UnifiedCounterOrderService.get_detailed_open_balance(symbol)
        print("\n--- UCOE Balance ---")
        print(f"Algo Units: {balance['algo_units']}")
        print(f"Basic Units: {balance['basic_units']}")
        print(f"Total Balanced Units: {balance['algo_units'] + balance['basic_units']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_algo_orders_integrated())
