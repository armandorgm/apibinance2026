from datetime import datetime
from typing import Set
from app.db.database import Originator, OrderSource
from app.domain.orders.base_order import BaseOrder
from app.domain.orders.standard_order import StandardOrder
from app.domain.orders.algo_order import AlgoOrder
from app.domain.orders.origin_resolver import OriginResolver

from typing import Set, Optional

def _conditional_kind_from_order_type(order_type: str) -> Optional[str]:
    ot = (order_type or '').upper()
    if 'TRAILING' in ot:
        return 'trailing'
    if 'TAKE_PROFIT' in ot:
        return 'take_profit'
    if 'STOP' in ot:
        return 'stop_loss'
    return None

class OrderFactory:
    """Factory to instantiate the correct Order subtype (SOLID - OCP)."""
    
    @staticmethod
    def create(raw_data: dict, logged_bot_order_ids: Set[str]) -> BaseOrder:
        # Determine Source
        source_tag = raw_data.get('_source', 'standard')
        source = OrderSource.ALGO if source_tag == 'algo' else OrderSource.STANDARD
        
        # Determine Originator
        originator = OriginResolver.resolve(raw_data, source, logged_bot_order_ids)
        is_bot_logged = originator == Originator.BOT

        # Common mapping logic
        if source == OrderSource.STANDARD:
            order_id = str(raw_data.get('orderId') or raw_data.get('id', ''))
            symbol = raw_data.get('symbol', '')
            side = raw_data.get('side', '').lower()
            amount = float(raw_data.get('origQty') or raw_data.get('amount', 0.0))
            price = float(raw_data.get('price', 0.0))
            status = raw_data.get('status', '').upper()
            ts = raw_data.get('timestamp') or raw_data.get('time', 0)
            dt = datetime.fromtimestamp(ts / 1000) if ts else datetime.utcnow()
            
            order_type = str(raw_data.get('origType') or raw_data.get('type') or 'LIMIT').upper()
            
            return StandardOrder(
                order_id=order_id,
                symbol=symbol,
                side=side,
                amount=amount,
                price=price,
                status=status,
                dt=dt,
                originator=originator,
                source=source,
                is_bot_logged=is_bot_logged,
                order_type=order_type
            )
        else:
            # Algo Service mapping
            order_id = str(raw_data.get('algoId', ''))
            symbol = raw_data.get('symbol', '')
            side = raw_data.get('side', '').lower()
            amount = float(raw_data.get('totalQty') or raw_data.get('quantity') or raw_data.get('amount', 0.0))
            price = float(raw_data.get('triggerPrice') or raw_data.get('stopPrice', 0.0))
            status = raw_data.get('algoStatus', 'NEW').upper()
            ts = raw_data.get('time') or raw_data.get('updateTime', 0)
            try:
                ts_int = int(ts)
            except (TypeError, ValueError):
                ts_int = 0
            dt = datetime.fromtimestamp(ts_int / 1000) if ts_int else datetime.utcnow()
            
            order_type = str(raw_data.get('orderType') or raw_data.get('type') or 'ALGO').upper()
            conditional_kind = _conditional_kind_from_order_type(order_type)
            
            # Extract createTime safely
            create_time_ms = None
            ct = raw_data.get('createTime')
            if ct is not None and ct != 0:
                try:
                    create_time_ms = int(ct)
                except (TypeError, ValueError):
                    pass
            
            return AlgoOrder(
                order_id=order_id,
                symbol=symbol,
                side=side,
                amount=amount,
                price=price,
                status=status,
                dt=dt,
                originator=originator,
                source=source,
                is_bot_logged=is_bot_logged,
                order_type=order_type,
                create_time_ms=create_time_ms,
                conditional_kind=conditional_kind
            )
