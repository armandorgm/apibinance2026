from typing import Any, Dict
from app.core.exchange import exchange_manager
import traceback
from app.core.logger import logger

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
                ticker = await exchange_manager.fetch_ticker(symbol)
                current_price = ticker.get('last')
            
            if not current_price:
                return {"success": False, "error": "Cannot fetch current price for min notional"}
                
            notional_target = 5.05 # Slightly above $5 minimum
            qty = notional_target / current_price
            
            # Use formatAmount from exchange manager logic or let CCXT handle precision using createOrder
            qty_rounded = round(qty, 4) # Very naive rounding, exchange manager ideally enforces precision
            
            order = await exchange_manager.create_order(
                symbol,
                "market",
                "buy", # Hardcoded since it says BuyMinNotional
                qty_rounded,
                None,
                {"reduceOnly": False}
            )
            return {"success": True, "action": "BUY_MIN_NOTIONAL", "result": order, "qty": qty_rounded}
        except Exception as e:
            traceback.print_exc()
            return {"success": False, "error": str(e), "action": "BUY_MIN_NOTIONAL"}

class AdaptiveOTOScalingAction(BaseAction):
    """
    Stateful Action. Implements the Chase & Scalp logic.
    - Chase: Keeps entry order 1 tick away from market using CCXT pro stream.
    - OTO: Places a TP automatically when entry is filled.
    """
    async def execute(self, symbol: str, params: dict, context_params: dict) -> Dict[str, Any]:
        """Initial Trigger when rule activates"""
        try:
            current_price = context_params.get("current_price")
            side = params.get("side", "buy")
            notional_usd = params.get("amount", 20.0)
            qty = float(notional_usd) / float(current_price)
            pipeline_id = params.get("pipeline_id")
            
            from app.db.database import get_session_direct, BotPipelineProcess
            
            # Ensure symbol is normalized to CCXT standard for consistent event routing
            symbol = await exchange_manager.normalize_symbol(symbol)
            
            with get_session_direct() as session:
                active_chase = session.query(BotPipelineProcess).filter(
                    BotPipelineProcess.symbol == symbol,
                    BotPipelineProcess.status == "CHASING"
                ).first()
                if active_chase:
                    return {"success": False, "error": "Already chasing"}

                # Debug log: parameters before precision
                logger.debug(f"[AdaptiveOTO] Params before precision: qty={qty}, price={current_price}, side={side}")

                # Apply Precision
                qty_str = await exchange_manager.amount_to_precision(symbol, float(qty))
                price_str = await exchange_manager.price_to_precision(symbol, float(current_price))

                # V5.9.1: Robustness check for Binance Min Notional ($5.0)
                # If rounding down dropped the notional below $5, we try to nudge it UP
                # by adding a small amount to the raw qty and re-applying precision.
                final_notional = float(qty_str) * float(price_str)
                if final_notional < 5.0 and not params.get('reduceOnly'):
                    logger.warning(f"[AdaptiveOTO] Notional {final_notional} too low (<$5). Nudging qty UP.")
                    # Try raw qty + 5% or at least one unit
                    raw_qty = float(qty) * 1.02 
                    qty_str = await exchange_manager.amount_to_precision(symbol, raw_qty)
                    # Re-check
                    final_notional = float(qty_str) * float(price_str)
                    logger.info(f"[AdaptiveOTO] Nudged Notional: {final_notional}")

                logger.debug(f"[AdaptiveOTO] Precision strings: qty_str={qty_str}, price_str={price_str}")

                # 1. Create initial Limit Post-Only order 
                entry_order = None
                initial_rejection = False
                
                try:
                    entry_order = await exchange_manager.create_order(
                        symbol=symbol,
                        side=side,
                        amount=qty_str,
                        price=price_str,
                        order_type="limit",
                        params={"timeInForce": "GTX"} 
                    )
                    logger.debug(f"[AdaptiveOTO] Entry order created successfully: {entry_order.get('id')}")
                except Exception as order_error:
                    err_msg = str(order_error)
                    if "-5022" in err_msg or "-2021" in err_msg or "Post Only" in err_msg:
                        logger.warning(f"[AdaptiveOTO] Initial order rejected by Post-Only: {err_msg}. Switching to auto-recovery.")
                        initial_rejection = True
                    else:
                        logger.error(f"[AdaptiveOTO] Initial order failed: {order_error}")
                        raise order_error
                
                try:
                    # 2. Start tracking session
                    process = BotPipelineProcess(
                        pipeline_id=pipeline_id or 0,
                        symbol=symbol,
                        entry_order_id=str(entry_order['id']) if entry_order else "INITIAL_REJECTED",
                        side=side,
                        amount=float(qty_str),
                        last_tick_price=current_price,
                        last_order_price=float(price_str),
                        retry_count=1 if initial_rejection else 0, # Start count if we already failed once
                        status="CHASING",
                        sub_status="WAITING_FILL" if not initial_rejection else "RECOVERING",
                        handler_type="ADAPTIVE_OTO",
                        custom_cooldown=params.get("cooldown"),
                        custom_threshold=params.get("threshold")
                    )
                    session.add(process)
                    session.commit()
                    session.refresh(process) # Get ID for signals
                    
                    # Log Signal for tracking
                    from app.db.database import BotSignal
                    import json
                    signal = BotSignal(
                        symbol=symbol,
                        rule_triggered="INITIAL_PLACEMENT" if not initial_rejection else "POST_ONLY_RECOVERY_STARTED",
                        action_taken="INIT_CHASE",
                        params_snapshot=json.dumps({"price": price_str, "qty": qty_str, "initial_match_fail": initial_rejection}),
                        success=True
                    )
                    session.add(signal)
                    session.commit()

                    # 3. If we failed initially, trigger the first retry IMMEDIATELY with 1-tick offset
                    if initial_rejection:
                        exchange_ccxt = await exchange_manager.get_exchange()
                        await exchange_ccxt.load_markets()
                        market = exchange_ccxt.market(symbol)
                        tick_size = market['precision']['price']
                        
                        target_price = current_price - float(tick_size) if side == "buy" else current_price + float(tick_size)
                        
                        logger.info(f"[AdaptiveOTO] Triggering immediate recovery retry at {target_price}")
                        await AdaptiveOTOScalingAction._execute_order_replacement(process, target_price, session, reason="Initial Post-Only Recovery")

                    # Suscribir stream de alta frecuencia
                    from app.core.stream_service import stream_manager
                    await stream_manager.subscribe(symbol)
                    
                    return {"success": True, "action": "ADAPTIVE_OTO", "process_id": process.id}
                except Exception as db_error:
                    # CRITICAL: If DB fails, we must cancel the order on Binance to avoid "Orphans"
                    if entry_order:
                        logger.error(f"[AdaptiveOTO] DB Commit failed. CANCELLING orphan order {entry_order.get('id')}")
                        try:
                            exchange_ccxt = await exchange_manager.get_exchange()
                            await exchange_ccxt.cancel_order(entry_order['id'], symbol)
                        except Exception as cancel_err:
                            logger.error(f"[AdaptiveOTO] Failed to cancel orphan order! {cancel_err}")
                    raise db_error

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"[AdaptiveOTO] Exception: {tb}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def handle_tick(process, current_price: float, session):
        """Called every millisecond by WS Stream. Fast chase execution."""
        from .chase_manager import ChaseDecisionEngine
        
        # 1. SOLID Principle: Delegate decision to the engine
        if not ChaseDecisionEngine.should_update(
            process, 
            current_price,
            cooldown_seconds=getattr(process, 'custom_cooldown', None),
            price_threshold=getattr(process, 'custom_threshold', None)
        ):
            return

        logger.info(f"[CHASE] Throttling passed. Updating order for {process.symbol} at {current_price}")
        process.sub_status = "CHASING"
        session.commit()
        await AdaptiveOTOScalingAction._execute_order_replacement(process, current_price, session, reason="Price Chase")

    @staticmethod
    async def handle_order_event(process, order_data: Dict[str, Any], session):
        """Processes live WS order updates (FILLED, CANCELED, EXPIRED) for OTO logic."""
        status = order_data.get('status', '').lower()
        symbol = process.symbol

        if status == 'closed':
            await AdaptiveOTOScalingAction.handle_fill(process, session)

        elif status == 'expired':
            # GTX (Post-Only) order was auto-expired by Binance when the price crossed
            # our level. This is NOT a user cancellation — we must chase and re-place.
            logger.info(f"[CHASE] GTX order expired for {symbol}. Re-placing at latest tick price.")
            from app.db.database import BotSignal
            import json
            signal = BotSignal(
                symbol=symbol,
                rule_triggered="GTX_EXPIRED",
                action_taken="RETRY_GTX_EXPIRE",
                params_snapshot=json.dumps({"last_tick": process.last_tick_price}),
                success=True
            )
            session.add(signal)
            session.commit()
            # Re-place immediately at the last known market price
            await AdaptiveOTOScalingAction._execute_order_replacement(
                process, process.last_tick_price or 0.0, session, reason="GTX Expired - Retry"
            )

        elif status in ['canceled', 'rejected']:
            # Check if it was a Post-Only creation-time rejection (Binance error -2021)
            info = order_data.get('info', {})
            error_code = info.get('code') or info.get('ec')

            is_post_only_reject = False
            if error_code in [-2021, "-2021"]:
                is_post_only_reject = True

            # Also check message text
            msg = str(info.get('msg', '')).lower()
            if "post-only" in msg or "immediately match" in msg:
                is_post_only_reject = True

            if is_post_only_reject:
                if process.retry_count < 10:
                    process.retry_count += 1

                    from app.db.database import BotSignal
                    import json
                    signal = BotSignal(
                        symbol=symbol,
                        rule_triggered=f"Post-Only Retry {process.retry_count}/10",
                        action_taken="RETRY_POST_ONLY",
                        params_snapshot=json.dumps({"attempt": process.retry_count, "last_tick": process.last_tick_price}),
                        success=True
                    )
                    session.add(signal)
                    process.sub_status = "RECOVERING"
                    session.commit()

                    exchange_ccxt = await exchange_manager.get_exchange()
                    await exchange_ccxt.load_markets()
                    market = exchange_ccxt.market(symbol)
                    tick_size = market['precision']['price']

                    # V5.9.3: Accurate Maker Pricing (ask - 1 tick for long)
                    # This ensures the most competitive bid while staying Maker
                    ticker = await exchange_manager.fetch_ticker(symbol)
                    ask = ticker.get('ask')
                    bid = ticker.get('bid')
                    
                    side = process.side or "buy"
                    
                    if side == "buy":
                        # Target ask - 1 tick for maximum competitiveness as Maker
                        new_price = (ask - float(tick_size)) if ask else (process.last_tick_price - float(tick_size))
                    else:
                        # Target bid + 1 tick for short
                        new_price = (bid + float(tick_size)) if bid else (process.last_tick_price + float(tick_size))

                    logger.info(f"[CHASE] Post-Only rejected. Retry {process.retry_count}/10 at {new_price} (Maker Target)")
                    await AdaptiveOTOScalingAction._execute_order_replacement(process, new_price, session, reason=f"Post-Only Retry {process.retry_count}")
                else:
                    logger.error(f"[CHASE] Max Post-Only retries (10) reached for {symbol}. Aborting.")
                    await AdaptiveOTOScalingAction.handle_abort(process, session)
            else:
                # Explicit user cancellation or unrecoverable error → abort
                logger.info(f"[CHASE] Order explicitly canceled for {symbol}. Aborting chase.")
                await AdaptiveOTOScalingAction.handle_abort(process, session)

    @staticmethod
    async def _execute_order_replacement(process, target_price: float, session, reason: str = "Chase"):
        """Internal helper to swap orders and update DB status."""
        from datetime import datetime
        import json
        from app.db.database import BotSignal
        
        try:
            side = process.side or "buy"
            qty = process.amount
            symbol = process.symbol
            
            if qty <= 0: return

            # 1. Cancel old (Optional if we come from a rejection event, but safe)
            exchange_ccxt = await exchange_manager.get_exchange()
            if process.entry_order_id and process.entry_order_id != "INITIAL_REJECTED":
                try:
                    # If we are here because of a CANCELED event, this might fail, which is fine.
                    await exchange_ccxt.cancel_order(process.entry_order_id, symbol)
                except Exception as cancel_err:
                    pass # Already handled or irrelevant for event-driven logic

            # 2. Apply Precision
            qty_str = await exchange_manager.amount_to_precision(symbol, float(qty))
            price_str = await exchange_manager.price_to_precision(symbol, float(target_price))
            
            # 3. Place new (Post-Only GTX)
            new_order = await exchange_manager.create_order(
                symbol=symbol,
                side=side,
                amount=qty_str,
                price=price_str,
                order_type="limit",
                params={"timeInForce": "GTX"}
            )
            
            # 4. Update DB state
            process.entry_order_id = str(new_order['id'])
            # Don't overwrite last_tick_price if it's a retry, we want to know the market price at rejection
            if "Retry" not in reason:
                process.last_tick_price = target_price
            
            process.last_order_price = float(price_str)
            process.sub_status = "WAITING_FILL"
            process.updated_at = datetime.utcnow()
            session.commit()
            
            # Log Signal
            signal = BotSignal(
                symbol=symbol,
                rule_triggered=reason,
                action_taken="UPDATE_ORDER",
                params_snapshot=json.dumps({"price": price_str, "order_id": new_order['id']}),
                success=True,
                exchange_response=json.dumps(new_order)
            )
            session.add(signal)
            session.commit()
            
            logger.info(f"[CHASE] Order replaced: {new_order['id']} at {price_str} ({reason})")

        except Exception as e:
            err_msg = str(e)
            is_post_only = "-5022" in err_msg or "-2021" in err_msg or "Post Only" in err_msg
            
            if is_post_only:
                if process.retry_count < 10:
                    process.retry_count += 1
                    process.entry_order_id = "INITIAL_REJECTED"
                    process.sub_status = "RECOVERING"
                    logger.warning(f"[_execute_order_replacement] Post-Only reject during {reason}. Retry {process.retry_count}/10. State set to RECOVERING.")
                else:
                    logger.error(f"[_execute_order_replacement] Max retries reached during {reason}. Aborting.")
                    await AdaptiveOTOScalingAction.handle_abort(process, session)
            else:
                logger.error(f"[_execute_order_replacement] Unexpected failure: {err_msg}")

            session.commit()
            
            # Log failure Signal
            signal = BotSignal(
                symbol=process.symbol,
                rule_triggered=reason,
                action_taken="RETRY_REQUIRED" if is_post_only else "UPDATE_ORDER_FAILED",
                params_snapshot=json.dumps({"target_price": target_price, "retry": process.retry_count}),
                success=False,
                error_message=err_msg
            )
            session.add(signal)
            session.commit()

    @staticmethod
    async def handle_fill(process, session):
        """Called when entry order is fully closed/filled."""
        logger.info(f"[CHASE] Entry FILLED for {process.symbol}. Placing TP.")
        try:
            order = await exchange_manager.fetch_order_raw(process.symbol, process.entry_order_id)
            if not order: return
            filled_qty = order['filled']
            entry_price = order['average'] or order['price']
            tp_side = "sell" if order['side'] == "buy" else "buy"
            
            # Default TP is 1% away for fallback
            tp_price = entry_price * 1.01 if tp_side == "sell" else entry_price * 0.99
            
            tp_client_id = f"TP_OTO_PID_{process.id}"
            
            # --- 1. Validación Activa (Pre-Flight Check) ---
            open_orders = await exchange_manager.fetch_open_orders(process.symbol)
            for o in open_orders:
                o_client_id = o.get('clientOrderId') or o.get('info', {}).get('clientOrderId', '')
                if o_client_id == tp_client_id:
                    logger.info(f"[CHASE] Pre-Flight: TP order {tp_client_id} already exists on Exchange. Healing DB state.")
                    process.status = "COMPLETED"
                    process.sub_status = "DONE"
                    from datetime import datetime
                    process.finished_at = datetime.utcnow()
                    session.add(process)
                    session.commit()
                    return

            # Apply Precision
            qty_str = await exchange_manager.amount_to_precision(process.symbol, float(filled_qty))
            price_str = await exchange_manager.price_to_precision(process.symbol, float(tp_price))
            
            # --- 2. Inyección de Sello Idempotente ---
            # Place Limit TP (reduceOnly to prevent margin exhaustion)
            tp_order = await exchange_manager.create_order(
                symbol=process.symbol,
                side=tp_side,
                amount=qty_str,
                price=price_str,
                order_type="limit",
                params={"reduceOnly": True, "newClientOrderId": tp_client_id}
            )
            
            symbol = process.symbol
            
            # Log TP placement signal
            import json
            from app.db.database import BotSignal
            signal = BotSignal(
                symbol=symbol,
                rule_triggered="OTO_TP_PLACEMENT",
                action_taken="PLACE_LIMIT_TP",
                params_snapshot=json.dumps({
                    "entry_price": float(entry_price),
                    "tp_price": float(tp_price),
                    "qty": float(filled_qty),
                    "tp_order_id": str(tp_order.get('id', ''))
                }),
                success=True
            )
            session.add(signal)
            
            # Persist finished state for 60s instead of deleting immediately
            from datetime import datetime
            process.status = "COMPLETED"
            process.sub_status = "DONE"
            process.finished_at = datetime.utcnow()
            session.add(process)
            session.commit()
            
            # Tell engine we don't need ticker stream anymore
            from app.core.stream_service import stream_manager
            stream_manager.unsubscribe(symbol)
            
            # Reactor Bot B Hook
            from app.services.close_fill_reactor import close_fill_reactor
            # V5.9.44: Extract primitives BEFORE session closes to avoid DetachedInstanceError
            _closed_symbol = process.symbol
            _closed_at = process.created_at
            asyncio.create_task(close_fill_reactor.on_position_closed(
                symbol=_closed_symbol, created_at=_closed_at
            ))
            
            logger.info(f"[CHASE] Completed OTO loop for {symbol}. TP at {price_str}, order ID: {tp_order.get('id')}")

            
        except Exception as e:
            err_msg = str(e)
            
            # --- 3. Detección Pasiva (Exchange Firewall Auto-heal) ---
            if "-2012" in err_msg or "Duplicate clientOrderId" in err_msg:
                logger.info(f"[CHASE] Ignored duplicate TP placement for {process.symbol} (Idempotency Key Auto-heal).")
                process.status = "COMPLETED"
                process.sub_status = "DONE"
                from datetime import datetime
                process.finished_at = datetime.utcnow()
                session.add(process)
                session.commit()
                return
            
            tb = traceback.format_exc()
            logger.error(f"[CHASE FILL] Critical error placing TP for {process.symbol}: {err_msg}")
            
            # Log TP placement failure signal
            import json
            from app.db.database import BotSignal
            signal = BotSignal(
                symbol=process.symbol,
                rule_triggered="OTO_TP_PLACEMENT_FAILED",
                action_taken="ABORT_TP",
                params_snapshot=json.dumps({"error": err_msg}),
                success=False,
                error_message=err_msg
            )
            session.add(signal)
            
            # If it fails, we still want to mark the process as DONE or ERROR to stop the ticking loop
            process.status = "COMPLETED" # Or "ABORTED"
            process.sub_status = "TP_FAILED"
            from datetime import datetime
            process.finished_at = datetime.utcnow()
            session.add(process)
            session.commit()
            
            logger.warning(f"[CHASE] OTO Loop stopped due to TP failure on {process.symbol}. Manual TP recommended.")

    @staticmethod
    async def handle_abort(process, session):
        """Called if entry is explicitly canceled by user."""
        symbol = process.symbol
        logger.info(f"[CHASE] Entry aborted/canceled for {symbol}.")
        
        from datetime import datetime
        process.status = "ABORTED"
        process.sub_status = "ABORTED"
        process.finished_at = datetime.utcnow()
        session.add(process)
        session.commit()
        from app.core.stream_service import stream_manager
        stream_manager.unsubscribe(symbol)

class RepairChaseAction(BaseAction):
    """
    Action to repair an orphan sell by creating a synthetic buy.
    Params: order_id, profit_pc
    """
    async def execute(self, symbol: str, params: dict, context_params: dict) -> Dict[str, Any]:
        try:
            from app.services.repair_service import RepairService
            order_id = params.get("order_id")
            profit_pc = params.get("profit_pc", 0.5)
            
            if not order_id:
                return {"success": False, "error": "Missing order_id for repair"}
                
            result = await RepairService.execute_repair(order_id, profit_pc)
            return result
        except Exception as e:
            logger.error(f"[RepairAction] Error: {e}")
            return {"success": False, "error": str(e)}


# End of Action classes
