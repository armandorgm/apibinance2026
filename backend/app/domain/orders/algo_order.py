from app.domain.orders.base_order import BaseOrder
from app.db.database import OrderSource

class AlgoOrder(BaseOrder):
    """Managed by /fapi/v1/algo/ (TP, SL, Trailing)."""
    
    def __init__(self, **kwargs):
        kwargs['source'] = OrderSource.ALGO
        super().__init__(**kwargs)

    def can_be_entry(self) -> bool:
        """Central business rule: Algo/Conditional orders can NEVER be entries."""
        return False
