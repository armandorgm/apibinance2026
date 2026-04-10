from typing import Dict, Any, Optional
from sqlmodel import Session, select
from app.db.database import engine, Fill, Trade, Originator, get_session_direct, BotSignal
from app.core.exchange import exchange_manager
from app.core.logger import logger
from datetime import datetime
import json

class RepairService:
    @staticmethod
    def get_repair_preview(order_id: str, profit_pc: float) -> Dict[str, Any]:
        """
        Calculates the real buy order details for closing an orphan sell.
        """
        with Session(engine) as session:
            # Find the unmatched sell (orphan)
            stmt = select(Fill).where(Fill.order_id == order_id, Fill.side == 'sell')
            sell_fills = session.exec(stmt).all()
            
            if not sell_fills:
                # Try with prefix removal
                raw_id = order_id[1:] if order_id[0] in ['B', 'C'] else order_id
                stmt = select(Fill).where(Fill.order_id == raw_id, Fill.side == 'sell')
                sell_fills = session.exec(stmt).all()
                
            if not sell_fills:
                raise ValueError(f"No sell execution found for Order ID {order_id}")
            
            total_amount = sum(f.amount for f in sell_fills)
            avg_price = sum(f.price * f.amount for f in sell_fills) / total_amount
            symbol = sell_fills[0].symbol
            
            # Calculation: BuyPrice = SellPrice / (1 + profit_pc/100)
            target_buy_price = avg_price / (1 + (profit_pc / 100))
            
            # Notional check (Binance $5 minimum rule)
            notional = total_amount * target_buy_price
            needs_scaling = notional < 5.0
            
            scaling_factor = 1.0
            adjusted_amount = total_amount
            
            if needs_scaling:
                # Calculate required amount to reach $5.05
                adjusted_amount = 5.05 / target_buy_price
                scaling_factor = adjusted_amount / total_amount
            
            return {
                "symbol": symbol,
                "order_id": order_id,
                "side": "sell",
                "original_price": avg_price,
                "amount": total_amount,
                "adjusted_amount": adjusted_amount,
                "needs_scaling": needs_scaling,
                "target_buy_price": target_buy_price,
                "profit_percentage": profit_pc,
                "timestamp": sell_fills[0].timestamp,
                "datetime": sell_fills[0].datetime,
                "notional": notional
            }

    @staticmethod
    async def execute_repair(order_id: str, profit_pc: float) -> Dict[str, Any]:
        """
        Executes the repair by placing a REAL STANDARD LIMIT ORDER on Binance.
        Implements auto-scaling if notional < $5.
        """
        preview = RepairService.get_repair_preview(order_id, profit_pc)
        symbol = preview['symbol']
        
        # 1. Place the REAL Order on Binance
        try:
            # Ensure exchange is initialized
            await exchange_manager.get_exchange()
            
            # Use adjusted_amount if scaling was needed
            final_amount = preview['adjusted_amount']
            
            # Formate price and amount for the exchange
            price_str = await exchange_manager.price_to_precision(symbol, preview['target_buy_price'])
            amount_str = await exchange_manager.amount_to_precision(symbol, final_amount)
            
            logger.info(f"[RepairService] Placing REAL BUY LIMIT order for {symbol} at {price_str} (Amount: {amount_str})")
            
            # Standard Limit Order (No Post-Only, No Reduce-Only as requested by user)
            order = await exchange_manager.create_order(
                symbol=symbol,
                order_type="limit",
                side="buy",
                amount=amount_str,
                price=price_str,
                params={} # Empty = Standard Limit
            )
            
            # 2. Log the execution as a Bot Signal
            with Session(engine) as session:
                signal = BotSignal(
                    symbol=symbol,
                    rule_triggered="MANUAL_REPAIR_ORDER",
                    action_taken="PLACE_LIMIT_BUY",
                    params_snapshot=json.dumps({
                        "orphan_order_id": order_id,
                        "target_price": price_str,
                        "amount": amount_str,
                        "profit_pc": profit_pc,
                        "scaled": preview['needs_scaling']
                    }),
                    exchange_response=json.dumps(order),
                    success=True
                )
                session.add(signal)
                session.commit()
            
            return {
                "success": True,
                "message": f"Real LIMIT BUY order placed on Binance: {order.get('id')}",
                "order_id": order.get('id'),
                "price": price_str,
                "amount": amount_str,
                "scaled": preview['needs_scaling']
            }
            
        except Exception as e:
            logger.error(f"[RepairService] Order Execution Failed: {e}")
            raise e
