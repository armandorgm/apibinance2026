"""
Etiquetas derivadas del tipo de orden Binance / CCXT (precisión desde API).
"""
from __future__ import annotations

from typing import Any, List, Optional, Sequence


def extract_binance_order_type_from_ccxt_order(order: Optional[dict]) -> Optional[str]:
    """
    Prefiere el tipo nativo de Binance (info.origType / type) sobre el tipo unificado CCXT.
    """
    if not order or not isinstance(order, dict):
        return None
    info = order.get("info")
    if isinstance(info, dict):
        for key in ("origType", "type", "orderType"):
            v = info.get(key)
            if v:
                return str(v).strip().upper()
    t = order.get("type")
    if t:
        return str(t).strip().upper()
    return None


def tags_from_binance_order_type(
    order_type: Optional[str],
    *,
    algo_type: Optional[str] = None,
) -> List[str]:
    """
    Convierte un tipo Binance (p.ej. TAKE_PROFIT_MARKET, LIMIT, MARKET) en etiquetas UI.
    """
    tags: List[str] = []
    if algo_type and str(algo_type).upper() == "CONDITIONAL":
        tags.append("CONDITIONAL")
    if not order_type:
        return list(dict.fromkeys(tags))

    ot = str(order_type).upper()

    semantic: List[str] = []
    if "TRAILING" in ot:
        semantic.append("TRAILING_STOP")
    if "TAKE_PROFIT" in ot:
        semantic.append("TAKE_PROFIT")
    elif "STOP" in ot:
        semantic.append("STOP_LOSS")
    if "MARKET" in ot:
        semantic.append("MARKET")
    if "LIMIT" in ot:
        semantic.append("LIMIT")

    if semantic:
        tags.extend(semantic)
    else:
        tags.append(ot)

    return list(dict.fromkeys(tags))


def tags_from_open_order_response(order: Any) -> List[str]:
    """OrderResponse mapeado desde open orders / algo orders."""
    ot = getattr(order, "order_type", None) or getattr(order, "type", None)
    at = getattr(order, "algo_type", None)
    return tags_from_binance_order_type(str(ot) if ot else None, algo_type=str(at) if at else None)


def merge_tag_lists(parts: Sequence[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for p in parts:
        for t in p:
            if t and t not in out:
                out.append(t)
    return out
