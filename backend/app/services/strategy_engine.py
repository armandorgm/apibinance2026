"""
Dynamic Rules Motor (Pipeline Engine).
Evaluates persistent BotPipelines from DB utilizing Node Evaluators.
"""
import json
from typing import List, Dict, Optional, Any
from app.core.logger import logger
from app.db.database import get_session_direct, BotPipeline, BotSignal
from pydantic import BaseModel
from .pipeline_engine.data_providers import DATA_PROVIDERS
from .pipeline_engine.evaluators import RelationalEvaluator, ConditionNode
from .pipeline_engine.registry import ACTIONS

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

    async def evaluate_stream_event(self, symbol: str, current_price: float):
        """Processes live WS ticks for CHASE logic pipelines.
        
        Includes a polling fallback: every ~15 ticks, we verify the order status
        via REST API to catch fills that the WS order stream might have missed
        (e.g., after uvicorn hot-reload kills the stream task).
        """
        with get_session_direct() as session:
            from app.db.database import BotPipelineProcess
            active_processes = session.query(BotPipelineProcess).filter(
                BotPipelineProcess.symbol == symbol,
                BotPipelineProcess.status == "CHASING"
            ).all()

            if not active_processes:
                from app.core.stream_service import stream_manager
                stream_manager.unsubscribe(symbol)
                return

            from .pipeline_engine.registry import ACTIONS
            from .pipeline_engine.actions import AdaptiveOTOScalingAction
            from .pipeline_engine.native_actions import NativeOTOScalingAction
            from app.core.exchange import exchange_manager

            for process in active_processes:
                # Optimized Handler Routing (SOLID Heuristic)
                handler = NativeOTOScalingAction if "NATIVE" in (process.sub_status or "") else AdaptiveOTOScalingAction
                
                # Update tick price for logic and in-memory registry
                exchange_manager.update_price(symbol, current_price)

                # --- POLLING FALLBACK ---
                if not hasattr(self, '_tick_counter'):
                    self._tick_counter = {}
                key = process.entry_order_id or ""
                self._tick_counter[key] = self._tick_counter.get(key, 0) + 1

                if self._tick_counter[key] >= 15 and process.entry_order_id and process.entry_order_id != "INITIAL_REJECTED":
                    self._tick_counter[key] = 0
                    try:
                        order = await exchange_manager.fetch_order_raw(symbol, process.entry_order_id)
                        order_status = (order.get('status') or '').lower()
                        if order_status == 'closed':
                            logger.info(f"[FALLBACK] Order {process.entry_order_id} already FILLED. Triggering {handler.__name__}.handle_fill.")
                            await handler.handle_fill(process, session)
                            continue
                        elif order_status in ['canceled', 'expired']:
                            logger.info(f"[FALLBACK] Order {process.entry_order_id} is {order_status}. Re-routing to handle_order_event.")
                            await handler.handle_order_event(process, order, session)
                            continue
                    except Exception as e:
                        logger.debug(f"[FALLBACK] Polling check failed for {process.entry_order_id}: {e}")

                # --- NORMAL TICK HANDLING ---
                try:
                    await handler.handle_tick(process, current_price, session)
                except Exception as chase_err:
                    logger.warning(f"[STRATEGY] Chase tick failed for {symbol} (Process {process.id}): {chase_err}")

    async def evaluate_stream_order(self, order_data: Dict[str, Any]):
        """Processes live WS order updates (FILLED, CANCELED) for OTO logic."""
        from app.core.exchange import exchange_manager
        
        symbol = await exchange_manager.normalize_symbol(order_data.get('symbol', ''))
        order_id = str(order_data.get('id', ''))
        status = order_data.get('status', '').lower()
        
        logger.debug(f"[STREAM] Processing Order Update: {symbol} ID={order_id} ST={status}")
        
        with get_session_direct() as session:
            from app.db.database import BotPipelineProcess
            process = session.query(BotPipelineProcess).filter(
                BotPipelineProcess.symbol == symbol,
                BotPipelineProcess.entry_order_id == order_id
            ).first()

            if not process:
                return

            from .pipeline_engine.actions import AdaptiveOTOScalingAction
            from .pipeline_engine.native_actions import NativeOTOScalingAction
            
            # Optimized Handler Routing
            handler = NativeOTOScalingAction if "NATIVE" in (process.sub_status or "") else AdaptiveOTOScalingAction
            
            # Delegate to unified handler
            await handler.handle_order_event(process, order_data, session)
