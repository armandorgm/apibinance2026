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
    def should_update(process: BotPipelineProcess, current_price: float) -> bool:
        """
        Evaluates if the opening order should be replaced based on time and price.
        """
        # 1. Time Throttling (Cooldonw)
        # Use updated_at to track last execution
        last_update = process.updated_at or process.created_at
        elapsed = (datetime.utcnow() - last_update).total_seconds()
        
        if elapsed < ChaseDecisionEngine.COOLDOWN_SECONDS:
            # logger.debug(f"[CHASE] Cooldown active for {process.symbol}. {elapsed:.1f}s elapsed.")
            return False
            
        # 2. Price Threshold Check
        # Compare current market price with the price when we LAST moved (last_tick_price)
        if not process.last_tick_price:
            return True # First time move
            
        price_diff_percent = abs(current_price - process.last_tick_price) / process.last_tick_price
        
        if price_diff_percent < ChaseDecisionEngine.PRICE_DIFF_THRESHOLD:
            # logger.debug(f"[CHASE] Price move too small for {process.symbol} ({price_diff_percent:.5%})")
            return False
            
        # 3. Directional Logic (Smart Chasing)
        # If we are BUYING (Long), we only want to move the order UP if the price is escaping up.
        # If we are SELLING (Short), we only want to move the order DOWN if the price is escaping down.
        side = (process.side or "buy").lower()
        
        if side == "buy":
            # Chasing up: move only if the price is higher than our benchmark
            if current_price < process.last_tick_price:
                # logger.debug(f"[CHASE] Price moved DOWN for BUY order on {process.symbol}. Skipping move.")
                return False
        else:
            # Chasing down: move only if the price is lower than our benchmark
            if current_price > process.last_tick_price:
                # logger.debug(f"[CHASE] Price moved UP for SELL order on {process.symbol}. Skipping move.")
                return False
                
        return True
