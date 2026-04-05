from typing import Set, Optional
from app.db.database import Originator, OrderSource

class OriginResolver:
    """Logic to identify the originator of an order (SOLID - SRP)."""
    
    @staticmethod
    def resolve(
        raw_data: dict, 
        source: OrderSource, 
        logged_bot_order_ids: Set[str]
    ) -> Originator:
        """
        Deduce originator based on order source and bot logs.
        
        Rules:
        1. If it comes from Algo Service -> AUTO (always).
        2. If it's standard and ID is in bot logs -> BOT.
        3. If it's standard and NOT in bot logs -> MANUAL.
        """
        if source == OrderSource.ALGO:
            return Originator.AUTO
        
        # Standard orders
        order_id = str(raw_data.get('orderId') or raw_data.get('id', ''))
        if order_id in logged_bot_order_ids:
            return Originator.BOT
            
        return Originator.MANUAL
