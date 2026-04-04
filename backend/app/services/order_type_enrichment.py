"""
Enriquecimiento de fills con tipo de orden real desde Binance (fetch_order por orderId).
"""
from __future__ import annotations

from typing import Set

from sqlmodel import select

from app.db.database import Fill, Trade, get_session_direct
from app.core.exchange import exchange_manager
from app.services.order_type_tags import extract_binance_order_type_from_ccxt_order
from app.services.tracker_logic import TradeTracker


async def enrich_missing_fill_order_types(symbol: str, max_fetch: int = 80) -> int:
    """
    Completa Fill.order_type para fills con order_id y sin tipo.
    Limita peticiones por llamada para no bloquear la API.
    """
    with get_session_direct() as session:
        fills = list(
            session.exec(select(Fill).where(Fill.symbol == symbol)).all()
        )
        fills = [f for f in fills if f.order_id and not f.order_type]
        if not fills:
            return 0

        seen: Set[str] = set()
        order_ids: list[str] = []
        for f in fills:
            oid = str(f.order_id or "").strip()
            if not oid or oid in seen:
                continue
            seen.add(oid)
            order_ids.append(oid)

        updated = 0
        for oid in order_ids[:max_fetch]:
            try:
                raw = await exchange_manager.fetch_order_raw(symbol, oid)
                ot = extract_binance_order_type_from_ccxt_order(raw)
            except Exception:
                ot = None
            if not ot:
                continue
            for f in fills:
                if str(f.order_id or "") == oid and not f.order_type:
                    f.order_type = ot
                    session.add(f)
                    updated += 1
        session.commit()
        return updated


def sync_trade_order_metadata_from_fills(symbol: str, logic: str) -> int:
    """
    Actualiza Trade.entry/exit order ids y tipos desde el matching actual y fills enriquecidos.
    """
    tracker = TradeTracker(symbol)
    with get_session_direct() as session:
        fills = list(
            session.exec(select(Fill).where(Fill.symbol == symbol).order_by(Fill.timestamp)).all()
        )
        if not fills:
            return 0
        matched = tracker.match_trades(fills, logic)
        trades = list(session.exec(select(Trade).where(Trade.symbol == symbol)).all())
        updated = 0
        for tr in trades:
            for m in matched:
                if (
                    tr.entry_timestamp == m["entry_timestamp"]
                    and tr.exit_timestamp == m["exit_timestamp"]
                    and abs(tr.entry_price - m["entry_price"]) < 1e-8
                    and abs(tr.exit_price - m["exit_price"]) < 1e-8
                    and abs(tr.entry_amount - m["entry_amount"]) < 1e-6
                ):
                    tr.entry_order_id = m.get("entry_order_id")
                    tr.exit_order_id = m.get("exit_order_id")
                    tr.entry_order_type = m.get("entry_order_type")
                    tr.exit_order_type = m.get("exit_order_type")
                    session.add(tr)
                    updated += 1
                    break
        session.commit()
        return updated
