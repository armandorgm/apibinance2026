"""
Functional Rules Motor (Python version).
Translates trading context into automated actions based on pre-defined strategies.
"""
import time
from typing import List, Dict, Optional, Any, Callable
from pydantic import BaseModel

class TradingContext(BaseModel):
    last_purchase_time: int  # Unix timestamp in ms
    active_trades_count: int
    last_range: Optional[List[float]] = None # e.g. [1.0, 4.0]
    current_time: Optional[int] = None

class RuleActionResult(BaseModel):
    trigger: bool
    rule_name: Optional[str] = None
    action: Optional[str] = None # 'NEW_ORDER', 'UPDATE_RANGE'
    params: Optional[Dict[str, Any]] = None

TradingRule = Callable[[TradingContext], RuleActionResult]

# --- Rules Implementation ---

def time_rule(ctx: TradingContext) -> RuleActionResult:
    """Rule 1 (Time): Trigger NEW_ORDER if last_purchase_age >= 24h."""
    current_time = ctx.current_time or int(time.time() * 1000)
    age_ms = current_time - ctx.last_purchase_time
    is_expired = age_ms >= 24 * 60 * 60 * 1000

    return RuleActionResult(
        trigger=is_expired,
        rule_name="TIME_24H",
        action="NEW_ORDER" if is_expired else None
    )

def scaling_l1_rule(ctx: TradingContext) -> RuleActionResult:
    """Rule 2 (Scaling Level 1): If active trades exist and last_range == [1, 4], set new_range = [25%, 75%]."""
    has_active_trades = ctx.active_trades_count > 0
    is_target_range = ctx.last_range and ctx.last_range[0] == 1.0 and ctx.last_range[1] == 4.0

    if has_active_trades and is_target_range:
        return RuleActionResult(
            trigger=True,
            rule_name="SCALING_L1",
            action="UPDATE_RANGE",
            params={"new_range": [25.0, 75.0]}
        )
    return RuleActionResult(trigger=False)

def scaling_l2_rule(ctx: TradingContext) -> RuleActionResult:
    """Rule 3 (Scaling Level 2): If active trades persist, set new_range = [0%, 50%]."""
    has_active_trades = ctx.active_trades_count > 0

    if has_active_trades:
        return RuleActionResult(
            trigger=True,
            rule_name="SCALING_L2",
            action="UPDATE_RANGE",
            params={"new_range": [0.0, 50.0]}
        )
    return RuleActionResult(trigger=False)

# --- Engine ---

class StrategyEngine:
    def __init__(self):
        self.rules: List[TradingRule] = [
            time_rule,
            scaling_l1_rule,
            scaling_l2_rule,
        ]

    def evaluate(self, context: TradingContext) -> RuleActionResult:
        """Evaluates the context and returns the FIRST rule that triggers."""
        for rule in self.rules:
            result = rule(context)
            if result.trigger:
                return result
        return RuleActionResult(trigger=False)
