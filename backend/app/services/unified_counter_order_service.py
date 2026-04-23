from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from app.db.database import engine, BotSignal, Trade
from app.core.exchange import exchange_manager
from app.core.logger import logger
import json

class UnifiedCounterOrderService:
    """
    Unified Counter-Order Engine (UCOE) - Standard Edition V5.8
    Strategic service implementing 'True Units' with robust Algo detection.
    """

    @staticmethod
    async def get_candidates(symbol: str, filter_mode: str = '7d', orphans_only: bool = False) -> List[Dict[str, Any]]:
        since = None
        positions = await exchange_manager.get_open_positions(symbol)
        net_pos = 0.0
        
        if positions:
            pos = positions[0]
            net_pos = float(pos.get('info', {}).get('pa', pos.get('contracts', 0)))
            if filter_mode == 'position_cycle':
                cycle_start = await exchange_manager.get_position_cycle_start(symbol)
                if cycle_start:
                    since = cycle_start
                    logger.info(f"[UCOE] Cycle detection: Since {since}")

        raw_orders = await exchange_manager.fetch_orders_by_symbol(symbol, since=since)
        
        consumed_order_ids = set()
        if orphans_only:
            with Session(engine) as session:
                stmt = select(Trade.entry_order_id, Trade.exit_order_id).where(Trade.symbol == symbol)
                rows = session.exec(stmt).all()
                for e_id, x_id in rows:
                    if e_id: consumed_order_ids.add(str(e_id))
                    if x_id: consumed_order_ids.add(str(x_id))

        candidates = []
        for o in raw_orders:
            if o.get('status') != 'closed' and o.get('filled', 0) <= 0:
                continue
            oid = str(o.get('id'))
            if orphans_only and oid in consumed_order_ids:
                continue
            side = o.get('side', '').lower()
            is_compatible = (net_pos > 0 and side == 'buy') or (net_pos < 0 and side == 'sell') or (net_pos == 0)
            o['is_compatible_with_reduce_only'] = is_compatible
            o['is_orphan'] = oid not in consumed_order_ids
            candidates.append(o)

        candidates.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return candidates

    @staticmethod
    async def get_detailed_open_balance(symbol: str) -> Dict[str, Any]:
        """
        Calculates the net quantity of open orders, split by Algo and Basic types.
        Uses raw exchange contracts (no factor applied).
        """
        from app.domain.orders.order_factory import OrderFactory
        from app.db.database import OrderSource

        open_orders = await exchange_manager.fetch_open_orders(symbol)
        algo_qty = 0.0
        basic_qty = 0.0
        algo_breakdown = {"tp": 0.0, "sl": 0.0, "trailing": 0.0}
        
        for o in open_orders:
            # V5.9: Use SOLID Factory for consistent classification
            domain_order = OrderFactory.create(o, set())
            is_algo = domain_order.source == OrderSource.ALGO
            
            qty = domain_order.amount
            side = domain_order.side.lower()
            signed_qty = qty if side == 'buy' else -qty

            if is_algo:
                kind = getattr(domain_order, 'conditional_kind', None)
                if kind == 'take_profit': algo_breakdown['tp'] += signed_qty
                elif kind == 'stop_loss': algo_breakdown['sl'] += signed_qty
                elif kind == 'trailing': algo_breakdown['trailing'] += signed_qty
            
            # Exclusion Logic: Skip Stop Loss (Emergency tools) from main sum
            order_type = getattr(domain_order, 'order_type', '').upper()
            if "STOP" in order_type and "TRAILING" not in order_type and "TAKE_PROFIT" not in order_type:
                continue
            
            if is_algo: algo_qty += signed_qty
            else: basic_qty += signed_qty
            
        return {
            "algo_units": round(algo_qty, 8),
            "basic_units": round(basic_qty, 8),
            "algo_breakdown": {k: round(v, 8) for k, v in algo_breakdown.items()},
            "algo_contracts": round(algo_qty, 8),
            "basic_contracts": round(basic_qty, 8),
            "factor": 1.0
        }

    @staticmethod
    def calculate_target_price(ref_side: str, ref_price: float, profit_pc: float) -> float:
        profit_pc = max(0.01, min(100.0, profit_pc))
        if ref_side == "buy": return ref_price * (1 + (profit_pc / 100))
        else: return ref_price / (1 + (profit_pc / 100))

    @staticmethod
    def determine_reduce_only(current_net_pos: float, ref_order_side: str) -> bool:
        if current_net_pos > 0 and ref_order_side == "buy": return True
        if current_net_pos < 0 and ref_order_side == "sell": return True
        return False

    @staticmethod
    def scale_to_min_notional(amount: float, price: float, is_reduce_only: bool = False) -> (float, bool):
        if is_reduce_only: return amount, False
        notional = amount * price
        if notional < 5.08: return 5.2 / price, True
        return amount, False

    @staticmethod
    async def get_bulk_preview(symbol: str, order_ids: List[str], profit_pc: float) -> Dict[str, Any]:
        total_qty = 0.0
        weighted_cost = 0.0
        ref_side = None

        for oid in order_ids:
            order = await exchange_manager.fetch_order_raw(symbol, oid)
            if not order: continue
            side = order.get('side', '').lower()
            if ref_side and side != ref_side:
                raise ValueError("No se pueden mezclar órdenes de compra y venta en un bloque Bulk.")
            ref_side = side
            qty = float(order.get('filled') or order.get('amount') or 0)
            price = float(order.get('price') or order.get('average') or 0)
            total_qty += qty
            weighted_cost += (qty * price)

        if total_qty <= 0: raise ValueError("No se encontraron cantidades válidas.")
        avg_price = weighted_cost / total_qty
        
        positions = await exchange_manager.get_open_positions(symbol)
        net_pos = 0.0
        pos_notional = 0.0
        pos_context = {"current_side": "none", "net_pos": 0.0}
        
        if positions:
            p = positions[0]
            net_pos = float(p.get('info', {}).get('pa', p.get('contracts', 0)))
            pos_notional = abs(float(p.get('notional', 0) or p.get('info', {}).get('notional', 0)))
            pos_context = {
                "current_side": 'long' if net_pos > 0 else 'short', 
                "net_pos": net_pos,
                "notional": pos_notional
            }

        open_detailed = await UnifiedCounterOrderService.get_detailed_open_balance(symbol)
        target_side = "sell" if ref_side == "buy" else "buy"
        reduce_only = UnifiedCounterOrderService.determine_reduce_only(net_pos, ref_side)
        target_price = UnifiedCounterOrderService.calculate_target_price(ref_side, avg_price, profit_pc)
        adjusted_amount, needs_scaling = UnifiedCounterOrderService.scale_to_min_notional(total_qty, target_price, reduce_only)

        pos_units = net_pos
        action_units = (adjusted_amount if target_side == "buy" else -adjusted_amount)
        total_sum_units = pos_units + open_detailed['algo_units'] + open_detailed['basic_units'] + action_units
        projected_final = total_sum_units

        return {
            "symbol": symbol, "reference_ids": order_ids, "reference_side": ref_side, "reference_price_avg": avg_price,
            "target_side": target_side, "target_price": target_price, "original_total_amount": total_qty, "adjusted_total_amount": adjusted_amount,
            "needs_scaling": needs_scaling, "reduce_only": reduce_only, "profit_percentage": profit_pc, "position_context": pos_context,
            "algo_units": open_detailed['algo_units'],
            "basic_units": open_detailed['basic_units'],
            "pos_units": round(pos_units, 8),
            "action_units": round(action_units, 8),
            "projected_net_pos": round(projected_final, 8),
            "projected_net_units": round(projected_final, 8),
            "missing_amount_to_zero": round(abs(pos_units + open_detailed['algo_units'] + open_detailed['basic_units']), 8),
            "algo_notional_est": round(abs(open_detailed['algo_contracts'] * avg_price), 4) if avg_price else 0,
            "basic_notional_est": round(abs(open_detailed['basic_contracts'] * avg_price), 4) if avg_price else 0,
            "action_notional_est": round(abs(adjusted_amount * target_price), 4) if target_price else 0
        }

    @staticmethod
    async def get_counter_order_preview(symbol: str, order_id: str, profit_pc: float) -> Dict[str, Any]:
        ref_order = await exchange_manager.fetch_order_raw(symbol, order_id)
        if not ref_order: raise ValueError(f"Order {order_id} not found.")

        ref_price = float(ref_order.get('price') or ref_order.get('average') or 0)
        ref_amount = float(ref_order.get('filled') or ref_order.get('amount') or 0)
        ref_side = ref_order.get('side', '').lower()

        positions = await exchange_manager.get_open_positions(symbol)
        net_pos = 0.0
        pos_context = {"current_side": "none", "net_pos": 0.0}
        
        if positions:
            p = positions[0]
            net_pos = float(p.get('info', {}).get('pa', p.get('contracts', 0)))
            pos_notional = abs(float(p.get('notional', 0) or p.get('info', {}).get('notional', 0)))
            pos_context = {
                "current_side": 'long' if net_pos > 0 else 'short', 
                "net_pos": net_pos,
                "notional": pos_notional
            }

        open_detailed = await UnifiedCounterOrderService.get_detailed_open_balance(symbol)
        target_side = "sell" if ref_side == "buy" else "buy"
        reduce_only = UnifiedCounterOrderService.determine_reduce_only(net_pos, ref_side)
        target_price = UnifiedCounterOrderService.calculate_target_price(ref_side, ref_price, profit_pc)
        adjusted_amount, needs_scaling = UnifiedCounterOrderService.scale_to_min_notional(ref_amount, target_price, reduce_only)
            
        pos_units = net_pos
        action_units = (adjusted_amount if target_side == "buy" else -adjusted_amount)
        total_sum_units = pos_units + open_detailed['algo_units'] + open_detailed['basic_units'] + action_units
        projected_final = total_sum_units

        return {
            "symbol": symbol, "reference_order_id": order_id, "reference_side": ref_side, "reference_price": ref_price,
            "target_side": target_side, "target_price": target_price, "original_amount": ref_amount, "adjusted_amount": adjusted_amount,
            "needs_scaling": needs_scaling, "reduce_only": reduce_only, "profit_percentage": profit_pc, "position_context": pos_context,
            "algo_units": open_detailed['algo_units'],
            "basic_units": open_detailed['basic_units'],
            "pos_units": round(pos_units, 8),
            "action_units": round(action_units, 8),
            "projected_net_pos": round(projected_final, 8),
            "projected_net_units": round(projected_final, 8),
            "missing_amount_to_zero": round(abs(pos_units + open_detailed['algo_units'] + open_detailed['basic_units']), 8),
            "algo_notional_est": round(abs(open_detailed['algo_contracts'] * ref_price), 4) if ref_price else 0,
            "basic_notional_est": round(abs(open_detailed['basic_contracts'] * ref_price), 4) if ref_price else 0,
            "action_notional_est": round(abs(adjusted_amount * target_price), 4) if target_price else 0
        }

    @staticmethod
    async def execute_counter_order(symbol: str, order_id: str, profit_pc: float, is_bulk: bool = False, order_ids: List[str] = None, override_amount: float = None) -> Dict[str, Any]:
        if is_bulk and order_ids:
            preview = await UnifiedCounterOrderService.get_bulk_preview(symbol, order_ids, profit_pc)
        else:
            preview = await UnifiedCounterOrderService.get_counter_order_preview(symbol, order_id, profit_pc)
            order_ids = [order_id]
        
        try:
            await exchange_manager.get_exchange()
            price_str = await exchange_manager.price_to_precision(symbol, preview['target_price'])
            raw_target_amount = override_amount if override_amount is not None else (preview.get('adjusted_total_amount') or preview.get('adjusted_amount'))
            amount_str = await exchange_manager.amount_to_precision(symbol, raw_target_amount)
            
            params = {}
            if preview['reduce_only'] or (override_amount is not None):
                params['reduceOnly'] = True
                
            order = await exchange_manager.create_order(symbol=symbol, order_type="limit", side=preview['target_side'], amount=amount_str, price=price_str, params=params)
            
            with Session(engine) as session:
                signal = BotSignal(
                    symbol=symbol, rule_triggered="UCOE_V5.8",
                    action_taken=f"PLACE_LIMIT_{preview['target_side'].upper()}",
                    params_snapshot=json.dumps({"reference_ids": order_ids, "profit_pc": profit_pc}),
                    exchange_response=json.dumps(order), success=True
                )
                session.add(signal)
                session.commit()
                
            return {
                "success": True, "order_id": order.get('id'), "side": preview['target_side'], "price": price_str, "amount": amount_str,
                "reduce_only": params.get('reduceOnly', False), "is_bulk": is_bulk
            }
        except Exception as e:
            logger.error(f"[UCOE] execution failed: {e}")
            raise e

exchange_service = UnifiedCounterOrderService()
