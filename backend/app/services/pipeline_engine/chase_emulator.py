from typing import List, Optional, Dict, Any
from datetime import datetime
from .chase_manager import ChaseDecisionEngine
from app.db.database import BotPipelineProcess

class ChaseEmulator:
    """
    Unified Emulator for Chase Logic.
    Used by both automated tests and the visual playground.
    Stateful for simulation but can be used in a stateless way by passing the state.
    """
    
    def __init__(
        self, 
        side: str, 
        order_price: float, 
        last_tick_price: Optional[float] = None,
        last_update: Optional[datetime] = None,
        cooldown: int = 5, 
        threshold: float = 0.0005
    ):
        self.side = side.lower()
        self.order_price = order_price
        self.last_tick_price = last_tick_price if last_tick_price is not None else order_price
        self.last_update = last_update if last_update is not None else datetime.utcnow()
        self.cooldown = cooldown
        self.threshold = threshold
        self.status = "CHASING" # CHASING, FILLED
    
    def on_tick(self, current_price: float) -> Dict[str, Any]:
        """
        Processes a single price tick and returns the result and new state.
        """
        if self.status == "FILLED":
            return {
                "status": "FILLED",
                "order_price": self.order_price,
                "reason": "Order already filled",
                "should_update": False
            }

        # 1. Check for FILL (Price hits or crosses the order)
        # For a BUY order, fill happens if market price <= order price
        # For a SELL order, fill happens if market price >= order price
        is_fill = False
        if self.side == "buy":
            if current_price <= self.order_price:
                is_fill = True
        else: # sell
            if current_price >= self.order_price:
                is_fill = True

        if is_fill:
            self.status = "FILLED"
            return {
                "status": "FILLED",
                "order_price": self.order_price,
                "reason": f"Execution! Price {current_price} hit the order at {self.order_price}",
                "should_update": False
            }

        # 2. Check for CHASE replacement
        # Create a mock process to leverage ChaseDecisionEngine logic
        mock_process = BotPipelineProcess(
            symbol="SIM",
            side=self.side,
            last_tick_price=self.last_tick_price,
            updated_at=self.last_update,
            created_at=self.last_update
        )

        should_update = ChaseDecisionEngine.should_update(
            process=mock_process,
            current_price=current_price,
            cooldown_seconds=self.cooldown,
            price_threshold=self.threshold
        )

        if should_update:
            old_price = self.order_price
            # In a real chase, the order price follows the market price (plus/minus 1 tick)
            # For simulation, we'll assume the order price is the current price
            self.order_price = current_price
            self.last_tick_price = current_price
            self.last_update = datetime.utcnow()
            
            return {
                "status": "CHASING",
                "action": "REPLACED",
                "old_price": old_price,
                "new_price": self.order_price,
                "reason": "Price escaped! Chasing the movement.",
                "should_update": True,
                "last_update_iso": self.last_update.isoformat()
            }

        return {
            "status": "CHASING",
            "action": "WAITING",
            "order_price": self.order_price,
            "reason": "Holding position (cooldown, threshold or price moving towards us)",
            "should_update": False
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "side": self.side,
            "order_price": self.order_price,
            "last_tick_price": self.last_tick_price,
            "last_update_iso": self.last_update.isoformat(),
            "status": self.status
        }
