from abc import ABC, abstractmethod
from datetime import datetime
from app.db.database import Originator, OrderSource

class BaseOrder(ABC):
    """Abstract Base Class for Orders (SOLID)."""
    
    def __init__(
        self,
        order_id: str,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        status: str,
        dt: datetime,
        originator: Originator,
        source: OrderSource,
        is_bot_logged: bool = False,
        order_type: str = "LIMIT",
        create_time_ms: int | None = None,
        conditional_kind: str | None = None
    ):
        self.id = order_id
        self.symbol = symbol
        self.side = side.lower()
        self.amount = amount
        self.price = price
        self.status = status.upper()
        self.datetime = dt
        self.originator = originator
        self.source = source
        self.is_bot_logged = is_bot_logged
        self.order_type = order_type.upper() if order_type else "LIMIT"
        self.create_time_ms = create_time_ms
        self.conditional_kind = conditional_kind

    @abstractmethod
    def can_be_entry(self) -> bool:
        """Central business rule."""
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "amount": self.amount,
            "price": self.price,
            "status": self.status,
            "datetime": self.datetime,
            "originator": self.originator,
            "source": self.source,
            "can_be_entry": self.can_be_entry(),
            "is_bot_logged": self.is_bot_logged,
            "order_type": self.order_type,
            "create_time_ms": self.create_time_ms,
            "conditional_kind": self.conditional_kind
        }
