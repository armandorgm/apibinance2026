from datetime import datetime, timedelta
from typing import Optional
from app.db.database import BotPipelineProcess
import logging

logger = logging.getLogger("apibinance2026")

class ChaseDecisionEngine:
    """
    SOLID Principle: Single Responsibility.
    Responsible only for deciding if a chase update (order replacement) should occur.
    """
    
    COOLDOWN_SECONDS = 5
    PRICE_DIFF_THRESHOLD = 0.0005 # 0.05%
    
    @staticmethod
    def should_update(
        process: BotPipelineProcess, 
        current_price: float, 
        cooldown_seconds: Optional[int] = None,
        price_threshold: Optional[float] = None
    ) -> bool:
        """
        Evaluates if the opening order should be replaced based on time and price.
        """
        # 0. Configuration (Use provided params or defaults)
        cooldown = cooldown_seconds if cooldown_seconds is not None else ChaseDecisionEngine.COOLDOWN_SECONDS
        threshold = price_threshold if price_threshold is not None else ChaseDecisionEngine.PRICE_DIFF_THRESHOLD

        # CRITICAL: If we are in RECOVERING state, we have NO order in the market.
        # We MUST bypass threshold checks to get an order in as soon as possible.
        if process.sub_status == "RECOVERING" or process.entry_order_id == "INITIAL_REJECTED":
            return True

        # 1. Time Throttling (Cooldonw)
        # Use updated_at to track last execution
        last_update = process.updated_at or process.created_at
        elapsed = (datetime.utcnow() - last_update).total_seconds()
        
        if elapsed < cooldown:
            # logger.debug(f"[CHASE] Cooldown active for {process.symbol}. {elapsed:.1f}s elapsed.")
            return False
            
        # 2. Price Threshold Check
        # Compare current market price with the price when we LAST moved (last_tick_price)
        if process.last_tick_price is None:
            return True  # First time move

        price_diff_percent = abs(current_price - process.last_tick_price) / process.last_tick_price

        if price_diff_percent < threshold:
            # logger.debug(f"[CHASE] Price move too small for {process.symbol} ({price_diff_percent:.5%})")
            return False

        side = (process.side or "").lower()
        if side == "buy" and current_price < process.last_tick_price:
            return False
        if side == "sell" and current_price > process.last_tick_price:
            return False

        return True
