from .actions import BuyMinNotionalAction, AdaptiveOTOScalingAction, RepairChaseAction
from .native_actions import NativeOTOScalingAction

# Centralized Registry to break circular imports between actions.py and native_actions.py
ACTIONS = {
    "BUY_MIN_NOTIONAL": BuyMinNotionalAction(),
    "ADAPTIVE_OTO": AdaptiveOTOScalingAction(),
    "ADAPTIVE_OTO_V2": NativeOTOScalingAction(),
    "REPAIR_CHASE": RepairChaseAction()
}
