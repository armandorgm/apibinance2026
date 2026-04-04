"""
Vinculación de posiciones abiertas con órdenes FAPI CONDITIONAL por createTime (timestamp Binance).

Prioridad: emparejar entradas con algoOrders donde algoType == CONDITIONAL solo si createTime
coincide con el timestamp de la ejecución de entrada. El resto sigue la heurística flotante.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from pydantic import BaseModel

from app.services.order_type_tags import merge_tag_lists, tags_from_open_order_response


class ConditionalExitInfo(BaseModel):
    """Salida vinculada calculada en backend (no en el cliente)."""

    algo_id: str
    order_type: str
    side: str
    trigger_price: float
    create_time_ms: int
    conditional_kind: Optional[str] = None
    algo_type: Optional[str] = None


def filter_conditional_algo_orders(orders: Sequence[Any]) -> List[Any]:
    """Filter órdenes cuyo algoType sea CONDITIONAL (Binance FAPI)."""
    out: List[Any] = []
    for o in orders:
        at = getattr(o, "algo_type", None)
        if at and str(at).upper() == "CONDITIONAL":
            out.append(o)
    return out


def aggregate_conditional_orders_by_create_time(orders: Sequence[Any]) -> Dict[int, List[Any]]:
    """Agrupa órdenes CONDITIONAL por create_time_ms (solo entradas con ms definido)."""
    by_ts: Dict[int, List[Any]] = defaultdict(list)
    for o in orders:
        ct = getattr(o, "create_time_ms", None)
        if ct is not None:
            by_ts[int(ct)].append(o)
    return dict(by_ts)


def order_closes_entry_position(entry_side: str, order: Any) -> bool:
    """Futuros: SELL cierra long; BUY cierra short."""
    es = (entry_side or "").lower()
    if es == "buy":
        return bool(getattr(order, "closes_long", None))
    if es == "sell":
        return bool(getattr(order, "closes_short", None))
    return False


def cross_entry_timestamp_with_conditional_orders(
    entry_timestamp_ms: int,
    conditional_by_create_time: Dict[int, List[Any]],
    entry_side: str,
) -> List[Any]:
    """
    Cruce estricto: mismo createTime que el timestamp de entrada, y la orden debe cerrar la posición.
    """
    candidates = conditional_by_create_time.get(int(entry_timestamp_ms), [])
    return [o for o in candidates if order_closes_entry_position(entry_side, o)]


def sort_linked_orders_for_display(orders: Sequence[Any]) -> List[Any]:
    """TP antes que SL/trailing para la fila principal de UI."""
    kind_rank = {"take_profit": 0, "stop_loss": 1, "trailing": 2}

    def key(o: Any) -> Tuple[int, str]:
        k = getattr(o, "conditional_kind", None) or ""
        return (kind_rank.get(str(k), 9), str(getattr(o, "id", "")))

    return sorted(orders, key=key)


def build_conditional_exit_info(primary: Any) -> ConditionalExitInfo:
    return ConditionalExitInfo(
        algo_id=str(getattr(primary, "id", "") or ""),
        order_type=str(getattr(primary, "type", "") or getattr(primary, "order_type", "") or ""),
        side=str(getattr(primary, "side", "") or ""),
        trigger_price=float(getattr(primary, "price", 0.0) or 0.0),
        create_time_ms=int(getattr(primary, "create_time_ms", 0) or 0),
        conditional_kind=getattr(primary, "conditional_kind", None),
        algo_type=getattr(primary, "algo_type", None),
    )


def compute_tp_sl_from_order(
    entry_side: str,
    entry_price: float,
    entry_amount: float,
    order: Any,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Devuelve (tp_pnl, sl_pnl) según tipo condicional; solo uno suele aplicar por orden.
    """
    p_price = float(getattr(order, "price", 0.0) or 0.0)
    if p_price <= 0:
        return None, None
    order_amount = float(getattr(order, "amount", 0.0) or 0.0)
    if order_amount <= 0:
        order_amount = entry_amount
    diff = (p_price - entry_price) if entry_side == "buy" else (entry_price - p_price)
    potential = diff * order_amount
    kind = getattr(order, "conditional_kind", None)
    if kind == "take_profit":
        return potential, None
    if kind == "stop_loss":
        return None, potential
    if kind == "trailing":
        return potential if potential > 0 else None, potential if potential <= 0 else None
    # Sin clasificación: usar signo del potencial
    if potential > 0:
        return potential, None
    return None, potential


def merge_tp_sl(
    a: Tuple[Optional[float], Optional[float]],
    b: Tuple[Optional[float], Optional[float]],
) -> Tuple[Optional[float], Optional[float]]:
    tp_a, sl_a = a
    tp_b, sl_b = b
    tp = tp_a if tp_a is not None else tp_b
    sl = sl_a if sl_a is not None else sl_b
    return tp, sl


def apply_legacy_floating_tp_sl(
    entry_side: str,
    entry_price: float,
    entry_amount: float,
    open_orders: Sequence[Any],
    matched_order_ids: set,
) -> Tuple[Optional[float], Optional[float], List[str]]:
    """
    Heurística previa: órdenes opuestas con precio > 0; asigna TP/SL por signo del potencial.
    Omite ids ya emparejados por timestamp.
    """
    tp_val: Optional[float] = None
    sl_val: Optional[float] = None
    last_tp_tags: List[str] = []
    last_sl_tags: List[str] = []
    es = (entry_side or "").lower()

    for order in open_orders:
        oid = str(getattr(order, "id", ""))
        if oid in matched_order_ids:
            continue
        order_side = (getattr(order, "side", None) or "").lower()
        if not order_side or order_side == es:
            continue
        p_price = float(getattr(order, "price", 0.0) or 0.0)
        if p_price <= 0:
            continue
        order_amount = float(getattr(order, "amount", 0.0) or 0.0)
        if order_amount <= 0:
            order_amount = entry_amount
        diff = (p_price - entry_price) if es == "buy" else (entry_price - p_price)
        potential = diff * order_amount
        if potential > 0:
            tp_val = potential
            last_tp_tags = tags_from_open_order_response(order)
        else:
            sl_val = potential
            last_sl_tags = tags_from_open_order_response(order)
        matched_order_ids.add(oid)
    exit_tags = merge_tag_lists([last_tp_tags, last_sl_tags])
    return tp_val, sl_val, exit_tags
