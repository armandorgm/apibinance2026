from typing import Any

from pydantic import BaseModel

class ConditionNode(BaseModel):
    provider_a: str
    params_a: dict = {}
    operator: str # 'GT', 'LT', 'EQ'
    provider_b: str
    params_b: dict = {}
    offset: float = 0.0

class BaseEvaluator:
    async def evaluate(self, symbol: str, condition: ConditionNode, data_providers: dict, context_params: dict) -> bool:
        raise NotImplementedError()

class RelationalEvaluator(BaseEvaluator):
    async def evaluate(self, symbol: str, condition: ConditionNode, data_providers: dict, context_params: dict) -> bool:
        provider_a = data_providers.get(condition.provider_a)
        provider_b = data_providers.get(condition.provider_b)
        
        if not provider_a or not provider_b:
            return False
            
        value_a = await provider_a.get_value(symbol, {**condition.params_a, **context_params})
        value_b = await provider_b.get_value(symbol, {**condition.params_b, **context_params})
        
        if value_a is None or value_b is None:
            return False
            
        target_value = float(value_b) + condition.offset
        
        if condition.operator == 'GT':
            return float(value_a) > target_value
        elif condition.operator == 'LT':
            return float(value_a) < target_value
        elif condition.operator == 'EQ':
            return float(value_a) == target_value
            
        return False
