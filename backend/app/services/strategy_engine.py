"""
Dynamic Rules Motor (Pipeline Engine).
Evaluates persistent BotPipelines from DB utilizing Node Evaluators.
"""
import asyncio
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
        self._chase_registry: set[str] = set() # In-memory set of symbols currently being chased
        self._locks: Dict[str, asyncio.Lock] = {}
        self.is_running = True
        logger.info("[PipelineEngine] Initialized with empty chase registry.")

    def register_chase(self, symbol: str):
        """Adds a symbol to the in-memory chase registry."""
        self._chase_registry.add(symbol)
        logger.debug(f"[PipelineEngine] Registered {symbol} for chasing.")

    def unregister_chase(self, symbol: str):
        """Removes a symbol from the in-memory chase registry."""
        if symbol in self._chase_registry:
            self._chase_registry.remove(symbol)
            logger.debug(f"[PipelineEngine] Unregistered {symbol} from chasing.")

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
        """
        Main hook for the WebSocket stream.
        Optimized with per-symbol locks to prevent QueuePool exhaustion (V5.9.36).
        """
        if not self.is_running or symbol not in self._chase_registry:
            return

        # 1. Get or create lock for symbol
        if symbol not in self._locks:
            self._locks[symbol] = asyncio.Lock()
        
        async with self._locks[symbol]:
            try:
                with get_session_direct() as session:
                    from app.db.database import BotPipelineProcess
                    from app.core.exchange import exchange_manager
                    from app.services.chase_v2_service import chase_v2_service
                    from .pipeline_engine.native_actions import NativeOTOScalingAction
                    from .pipeline_engine.actions import AdaptiveOTOScalingAction

                    # Explicit Handler Map
                    HANDLER_MAP = {
                        "CHASE_V2": chase_v2_service,
                        "NATIVE_OTO": NativeOTOScalingAction,
                        "ADAPTIVE_OTO": AdaptiveOTOScalingAction
                    }

                    active_processes = session.query(BotPipelineProcess).filter(
                        BotPipelineProcess.symbol == symbol,
                        BotPipelineProcess.status == "CHASING",
                        BotPipelineProcess.sub_status != "PLACING_TP" # Guard against race conditions (V5.9.36)
                    ).all()

                    if not active_processes:
                        self.unregister_chase(symbol)
                        return

                    for process in active_processes:
                        handler = HANDLER_MAP.get(process.handler_type, chase_v2_service)
                        
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
                                    logger.info(f"[FALLBACK] Order {process.entry_order_id} already FILLED. Triggering handle_fill.")
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
                            
            except Exception as e:
                logger.error(f"[STRATEGY ENGINE] Error processing tick for {symbol}: {e}")

    async def evaluate_stream_order(self, order_data: Dict[str, Any]):
        """Processes live WS order updates (FILLED, CANCELED) for OTO logic."""
        from app.core.exchange import exchange_manager
        
        symbol = await exchange_manager.normalize_symbol(order_data.get('symbol', ''))
        order_id = str(order_data.get('id', ''))
        status = order_data.get('status', '').lower()
        
        logger.debug(f"[STREAM] Processing Order Update: {symbol} ID={order_id} ST={status}")
        
        # Guard with per-symbol lock to prevent race with polling fallback
        if symbol not in self._locks:
            self._locks[symbol] = asyncio.Lock()
            
        async with self._locks[symbol]:
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
                from app.services.chase_v2_service import chase_v2_service
                
                # Unified Handler Map
                HANDLER_MAP = {
                    "CHASE_V2": chase_v2_service,
                    "NATIVE_OTO": NativeOTOScalingAction,
                    "ADAPTIVE_OTO": AdaptiveOTOScalingAction
                }

                # Dispatch using explicit handler_type with Chase V2 as safe fallback
                handler = HANDLER_MAP.get(process.handler_type, chase_v2_service)
                
                # Delegate to unified handler
                await handler.handle_order_event(process, order_data, session)
