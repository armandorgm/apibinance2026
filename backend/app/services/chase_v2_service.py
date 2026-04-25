import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.logger import logger
from app.core.exchange import exchange_manager
from app.core.binance_native import binance_native
from app.db.database import get_session_direct, BotPipelineProcess
from app.core.stream_service import stream_manager

class ChaseV2Service:
    """
    Autonomous Backend-Only Service for Chase V2.
    Handles 'Set & Forget' Post-Only execution without relying on browser UI.
    """
    
    COOLDOWN_SECONDS = 5
    PRICE_DIFF_THRESHOLD = 0.0005 # 0.05%

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChaseV2Service, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def should_update(process: BotPipelineProcess, current_price: float) -> bool:
        """
        Evaluates if the opening order should be replaced based on time and price.
        """
        if process.sub_status == "RECOVERING" or process.entry_order_id == "INITIAL_REJECTED":
            return True

        last_update = process.updated_at or process.created_at
        elapsed = (datetime.utcnow() - last_update).total_seconds()
        
        if elapsed < ChaseV2Service.COOLDOWN_SECONDS:
            return False
            
        if not process.last_tick_price:
            return True 
            
        price_diff_percent = abs(current_price - process.last_tick_price) / process.last_tick_price
        
        if price_diff_percent < ChaseV2Service.PRICE_DIFF_THRESHOLD:
            return False
            
        return True

    async def init_chase(self, symbol: str, side: str, amount: float, profit_pc: float = 0.005, pipeline_id: int = 0, originator: str = "MANUAL") -> Dict[str, Any]:
        try:
            # V5.9.38: Proactive normalization to ensure registry match (DIAS Robustness)
            symbol = await exchange_manager.normalize_symbol(symbol)
            
            print(f"[DEBUG] Subscribing to {symbol}...")
            await stream_manager.subscribe(symbol)
            
            price = None
            for _ in range(15):
                ticker = exchange_manager.get_ticker(symbol)
                if ticker:
                    price = ticker.get('ask' if side == 'buy' else 'bid')
                    if price: break
                await asyncio.sleep(0.2)
            
            if not price:
                logger.warning(f"[CHASE V2 SERVICE] Stream price missing for {symbol}, falling back to REST")
                print(f"[DEBUG] Falling back to REST fetch_ticker...")
                ticker = await exchange_manager.fetch_ticker(symbol)
                price = ticker.get('ask' if side == 'buy' else 'bid') or ticker.get('last')
            
            if not price:
                return {"success": False, "error": "Cannot fetch execution price"}

            print(f"[DEBUG] Getting market ID...")
            market_id = await exchange_manager.get_market_id(symbol)
            entry_order = None
            
            # Fetch tick_size once — needed for maker-safe price adjustment
            tick_size = await exchange_manager.get_tick_size(symbol)

            for attempt in range(20):
                # Always fetch the freshest book price on each attempt
                ticker = exchange_manager.get_ticker(symbol)
                if ticker:
                    bid = ticker.get("bid")
                    ask = ticker.get("ask")
                    if side == "buy" and bid:
                        # Place 1 tick above bid to be first in maker queue
                        raw_price = bid + tick_size
                        if raw_price >= ask:
                            raw_price = bid   # fallback: sit at bid to avoid crossing
                        price = raw_price
                    elif side == "sell" and ask:
                        # Place 1 tick below ask to be first in maker queue
                        raw_price = ask - tick_size
                        if raw_price <= bid:
                            raw_price = ask   # fallback: sit at ask
                        price = raw_price

                if not price:
                    await asyncio.sleep(0.3)
                    continue

                qty = amount / price
                price_str = await exchange_manager.price_to_precision(symbol, price)

                min_safe_qty = await exchange_manager.get_safe_min_notional_qty(symbol, price)
                final_qty = max(qty, min_safe_qty)
                logger.info(f"[CHASE V2] Qty Debug: amount={amount}, price={price}, qty={qty}, min_safe={min_safe_qty}, final={final_qty}")
                qty_str = await exchange_manager.amount_to_precision(symbol, final_qty)

                native_params = {
                    "recvWindow": 10000,
                    "timeInForce": "GTX",
                    "newClientOrderId": f"V2_ENTRY_{int(datetime.utcnow().timestamp())}"
                }

                print(f"[DEBUG] Calling binance_native.create_order for {market_id}...")
                res = await binance_native.create_order(
                    symbol=market_id,
                    side=side,
                    order_type="LIMIT",
                    quantity=qty_str,
                    price=price_str,
                    params=native_params
                )

                if res.get("success"):
                    entry_order = res["result"]
                    logger.info(f"[CHASE V2 SERVICE] Entry placed as Maker on attempt {attempt+1} at {price_str}")
                    break

                error = str(res.get("error", ""))
                if "-5022" in error:
                    # Exponential backoff capped at 2s — gives the book time to shift
                    backoff = min(0.2 * (1.5 ** attempt), 2.0)
                    logger.info(
                        f"[CHASE V2 SERVICE] Post-Only rejection #{attempt+1}. "
                        f"Retrying in {backoff:.2f}s with fresh price..."
                    )
                    await asyncio.sleep(backoff)
                    continue
                else:
                    return {"success": False, "error": f"Execution failed: {error}"}
            
            if not entry_order:
                return {"success": False, "error": "Failed to place Maker order after 20 attempts."}
            
            order_id = str(entry_order.get("orderId"))

            with get_session_direct() as session:
                process = BotPipelineProcess(
                    pipeline_id=pipeline_id,
                    symbol=symbol,
                    entry_order_id=order_id,
                    side=side,
                    amount=float(qty_str),
                    last_order_price=price,
                    status="CHASING",
                    sub_status="INIT_NATIVE",
                    handler_type="CHASE_V2",
                    originator=originator,
                    custom_profit_pc=profit_pc
                )
                session.add(process)
                session.commit()
                
                # Register in bot engine registry (V5.9.35)
                from app.services.bot_service import bot_instance
                bot_instance.engine.register_chase(symbol)
                
                logger.info(f"[CHASE V2 SERVICE] Started for {symbol} at {price} with orderId {order_id}")
                return {"success": True, "process_id": process.id, "order_id": order_id}

        except Exception as e:
            logger.error(f"[CHASE V2 SERVICE] Failed to start: {e}")
            return {"success": False, "error": str(e)}

    async def handle_tick(self, process: BotPipelineProcess, current_price: float, session):
        try:
            # Ensure symbol is normalized for ticker registry lookup
            symbol = await exchange_manager.normalize_symbol(process.symbol)
            
            if not self.should_update(process, current_price):
                return

            market_id = await exchange_manager.get_market_id(symbol)
            
            ticker = exchange_manager.get_ticker(symbol)
            if not ticker:
                return
                
            bid = ticker.get("bid", current_price)
            ask = ticker.get("ask", current_price)
            tick_size = await exchange_manager.get_tick_size(symbol)
            
            side = (process.side or "buy").lower()
            if side == "buy":
                target_price = bid + tick_size
                if target_price >= ask:
                    target_price = bid
            else:
                target_price = ask - tick_size
                if target_price <= bid:
                    target_price = ask
                    
            price_str = await exchange_manager.price_to_precision(process.symbol, target_price)
            qty_str = await exchange_manager.amount_to_precision(process.symbol, process.amount)
            
            # Handle RECOVERING state by creating a new order
            if process.sub_status == "RECOVERING" or process.entry_order_id == "INITIAL_REJECTED":
                native_params = {
                    "timeInForce": "GTX",
                    "newClientOrderId": f"V2_ENTRY_{int(datetime.utcnow().timestamp())}"
                }
                res = await binance_native.create_order(
                    symbol=market_id,
                    side=process.side,
                    order_type="LIMIT",
                    quantity=qty_str,
                    price=price_str,
                    params=native_params
                )
            else:
                res = await binance_native.modify_limit_order(
                    symbol=market_id,
                    side=process.side,
                    quantity=qty_str,
                    price=price_str,
                    order_id=process.entry_order_id
                )
            
            if res.get("success"):
                process.last_tick_price = target_price
                process.last_order_price = target_price
                process.sub_status = "CHASING_NATIVE"
                
                # Update entry_order_id if we created a new one during recovery
                if process.entry_order_id == "INITIAL_REJECTED" or process.sub_status == "RECOVERING":
                   if "result" in res and "orderId" in res["result"]:
                       process.entry_order_id = str(res["result"]["orderId"])

                session.commit()
            else:
                error = str(res.get('error', '')).lower()
                # 1. Detectar si la orden ya se llenó o ya no existe (asumimos fill)
                if "filled" in error or "-2012" in error or "-2013" in error:
                    logger.info(f"[CHASE V2] Order {process.entry_order_id} filled or not found (-2013) during PUT. Triggering handle_fill.")
                    await self.handle_fill(process, session)
                elif "post-only" in error or "-5022" in error:
                    logger.warning(f"[CHASE V2 SERVICE] Post-Only constraint failed (-5022). Forcing RECOVERING state.")
                    process.sub_status = "RECOVERING"
                    process.entry_order_id = "INITIAL_REJECTED" 
                    session.commit()
                
        except Exception as e:
            logger.error(f"[CHASE V2 SERVICE] Tick Error: {e}")

    async def handle_fill(self, process: BotPipelineProcess, session, executed_qty: float = None):
        try:
            if executed_qty is not None and executed_qty > 0:
                process.amount = executed_qty
                session.commit()

            final_profit_pc = process.custom_profit_pc or 0.005
            symbol = process.symbol
            side = "sell" if process.side == "buy" else "buy"
            entry_price = process.last_order_price or 0.0
            
            tp_price = entry_price * (1 + final_profit_pc) if process.side == "buy" else entry_price * (1 - final_profit_pc)
            
            logger.info(f"[CHASE V2 SERVICE] Entry filled at {entry_price}. Placing Native TP at {tp_price} ({final_profit_pc*100}%) for {process.amount} contracts")
            
            market_id = await exchange_manager.get_market_id(symbol)
            price_str = await exchange_manager.price_to_precision(symbol, tp_price)
            qty_str = await exchange_manager.amount_to_precision(symbol, process.amount)
            
            native_params = {
                "reduceOnly": True,
                "timeInForce": "GTC",
                "newClientOrderId": f"V2_TP_{int(datetime.utcnow().timestamp())}"
            }
            
            res = await binance_native.create_order(
                symbol=market_id,
                side=side,
                order_type="LIMIT",
                quantity=qty_str,
                price=price_str,
                params=native_params
            )
            
            if res.get("success"):
                process.status = "COMPLETED"
                process.sub_status = "DONE_NATIVE"
                process.finished_at = datetime.utcnow()
                session.commit()
                logger.info(f"[CHASE V2 SERVICE] TP placed successfully for {symbol}")
                
                from app.services.bot_service import bot_instance
                bot_instance.engine.unregister_chase(symbol)
                stream_manager.unsubscribe(symbol)

                # ── Bot B hook: emit to CloseFillReactor (non-blocking) ──
                from app.services.close_fill_reactor import close_fill_reactor
                asyncio.create_task(close_fill_reactor.on_position_closed(process))
            else:
                error = res.get("error", "Unknown error")
                logger.error(f"[CHASE V2 SERVICE] TP placement failed: {error}")
                if "Duplicate" in error or "-2012" in error:
                    process.status = "COMPLETED"
                    session.commit()

        except Exception as e:
            logger.error(f"[CHASE V2 SERVICE] handle_fill Error: {e}")

    async def handle_order_event(self, process: BotPipelineProcess, order_data: dict, session):
        status = order_data.get('status', '').lower()
        if status == 'filled':
            executed_qty = float(order_data.get('z', process.amount))
            logger.info(f"[CHASE V2 SERVICE] Order {process.entry_order_id} FILLED. Real executed qty: {executed_qty}")
            await self.handle_fill(process, session, executed_qty=executed_qty)
        elif status in ['canceled', 'expired']:
            logger.warning(f"[CHASE V2 SERVICE] Order {process.entry_order_id} was {status} externally. Aborting.")
            process.sub_status = f"EXTERNAL_{status.upper()}"
            session.commit()
            
            from app.services.bot_service import bot_instance
            bot_instance.engine.unregister_chase(process.symbol)
            stream_manager.unsubscribe(process.symbol)

    async def stop_chase(self, process_id: int) -> bool:
        with get_session_direct() as session:
            process = session.query(BotPipelineProcess).filter_by(id=process_id).first()
            if not process:
                return False
                
            if process.status == "CHASING":
                process.status = "ABORTED"
                process.sub_status = "MANUAL_STOP"
                
                if process.entry_order_id and process.entry_order_id != "INITIAL_REJECTED":
                    try:
                        market_id = await exchange_manager.get_market_id(process.symbol)
                        await binance_native.cancel_order(symbol=market_id, order_id=process.entry_order_id)
                    except Exception as e:
                        logger.error(f"[CHASE V2 SERVICE] Failed to cancel order: {e}")
                
                session.commit()
                from app.services.bot_service import bot_instance
                bot_instance.engine.unregister_chase(process.symbol)
                stream_manager.unsubscribe(process.symbol)
                return True
            return False

chase_v2_service = ChaseV2Service()
