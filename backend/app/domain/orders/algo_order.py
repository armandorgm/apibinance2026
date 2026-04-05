from app.domain.orders.base_order import BaseOrder

class AlgoOrder(BaseOrder):
    """Managed by /fapi/v1/algo/ (TP, SL, Trailing)."""
    
    def __init__(self, *args, **kwargs):
        # We can add algo-specific fields here if needed later (triggerPrice, etc)
        super().__init__(*args, **kwargs)

    def can_be_entry(self) -> bool:
        """Central business rule: Algo/Conditional orders can NEVER be entries."""
        return False
