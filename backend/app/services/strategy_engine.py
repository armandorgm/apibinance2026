"""
Dynamic Rules Motor (Pipeline Engine).
Evaluates persistent BotPipelines from DB utilizing Node Evaluators.
"""
import json
from typing import List, Dict, Optional, Any
from app.db.database import get_session_direct, BotPipeline, BotSignal
from pydantic import BaseModel
from .pipeline_engine.data_providers import DATA_PROVIDERS
from .pipeline_engine.evaluators import RelationalEvaluator, ConditionNode
from .pipeline_engine.actions import ACTIONS

class PipelineEngine:
    def __init__(self):
        self.evaluator = RelationalEvaluator()

    async def evaluate_and_execute(self, symbol: str, current_price: float) -> List[Dict[str, Any]]:
        """Evaluates all active pipelines for the given symbol."""
        results = []
        with get_session_direct() as session:
            pipelines = session.query(BotPipeline).filter(
                BotPipeline.is_active == True,
                BotPipeline.symbol == symbol,
                BotPipeline.trigger_event == "POLLING"
            ).all()

            for pipeline in pipelines:
                try:
                    config = json.loads(pipeline.pipeline_config)
                    # Expected JSON format: 
                    # {
                    #   "condition": {"provider_a": "LAST_ENTRY_PRICE", "operator": "GT", "provider_b": "CURRENT_PRICE", "offset": 0.0005},
                    #   "action": {"type": "BUY_MIN_NOTIONAL"}
                    # }
                    
                    if "condition" in config:
                        cond_node = ConditionNode(**config["condition"])
                        is_triggered = await self.evaluator.evaluate(
                            symbol, 
                            cond_node, 
                            DATA_PROVIDERS, 
                            context_params={"current_price": current_price}
                        )
                        
                        if is_triggered:
                            action_config = config.get("action", {})
                            action_type = action_config.get("type")
                            action_impl = ACTIONS.get(action_type)
                            
                            if action_impl:
                                exec_res = await action_impl.execute(symbol, action_config, {"current_price": current_price})
                                
                                # Log signal
                                signal = BotSignal(
                                    symbol=symbol,
                                    rule_triggered=pipeline.name,
                                    action_taken=action_type,
                                    params_snapshot=json.dumps({"price": current_price}),
                                    success=exec_res.get("success", False),
                                    exchange_response=json.dumps(exec_res.get("result", {})),
                                    error_message=exec_res.get("error")
                                )
                                session.add(signal)
                                session.commit()
                                
                                results.append(exec_res)
                except Exception as e:
                    print(f"[PipelineEngine] Error evaluating pipeline {pipeline.id}: {e}")
                    
        return results
