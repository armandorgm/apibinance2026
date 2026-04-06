from typing import Any, Dict
from app.core.exchange import exchange_manager
import traceback

class BaseAction:
    async def execute(self, symbol: str, params: dict, context_params: dict) -> Dict[str, Any]:
        raise NotImplementedError()

class BuyMinNotionalAction(BaseAction):
    """Buys the minimum amount around 5 USD at the current market price."""
    async def execute(self, symbol: str, params: dict, context_params: dict) -> Dict[str, Any]:
        try:
            current_price = context_params.get("current_price")
            if not current_price:
                # Fallback to fetch explicitly if missing
                ticker = await exchange_manager.execute_with_retry("fetchTicker", symbol)
                current_price = ticker.get('last')
            
            if not current_price:
                return {"success": False, "error": "Cannot fetch current price for min notional"}
                
            notional_target = 5.05 # Slightly above $5 minimum
            qty = notional_target / current_price
            
            # Use formatAmount from exchange manager logic or let CCXT handle precision using createOrder
            qty_rounded = round(qty, 4) # Very naive rounding, exchange manager ideally enforces precision
            
            order = await exchange_manager.execute_with_retry(
                "createMarketBuyOrder",
                symbol,
                qty_rounded,
                {"reduceOnly": False}
            )
            return {"success": True, "action": "BUY_MIN_NOTIONAL", "result": order, "qty": qty_rounded}
        except Exception as e:
            traceback.print_exc()
            return {"success": False, "error": str(e), "action": "BUY_MIN_NOTIONAL"}

# Registry for easy parsing
ACTIONS = {
    "BUY_MIN_NOTIONAL": BuyMinNotionalAction()
}
