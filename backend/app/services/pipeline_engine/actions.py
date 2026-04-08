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

                logger.debug(f"[AdaptiveOTO] Precision strings: qty_str={qty_str}, price_str={price_str}")

                # 1. Create initial Limit Post-Only order 
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
                    logger.error(f"[AdaptiveOTO] Initial order failed: {order_error}")
                    raise order_error
                
                try:
                    # 2. Start tracking ONLY if order succeeded
                    process = BotPipelineProcess(
                        pipeline_id=pipeline_id or 0,
                        symbol=symbol,
                        entry_order_id=str(entry_order['id']),
                        side=side,
                        amount=float(qty_str),
                        last_tick_price=current_price,
                        last_order_price=float(price_str),
                        status="CHASING"
                    )
                    session.add(process)
                    session.commit()
                    session.refresh(process)
                    process_id = process.id
                except Exception as db_error:
                    # CRITICAL: If DB fails, we must cancel the order on Binance to avoid "Orphans"
                    logger.error(f"[AdaptiveOTO] DB Commit failed. CANCELLING orphan order {entry_order.get('id')}")
                    try:
                        exchange_ccxt = await exchange_manager.get_exchange()
                        await exchange_ccxt.cancel_order(entry_order['id'], symbol)
                    except Exception as cancel_err:
                        logger.error(f"[AdaptiveOTO] Failed to cancel orphan order! {cancel_err}")
                    raise db_error
                
                # 3. Subscribe ONLY after everything else succeeded
                from app.core.stream_service import stream_manager
                stream_manager.subscribe(symbol)
                
            return {"success": True, "action": "ADAPTIVE_OTO", "process_id": process_id}
        except Exception as e:
            # Capture full traceback and log it
            tb = traceback.format_exc()
            logger.error(f"[AdaptiveOTO] Exception: {tb}")
            return {"success": False, "error": tb}

    @staticmethod
    async def handle_tick(process, current_price: float, session):
        """Called every millisecond by WS Stream. Fast chase execution."""
        from .chase_manager import ChaseDecisionEngine
        from datetime import datetime
        
        # 1. SOLID Principle: Delegate decision to the engine
        if not ChaseDecisionEngine.should_update(process, current_price):
            return

        logger.info(f"[CHASE] Throttling passed. Updating order for {process.symbol} at {current_price}")
        
        try:
            # 2. Use cached qty/side instead of fetching from exchange (low latency)
            side = process.side or "buy"
            qty = process.amount
            
            if qty > 0:
                # Cancel old
                exchange_ccxt = await exchange_manager.get_exchange()
                try:
                    await exchange_ccxt.cancel_order(process.entry_order_id, process.symbol)
                except Exception as cancel_err:
                    err_str = str(cancel_err).lower()
                    logger.warning(f"[CHASE] Could not cancel old order {process.entry_order_id}: {cancel_err}")
                    
                    # If order is already gone (filled or canceled), stop chasing
                    if "not found" in err_str or "order_state_invalid" in err_str or "no such order" in err_str:
                        logger.info(f"[CHASE] Order {process.entry_order_id} is no longer active on exchange. Fetching final status.")
                        try:
                            order = await exchange_manager.fetch_order_raw(process.symbol, process.entry_order_id)
                            if order.get('status') == 'closed':
                                await self.handle_fill(process, session)
                            else:
                                await self.handle_abort(process, session)
                            return # Stop processing this tick
                        except Exception as fetch_err:
                            logger.error(f"[CHASE] Failed to fetch final status: {fetch_err}. Force aborting.")
                            await self.handle_abort(process, session)
                            return
                
                # Apply Precision
                qty_str = await exchange_manager.amount_to_precision(process.symbol, float(qty))
                price_str = await exchange_manager.price_to_precision(process.symbol, float(current_price))
                
                # Place new
                new_order = await exchange_manager.create_order(
                    symbol=process.symbol,
                    side=side,
                    amount=qty_str,
                    price=price_str,
                    order_type="limit",
                    params={"timeInForce": "GTX"}
                )
                
                # 3. Update DB state
                process.entry_order_id = str(new_order['id'])
                process.last_tick_price = current_price
                process.last_order_price = float(price_str)
                process.updated_at = datetime.utcnow() # Force updated_at for next cooldown check
                session.commit()
                logger.info(f"[CHASE] Order replaced: {new_order['id']} at {price_str}")
                
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"[CHASE] Exception: {tb}")
            print(f"[CHASE ERROR] {e}")

    @staticmethod
    async def handle_fill(process, session):
        """Called when entry order is fully closed/filled."""
        print(f"[CHASE] Entry FILLED for {process.symbol}. Placing TP.")
        try:
            order = await exchange_manager.fetch_order_raw(process.symbol, process.entry_order_id)
            if not order: return
            filled_qty = order['filled']
            entry_price = order['average'] or order['price']
            tp_side = "sell" if order['side'] == "buy" else "buy"
            
            # Default TP is 1% away for fallback
            tp_price = entry_price * 1.01 if tp_side == "sell" else entry_price * 0.99
            
            # Apply Precision
            qty_str = await exchange_manager.amount_to_precision(process.symbol, float(filled_qty))
            price_str = await exchange_manager.price_to_precision(process.symbol, float(tp_price))
            
            # Place Limit TP
            await exchange_manager.create_order(
                symbol=process.symbol,
                side=tp_side,
                amount=qty_str,
                price=price_str,
                order_type="limit"
            )
            
            symbol = process.symbol
            
            # SUCCESS! Self-clean DB state.
            session.delete(process)
            session.commit()
            
            # Tell engine we don't need ticker stream anymore
            from app.core.stream_service import stream_manager
            stream_manager.unsubscribe(symbol)
            print(f"[CHASE] Completed OTO loop for {symbol}.")
            
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"[CHASE FILL] Exception: {tb}")
            print(f"[CHASE FILL ERROR] {e}")
    @staticmethod
    async def handle_abort(process, session):
        """Called if entry is explicitly canceled by user."""
        symbol = process.symbol
        print(f"[CHASE] Entry aborted/canceled for {symbol}.")
        session.delete(process)
        session.commit()
        from app.core.stream_service import stream_manager
        stream_manager.unsubscribe(symbol)


# Registry for easy parsing
ACTIONS = {
    "BUY_MIN_NOTIONAL": BuyMinNotionalAction(),
    "ADAPTIVE_OTO": AdaptiveOTOScalingAction()
}
