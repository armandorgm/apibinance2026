import asyncio
import traceback
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from app.core.logger import logger
from app.core.exchange import exchange_manager
from app.core.binance_native import binance_native
from app.db.database import get_session_direct, BotPipelineProcess, BotSignal
from .actions import BaseAction
from .chase_manager import ChaseDecisionEngine

class NativeOTOScalingAction(BaseAction):
    """
    Chase V2 (Official Native).
    Specialized for high reliability using 'binance-futures-connector'.
    Uses PUT /fapi/v1/order for tracking.
    """
    
    async def execute(self, symbol: str, params: dict, context_params: dict) -> Dict[str, Any]:
        """Initial Trigger when rule activates"""
        try:
            side = params.get("side", "buy")
            amount = params.get("amount", 5.0)
            profit_pc = params.get("profit_pc", 0.005) # Default 0.5%
            
            # 1. Fetch current price from real-time stream (registry)
            from app.core.stream_service import stream_manager
            await stream_manager.subscribe(symbol) # Ensure we are watching
            
            price = None
            for _ in range(15): # Wait up to 3 seconds (15 * 0.2s)
                ticker = exchange_manager.get_ticker(symbol)
                if ticker:
                    price = ticker.get('ask' if side == 'buy' else 'bid')
                    if price: break
                await asyncio.sleep(0.2)
            
            if not price:
                # Emergency fallback to fetch_ticker if stream is slow, 
                # but log it as it might lack bid/ask
                logger.warning(f"[CHASE V2] Stream price missing for {symbol}, falling back to REST")
                ticker = await exchange_manager.fetch_ticker(symbol)
                price = ticker.get('ask' if side == 'buy' else 'bid') or ticker.get('last')
            
            if not price:
                return {"success": False, "error": "Cannot fetch execution price (Stream + REST failed)"}

            # 2. Place Initial Post-Only order using Native Driver with Aggressive Chase (V5.9.32)
            market_id = await exchange_manager.get_market_id(symbol)
            entry_order = None
            
            for attempt in range(20):
                # Fetch latest price from registry for each attempt
                ticker = exchange_manager.get_ticker(symbol)
                if ticker:
                    price = ticker.get('ask' if side == 'buy' else 'bid')
                
                if not price:
                    logger.warning(f"[CHASE V2] Price missing in attempt {attempt+1}, skipping...")
                    await asyncio.sleep(0.2)
                    continue

                qty = amount / price
                price_str = await exchange_manager.price_to_precision(symbol, price)
                qty_str = await exchange_manager.amount_to_precision(symbol, qty)
                
                # Minimum Notional Hardening
                final_notional = float(qty_str) * float(price_str)
                if final_notional < 5.0:
                    qty_str = await exchange_manager.amount_to_precision(symbol, qty * 1.02)
                
                native_params = {
                    "timeInForce": "GTX", # Post-Only Mandatory
                    "newClientOrderId": f"V2_ENTRY_{int(datetime.utcnow().timestamp())}"
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
                    entry_order = res["result"]
                    logger.info(f"[CHASE V2] Entry placed successfully as Maker on attempt {attempt+1}")
                    break
                
                error = str(res.get("error", ""))
                if "-5022" in error:
                    logger.info(f"[CHASE V2] Post-Only rejection (Attempt {attempt+1}/20). Re-chasing {symbol} at new price {price}...")
                    await asyncio.sleep(0.2)
                    continue
                else:
                    return {"success": False, "error": f"Execution failed: {error}"}
            
            if not entry_order:
                return {"success": False, "error": "Failed to place Maker order after 20 attempts."}
            
            order_id = str(entry_order.get("orderId"))

            # 3. Create Pipeline Process for tracking
            with get_session_direct() as session:
                # Link to existing pipeline if provided in context
                pipeline_id = context_params.get("pipeline_id", 0)
                
                process = BotPipelineProcess(
                    pipeline_id=pipeline_id,
                    symbol=symbol,
                    entry_order_id=order_id,
                    side=side,
                    amount=float(qty_str), # Persist the ACTUAL precision-adjusted (and nudged) quantity
                    last_order_price=price,
                    status="CHASING",
                    sub_status="INIT_NATIVE",
                    originator="CHASE_V2",
                    custom_profit_pc=float(context_params.get("profit_pc") or params.get("profit_pc", 0.005))
                )
                session.add(process)
                session.commit()
                
                # Subscribe stream
                from app.core.stream_service import stream_manager
                await stream_manager.subscribe(symbol)
                
                logger.info(f"[CHASE V2] Started for {symbol} at {price} with orderId {order_id}")
                return {"success": True, "process_id": process.id, "order_id": order_id}

        except Exception as e:
            logger.error(f"[CHASE V2] Failed to start: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def handle_tick(process, current_price: float, session):
        """Called by StrategyEngine. Optimized Price tracking using PUT."""
        try:
            if not ChaseDecisionEngine.should_update(process, current_price):
                return

            market_id = await exchange_manager.get_market_id(process.symbol)
            
            # Formatear precisiones
            price_str = await exchange_manager.price_to_precision(process.symbol, current_price)
            qty_str = await exchange_manager.amount_to_precision(process.symbol, process.amount)
            
            res = await binance_native.modify_limit_order(
                symbol=market_id,
                side=process.side,
                quantity=qty_str,
                price=price_str,
                order_id=process.entry_order_id
            )
            
            if res.get("success"):
                process.last_tick_price = current_price
                process.last_order_price = current_price
                process.sub_status = "CHASING_NATIVE"
                session.commit()
            else:
                error = res.get('error', '')
                # If PUT fails because order is filled (-2012), trigger handle_fill immediately
                if "filled" in error.lower() or "-2012" in error:
                    logger.info(f"[CHASE V2] Order {process.entry_order_id} filled detected via PUT error. Triggering handle_fill.")
                    await NativeOTOScalingAction.handle_fill(process, session)
                else:
                    logger.warning(f"[CHASE V2] PUT failed: {error}. Skipping tick.")
                
        except Exception as e:
            logger.error(f"[CHASE V2] Tick Error: {e}")

    @staticmethod
    async def handle_fill(process, session, profit_pc: float = None, executed_qty: float = None):
        """Called when entry is filled. Places Native TP with reduceOnly. (V5.9.28)"""
        try:
            # V5.9.28: Contract Symmetry Sync
            # If we have the real executed qty from stream, use it and persist it.
            if executed_qty is not None and executed_qty > 0:
                logger.info(f"[CHASE V2] Syncing local amount {process.amount} -> real executed {executed_qty}")
                process.amount = executed_qty
                session.commit()

            # Use persisted profit_pc if available, fallback to provided or 0.5%
            final_profit_pc = profit_pc or process.custom_profit_pc or 0.005
            symbol = process.symbol
            side = "sell" if process.side == "buy" else "buy"
            entry_price = process.last_order_price or 0.0
            
            # Calculate TP price
            tp_price = entry_price * (1 + final_profit_pc) if process.side == "buy" else entry_price * (1 - final_profit_pc)
            
            logger.info(f"[CHASE V2] Entry filled at {entry_price}. Placing Native TP at {tp_price} ({final_profit_pc*100}%) for {process.amount} contracts")
            
            market_id = await exchange_manager.get_market_id(symbol)
            
            # Formatear precisiones
            price_str = await exchange_manager.price_to_precision(symbol, tp_price)
            qty_str = await exchange_manager.amount_to_precision(symbol, process.amount)
            
            # Use Native params with reduceOnly
            native_params = {
                "reduceOnly": "true",
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
                logger.info(f"[CHASE V2] TP placed successfully for {symbol}")
                
                from app.core.stream_service import stream_manager
                stream_manager.unsubscribe(symbol)
            else:
                error = res.get("error", "Unknown error")
                logger.error(f"[CHASE V2] TP placement failed: {error}")
                if "Duplicate" in error or "-2012" in error:
                    process.status = "COMPLETED"
                    session.commit()

        except Exception as e:
            logger.error(f"[CHASE V2] handle_fill Error: {e}")

    @staticmethod
    async def handle_order_event(process, order_data, session):
        """Unified stream event handler for V2. (V5.9.28)"""
        status = order_data.get('status', '').lower()
        if status == 'filled':
            # V5.9.28: Extract real executed quantity from 'z' (Cumulative filled qty)
            executed_qty = float(order_data.get('z', process.amount))
            logger.info(f"[CHASE V2] Order {process.entry_order_id} FILLED. Real executed qty: {executed_qty}")
            await NativeOTOScalingAction.handle_fill(process, session, executed_qty=executed_qty)
        elif status in ['canceled', 'expired']:
            logger.warning(f"[CHASE V2] Order {process.entry_order_id} was {status} externally. Aborting.")
            process.status = "ABORTED"
            process.sub_status = f"EXTERNAL_{status.upper()}"
            session.commit()
