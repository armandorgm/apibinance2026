from app.domain.orders.base_order import BaseOrder
from app.db.database import OrderSource

class StandardOrder(BaseOrder):
    """Managed by /fapi/v1/orders (LIMIT/MARKET)."""
    
    def __init__(self, **kwargs):
        kwargs['source'] = OrderSource.STANDARD
        super().__init__(**kwargs)

    def can_be_entry(self) -> bool:
        """A standard order can always initiate a position."""
        return True
