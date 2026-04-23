from typing import Any, Dict, Optional
from app.db.database import get_session_direct, Fill
from sqlmodel import select

class BaseDataProvider:
    """Base interface for all data providers."""
    async def get_value(self, symbol: str, params: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError()


class CurrentPriceProvider(BaseDataProvider):
    """Provides the current market price (simulated or fetched from exchange context)."""
    async def get_value(self, symbol: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # We would probably need to pass an exchange_manager reference or cache here.
        # But to keep dependencies clean, we expect a context injected.
        if params and "current_price" in params:
             return params["current_price"]
        return 0.0


class LastEntryPriceProvider(BaseDataProvider):
    """Provides the price of the last execution (Buy) from the database."""
    async def get_value(self, symbol: str, params: Optional[Dict[str, Any]] = None) -> Any:
        with get_session_direct() as session:
            statement = select(Fill).where(Fill.symbol == symbol, Fill.side == 'buy').order_by(Fill.timestamp.desc()).limit(1)
            last_fill = session.exec(statement).first()
            if last_fill:
                return float(last_fill.price)
            return None


# Registration for easy parsing
DATA_PROVIDERS = {
    "CURRENT_PRICE": CurrentPriceProvider(),
    "LAST_ENTRY_PRICE": LastEntryPriceProvider(),
}
