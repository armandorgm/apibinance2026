from app.domain.orders.base_order import BaseOrder

class StandardOrder(BaseOrder):
    """Managed by /fapi/v1/orders (LIMIT/MARKET)."""
    
    def can_be_entry(self) -> bool:
        """A standard order can always initiate a position."""
        return True
