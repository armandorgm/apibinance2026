"""
API routes for the Binance Futures Tracker.
"""
from fastapi import APIRouter, HTTPException
from typing import Any, List, Optional
from datetime import datetime
from app.services.bot_service import bot_instance
from sqlmodel import select, Session
from pydantic import BaseModel, ConfigDict
from app.db.database import Fill, Trade, BotSignal, BotConfig, ExchangeLog, get_session_direct, create_db_and_tables, engine
from app.services.tracker_logic import TradeTracker
from app.core.exchange import exchange_manager
from app.services.history_formatter import TradeResponseFormatter, SortByEntryDateDesc, SortByEntryDateAsc, SortByPnLDesc
from app.services.conditional_exit_link import (
    ConditionalExitInfo,
    aggregate_conditional_orders_by_create_time,
    apply_legacy_floating_tp_sl,
    build_conditional_exit_info,
    compute_tp_sl_from_order,
    cross_entry_timestamp_with_conditional_orders,
    filter_conditional_algo_orders,
    merge_tp_sl,
    sort_linked_orders_for_display,
)
from app.services.order_type_tags import (
    merge_tag_lists,
    tags_from_binance_order_type,
    tags_from_open_order_response,
)
from app.services.order_type_enrichment import (
    enrich_missing_fill_order_types,
    sync_trade_order_metadata_from_fills,
)
from abc import ABC, abstractmethod
import json

router = APIRouter()


class SyncResponse(BaseModel):
    """Response model for sync endpoint."""
    success: bool
    fills_added: int
    trades_created: int
    message: str
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class TradeResponse(BaseModel):
    """Response model for trade history."""
    model_config = ConfigDict(extra='ignore')

    id: int
    symbol: str
    entry_side: str
    entry_price: float
    entry_amount: float
    entry_fee: float
    entry_datetime: datetime
    exit_side: Optional[str]
    exit_price: Optional[float]
    exit_amount: Optional[float]
    exit_fee: Optional[float]
    exit_datetime: Optional[datetime]
    pnl_net: float
    pnl_percentage: float
    duration_seconds: int
    created_at: datetime
    is_orphan: bool = False
    
    # Pendientes y Extensiones UI
    is_pending: bool = False
    order_type: Optional[str] = None
    tp_pnl: Optional[float] = None
    sl_pnl: Optional[float] = None
    # Salida condicional vinculada en servidor (createTime == entry timestamp)
    conditional_exit: Optional[ConditionalExitInfo] = None
    # Tipos de orden (entrada / salida) derivados de Binance con precisión
    entry_order_tags: List[str] = []
    exit_order_tags: List[str] = []

class OrderResponse(BaseModel):
    """Response model for live open orders."""
    id: str
    symbol: str
    type: str
    side: str
    price: float
    amount: float
    filled: float
    remaining: float
    status: str
    datetime: datetime
    is_bot_logged: bool = False
    error_message: Optional[str] = None

    # Pendientes y Extensiones UI
    is_pending: bool = False
    order_type: Optional[str] = None
    tp_pnl: Optional[float] = None
    sl_pnl: Optional[float] = None
    is_algo: bool = False
    # Futures conditional (openAlgoOrders): positionSide + clasificación TP/SL
    position_side: Optional[str] = None
    algo_type: Optional[str] = None
    conditional_kind: Optional[str] = None  # take_profit | stop_loss | trailing
    closes_long: Optional[bool] = None
    closes_short: Optional[bool] = None
    # Binance FAPI createTime (ms); solo CONDITIONAL suele tenerlo para cruce con fills
    create_time_ms: Optional[int] = None

# --- SOLID ORDER MAPPERS ---

class OrderMapper(ABC):
    """Abstract Base Class for order mapping (SOLID)."""
    @abstractmethod
    def map(self, raw: dict) -> OrderResponse:
        pass

class StandardOrderMapper(OrderMapper):
    """Maps Standard v1/openOrders to OrderResponse."""
    def map(self, raw: dict) -> OrderResponse:
        return OrderResponse(
            id=str(raw.get('orderId') or raw.get('id', '')),
            symbol=raw.get('symbol', ''),
            type=raw.get('type', '').upper(),
            side=(raw.get('side') or '').lower(),
            price=float(raw.get('price', 0.0)),
            amount=float(raw.get('origQty') or raw.get('amount', 0.0)),
            filled=float(raw.get('executedQty') or raw.get('filled', 0.0)),
            remaining=float(raw.get('remaining', 0.0)) if 'remaining' in raw else (float(raw.get('origQty', 0.0)) - float(raw.get('executedQty', 0.0))),
            status=raw.get('status', '').upper(),
            datetime=datetime.fromtimestamp(raw['timestamp'] / 1000) if raw.get('timestamp') else datetime.utcnow(),
            is_algo=False,
            is_pending=True,  # By definition if open
            create_time_ms=int(raw['timestamp']) if raw.get('timestamp') is not None else None,
        )

def _algo_order_timestamp(raw: dict) -> datetime:
    """Ms timestamps from FAPI openAlgoOrders or SAPI algo futures."""
    for key in ('time', 'createTime', 'updateTime', 'bookTime', 'transactTime'):
        v = raw.get(key)
        if v is not None and v != 0:
            try:
                return datetime.utcfromtimestamp(int(v) / 1000)
            except (TypeError, ValueError, OSError):
                continue
    return datetime.utcnow()


def _conditional_kind_from_order_type(order_type: str) -> Optional[str]:
    ot = (order_type or '').upper()
    if 'TRAILING' in ot:
        return 'trailing'
    if 'TAKE_PROFIT' in ot:
        return 'take_profit'
    if 'STOP' in ot:
        return 'stop_loss'
    return None


class AlgoOrderMapper(OrderMapper):
    """
    Maps Binance futures algo / conditional orders.
    FAPI openAlgoOrders: orderType, triggerPrice, side (SELL = TP para long), quantity, algoType CONDITIONAL.
    SAPI algo/futures: totalQty, bookTime, etc.
    """
    def map(self, raw: dict) -> OrderResponse:
        order_type = (
            raw.get('orderType') or raw.get('type') or 'ALGO'
        )
        order_type_u = str(order_type).upper()
        side = (raw.get('side') or '').lower()
        position_side = (raw.get('positionSide') or '') or None

        qty = float(raw.get('quantity') or raw.get('totalQty') or raw.get('amount') or 0.0)
        filled = float(raw.get('executedQty') or 0.0)
        remaining = qty - filled

        trigger = raw.get('triggerPrice') or raw.get('stopPrice') or 0.0
        price = float(trigger) if trigger not in (None, '') else 0.0

        kind = _conditional_kind_from_order_type(order_type_u)
        # Futuros reduce-only: SELL cierra / toma profit en posición LONG; BUY en SHORT.
        closes_long = side == 'sell'
        closes_short = side == 'buy'

        create_time_ms = None
        ct = raw.get('createTime')
        if ct is not None and ct != 0:
            try:
                create_time_ms = int(ct)
            except (TypeError, ValueError):
                create_time_ms = None

        return OrderResponse(
            id=str(raw.get('algoId', '')),
            symbol=raw.get('symbol', ''),
            type=order_type_u,
            side=side,
            price=price,
            amount=qty,
            filled=filled,
            remaining=remaining,
            status=str(raw.get('algoStatus') or raw.get('status') or 'NEW').upper(),
            datetime=_algo_order_timestamp(raw),
            is_algo=True,
            is_pending=True,
            order_type=order_type_u,
            position_side=position_side.lower() if position_side else None,
            algo_type=(raw.get('algoType') or None),
            conditional_kind=kind,
            closes_long=closes_long,
            closes_short=closes_short,
            create_time_ms=create_time_ms,
        )

def get_order_mapper(raw: dict) -> OrderMapper:
    """Factory to get the correct mapper based on source tag."""
    if raw.get('_source') == 'algo':
        return AlgoOrderMapper()
    return StandardOrderMapper()

# --- END SOLID ORDER MAPPERS ---


@router.get("/trades/history", response_model=List[TradeResponse])
async def get_trade_history(symbol: str = "BTC/USDT", logic: str = "fifo", sort_by: str = "recent"):
    """
    Get processed trade history.
    Returns list of individual trades with PnL calculations.
    """
    try:
        # Normalize incoming symbol to exchange market format (e.g. BTCUSDT -> BTC/USDT)
        try:
            symbol = await exchange_manager.normalize_symbol(symbol)
        except Exception:
            pass

        try:
            await enrich_missing_fill_order_types(symbol)
            sync_trade_order_metadata_from_fills(symbol, "atomic_fifo")
        except Exception:
            pass

        tracker = TradeTracker(symbol)
        
        # Determine strategy from logic string
        strategy = logic.lower()
        if strategy not in ["fifo", "lifo", "atomic_fifo", "atomic_lifo"]:
            # Fallback for UI if it sends "atomic"
            strategy = "atomic_fifo" if strategy == "atomic" else "fifo"

        # Only atomic_fifo reads from DB (pre-saved trades).
        # Everything else (fifo, lifo, atomic_lifo) is calculated live from fills
        # so the correct strategy is always applied without DB interference.
        if strategy != "atomic_fifo":
            with get_session_direct() as session:
                statement = select(Fill).where(Fill.symbol == symbol).order_by(Fill.timestamp)
                fills = session.exec(statement).all()
            matched_trades = tracker.match_trades(fills, strategy)
            matched_trades.sort(key=lambda x: x['entry_timestamp'], reverse=True)
            closed = [
                TradeResponse(
                    **{
                        **t,
                        'id': i,
                        'created_at': t['entry_datetime'],
                        'entry_order_tags': tags_from_binance_order_type(t.get('entry_order_type')),
                        'exit_order_tags': tags_from_binance_order_type(t.get('exit_order_type')),
                    }
                )
                for i, t in enumerate(matched_trades)
            ]
        else:
            with get_session_direct() as session:
                statement = (
                    select(Trade)
                    .where(Trade.symbol == symbol)
                    .order_by(Trade.entry_datetime.desc())
                )
                trades = session.exec(statement).all()

            # Build closed trades from DB
            closed = [
                TradeResponse(
                    **{
                        **trade.model_dump(),
                        'entry_order_tags': tags_from_binance_order_type(trade.entry_order_type),
                        'exit_order_tags': tags_from_binance_order_type(trade.exit_order_type),
                    }
                )
                for trade in trades
            ]

        # Compute open positions and unrealized PnL
        try:
            open_positions = tracker.compute_open_positions(logic=logic)
        except Exception:
            open_positions = []

        # Fetch pending orders from the order book
        try:
            raw_open_orders = await exchange_manager.fetch_open_orders(symbol)
            
            # Formally map CCXT orders and Binance Algo Responses using our SOLID factories
            open_orders = []
            for raw in raw_open_orders:
                mapper = get_order_mapper(raw)
                open_orders.append(mapper.map(raw))
        except Exception:
            open_orders = []

        unrealized = []
        matched_order_ids: set = set()

        conditional_by_ts = aggregate_conditional_orders_by_create_time(
            filter_conditional_algo_orders(open_orders)
        )

        if open_positions:
            try:
                ticker = await exchange_manager.fetch_ticker(symbol)
                current_price = float(ticker.get('last') or ticker.get('close') or 0)
            except Exception:
                current_price = 0.0

            for op in open_positions:
                entry_side = op['entry_side']
                entry_price = float(op['entry_price'])
                entry_amount = float(op['entry_amount'])
                entry_fee = float(op.get('entry_fee') or 0.0)

                net_pnl, pnl_percentage = tracker.calculate_pnl(
                    entry_price=entry_price,
                    entry_amount=entry_amount,
                    entry_fee=entry_fee,
                    exit_price=current_price,
                    exit_amount=entry_amount,
                    exit_fee=0.0,
                    entry_side=entry_side
                )

                tp_pnl_val: Optional[float] = None
                sl_pnl_val: Optional[float] = None
                cond_exit_info: Optional[ConditionalExitInfo] = None
                linked_sorted: List[Any] = []

                entry_ts_ms = int(op['entry_timestamp'])

                if not op.get('is_orphan'):
                    linked = cross_entry_timestamp_with_conditional_orders(
                        entry_ts_ms, conditional_by_ts, entry_side
                    )
                    if linked:
                        linked_sorted = sort_linked_orders_for_display(linked)
                        for o in linked_sorted:
                            matched_order_ids.add(str(getattr(o, 'id', '')))
                        acc_tp: Optional[float] = None
                        acc_sl: Optional[float] = None
                        for o in linked_sorted:
                            tpp, slp = compute_tp_sl_from_order(
                                entry_side, entry_price, entry_amount, o
                            )
                            acc_tp, acc_sl = merge_tp_sl((acc_tp, acc_sl), (tpp, slp))
                        tp_pnl_val, sl_pnl_val = acc_tp, acc_sl
                        cond_exit_info = build_conditional_exit_info(linked_sorted[0])

                legacy_exit_tags: List[str] = []
                if cond_exit_info is None:
                    tp_pnl_val, sl_pnl_val, legacy_exit_tags = apply_legacy_floating_tp_sl(
                        entry_side,
                        entry_price,
                        entry_amount,
                        open_orders,
                        matched_order_ids,
                    )

                entry_tags = tags_from_binance_order_type(op.get('entry_order_type'))
                if linked_sorted:
                    exit_tags = merge_tag_lists([tags_from_open_order_response(o) for o in linked_sorted])
                else:
                    exit_tags = legacy_exit_tags if legacy_exit_tags else ["FLOATING"]

                unrealized.append(TradeResponse(
                    id=0,
                    symbol=symbol,
                    entry_side=entry_side,
                    entry_price=entry_price,
                    entry_amount=entry_amount,
                    entry_fee=entry_fee,
                    entry_datetime=op['entry_datetime'],
                    exit_side='',
                    exit_price=current_price if current_price else None,
                    exit_amount=None,
                    exit_fee=None,
                    exit_datetime=None,
                    pnl_net=net_pnl,
                    pnl_percentage=pnl_percentage,
                    duration_seconds=0,
                    created_at=op['entry_datetime'],
                    tp_pnl=tp_pnl_val,
                    sl_pnl=sl_pnl_val,
                    conditional_exit=cond_exit_info,
                    is_orphan=bool(op.get('is_orphan', False)),
                    entry_order_tags=entry_tags,
                    exit_order_tags=exit_tags,
                ))
                
        # Append unmatched open orders as standalone Pending Rows
        standalone_pending = []
        for order in open_orders:
            if order.id not in matched_order_ids:
                standalone_pending.append(TradeResponse(
                    id=0,
                    symbol=symbol,
                    entry_side=(order.side or 'buy').lower(),
                    entry_price=order.price,
                    entry_amount=order.amount,
                    entry_fee=0.0,
                    entry_datetime=order.datetime,
                    exit_side='',
                    exit_price=None,
                    exit_amount=None,
                    exit_fee=None,
                    exit_datetime=None,
                    pnl_net=0.0,
                    pnl_percentage=0.0,
                    duration_seconds=0,
                    created_at=order.datetime,
                    is_pending=True,
                    order_type=order.type,
                    entry_order_tags=tags_from_open_order_response(order),
                    exit_order_tags=["PENDING"],
                ))

        # Return combined trades processed by the Strategy Pattern formatter
        if sort_by == "oldest":
            strategy = SortByEntryDateAsc()
        elif sort_by == "pnl_desc":
            strategy = SortByPnLDesc()
        else:
            strategy = SortByEntryDateDesc() # default to recent
            
        formatter = TradeResponseFormatter(sorter=strategy)
        return formatter.format_and_sort(closed, unrealized + standalone_pending)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trade history: {str(e)}")


@router.post("/sync", response_model=SyncResponse)
async def sync_trades(symbol: str = "BTC/USDT", logic: str = "atomic_fifo"):
    """
    Sync trades from Binance.
    Fetches new fills from Binance, saves them, and processes them into trades.
    """
    # #region agent log
    import json
    import time
    _log_path = r"c:\Users\arman\OneDrive\Documentos\Visual Studio 2022\apibinance2026\.cursor\debug.log"
    try:
        with open(_log_path, "a", encoding="utf-8") as _f:
            _f.write(json.dumps({"message": "sync_trades called", "data": {"symbol": symbol}, "hypothesisId": "A", "location": "routes.py:sync_trades", "timestamp": int(time.time() * 1000)}) + "\n")
    except Exception:
        pass
    # #endregion
    try:
        # Normalize requested symbol before querying/syncing
        try:
            symbol = await exchange_manager.normalize_symbol(symbol)
        except Exception:
            pass
        # Initialize database tables if they don't exist
        create_db_and_tables()
        
        fills_added = 0
        trades_created = 0
        
        # Fetch trades from Binance
        # Get the most recent fill timestamp to only fetch new ones
        with get_session_direct() as session:
            statement = (
                select(Fill)
                .where(Fill.symbol == symbol)
                .order_by(Fill.timestamp.desc())
                .limit(1)
            )
            last_fill = session.exec(statement).first()
            since = last_fill.timestamp + 1 if last_fill else None
        
        # Fetch new trades from Binance
        binance_trades = await exchange_manager.fetch_my_trades(symbol, since=since)
        
        # Save new fills to database
        with get_session_direct() as session:
            existing_trade_ids = set()
            existing_statement = select(Fill.trade_id)
            existing_ids = session.exec(existing_statement).all()
            existing_trade_ids.update(existing_ids)
            
            for trade_data in binance_trades:
                trade_id_str = str(trade_data['id'])
                if trade_id_str not in existing_trade_ids:
                    # Handle fee structure (can be dict or number)
                    fee_cost = 0.0
                    fee_currency = 'USDT'
                    if isinstance(trade_data.get('fee'), dict):
                        fee_cost = abs(trade_data['fee'].get('cost', 0))
                        fee_currency = trade_data['fee'].get('currency', 'USDT')
                    elif trade_data.get('fee'):
                        fee_cost = abs(float(trade_data['fee']))
                    
                    # Normalize the symbol from the exchange (some exchanges return 'BTCUSDT')
                    try:
                        normalized_fill_symbol = await exchange_manager.normalize_symbol(trade_data.get('symbol') or symbol)
                    except Exception:
                        normalized_fill_symbol = trade_data.get('symbol') or symbol

                    fill = Fill(
                        trade_id=trade_id_str,
                        symbol=normalized_fill_symbol,
                        side=trade_data['side'],
                        amount=abs(trade_data['amount']),
                        price=trade_data['price'],
                        cost=abs(trade_data.get('cost', trade_data['amount'] * trade_data['price'])),
                        fee=fee_cost,
                        fee_currency=fee_currency,
                        timestamp=trade_data['timestamp'],
                        datetime=datetime.fromtimestamp(trade_data['timestamp'] / 1000),
                        order_id=str(trade_data.get('order', '')) if trade_data.get('order') else None
                    )
                    session.add(fill)
                    fills_added += 1
                    existing_trade_ids.add(trade_id_str)  # Prevent duplicates in same batch
            
            session.commit()

        await enrich_missing_fill_order_types(symbol)

        # Process fills into matched trades using selected strategy
        tracker = TradeTracker(symbol)
        trades_created = tracker.process_and_save_trades(strategy_name=logic)
        sync_trade_order_metadata_from_fills(symbol, logic)
        
        return SyncResponse(
            success=True,
            fills_added=fills_added,
            trades_created=trades_created,
            message=f"Sync completed. Added {fills_added} fills, created {trades_created} trades."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing trades: {str(e)}")


@router.post("/sync/historical", response_model=SyncResponse)
async def sync_historical_trades(symbol: str = "BTC/USDT", logic: str = "atomic_fifo", end_time: Optional[int] = None):
    """
    Sync historical trades from Binance.
    Fetches up to 7 days of trades predating the oldest trade in the database,
    or predating the provided end_time (ms).
    """
    try:
        try:
            symbol = await exchange_manager.normalize_symbol(symbol)
        except Exception:
            pass
            
        create_db_and_tables()
        fills_added = 0
        trades_created = 0
        
        with get_session_direct() as session:
            # If end_time is not provided, look for the oldest fill in the database
            if end_time is None:
                statement = (
                    select(Fill)
                    .where(Fill.symbol == symbol)
                    .order_by(Fill.timestamp.asc())
                    .limit(1)
                )
                oldest_fill = session.exec(statement).first()
                
                if oldest_fill:
                    end_time = oldest_fill.timestamp - 1
                else:
                    import time
                    end_time = int(time.time() * 1000)
            
            # 7 days in milliseconds
            seven_days_ms = 7 * 24 * 60 * 60 * 1000
            start_time = end_time - seven_days_ms
            
        binance_trades = await exchange_manager.fetch_my_trades(
            symbol, 
            since=start_time,
            params={"endTime": end_time}
        )

        
        with get_session_direct() as session:
            existing_trade_ids = set()
            existing_statement = select(Fill.trade_id)
            existing_ids = session.exec(existing_statement).all()
            existing_trade_ids.update(existing_ids)
            
            for trade_data in binance_trades:
                trade_id_str = str(trade_data['id'])
                if trade_id_str not in existing_trade_ids:
                    fee_cost = 0.0
                    fee_currency = 'USDT'
                    if isinstance(trade_data.get('fee'), dict):
                        fee_cost = abs(trade_data['fee'].get('cost', 0))
                        fee_currency = trade_data['fee'].get('currency', 'USDT')
                    elif trade_data.get('fee'):
                        fee_cost = abs(float(trade_data['fee']))
                    
                    try:
                        normalized_fill_symbol = await exchange_manager.normalize_symbol(trade_data.get('symbol') or symbol)
                    except Exception:
                        normalized_fill_symbol = trade_data.get('symbol') or symbol

                    fill = Fill(
                        trade_id=trade_id_str,
                        symbol=normalized_fill_symbol,
                        side=trade_data['side'],
                        amount=abs(trade_data['amount']),
                        price=trade_data['price'],
                        cost=abs(trade_data.get('cost', trade_data['amount'] * trade_data['price'])),
                        fee=fee_cost,
                        fee_currency=fee_currency,
                        timestamp=trade_data['timestamp'],
                        datetime=datetime.fromtimestamp(trade_data['timestamp'] / 1000),
                        order_id=str(trade_data.get('order', '')) if trade_data.get('order') else None
                    )
                    session.add(fill)
                    fills_added += 1
                    existing_trade_ids.add(trade_id_str)
            
            session.commit()

        await enrich_missing_fill_order_types(symbol)

        tracker = TradeTracker(symbol)
        # Bug fix: pass the selected strategy so historical sync respects it
        trades_created = tracker.process_and_save_trades(strategy_name=logic)
        sync_trade_order_metadata_from_fills(symbol, logic)
        
        # Calculate start range date strings for message
        start_date = datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d')
        end_date = datetime.fromtimestamp(end_time / 1000).strftime('%Y-%m-%d')
        
        return SyncResponse(
            success=True,
            fills_added=fills_added,
            trades_created=trades_created,
            message=f"Historical sync ({start_date} to {end_date}) completed. Added {fills_added} fills, created {trades_created} trades.",
            start_time=start_time,
            end_time=end_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing historical trades: {str(e)}")


@router.get("/balances")
async def get_balances():
    """Get aggregated account balances (filtered > 0.1 USD)."""
    try:
        futures_balance = await exchange_manager.fetch_balance()
        filtered_futures = {}
        
        for asset, amount in futures_balance.get('total', {}).items():
            if isinstance(amount, (int, float)) and amount > 0:
                # Basic filter rule: > 0.1 for USD stablecoins, > 0.0001 for altcoins
                is_usd = 'USD' in asset
                if (is_usd and amount >= 0.1) or (not is_usd and amount >= 0.0001):
                    filtered_futures[asset] = {
                        "free": futures_balance.get('free', {}).get(asset, 0),
                        "used": futures_balance.get('used', {}).get(asset, 0),
                        "total": amount
                    }
                    
        return {
            "spot": {}, # Spot requires a different CCXT instance; empty for now
            "futures": filtered_futures,
            "totals": {k: v['total'] for k, v in filtered_futures.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching balances: {str(e)}")


@router.get("/symbols")
async def get_symbols():
    """Get list of available symbols from database."""
    try:
        with get_session_direct() as session:
            statement = select(Fill.symbol).distinct()
            symbols = session.exec(statement).all()
            # Ensure returned symbols are normalized
            try:
                normalized = []
                for s in symbols:
                    normalized.append(await exchange_manager.normalize_symbol(s))
            except Exception:
                normalized = list(symbols)
            return {"symbols": normalized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching symbols: {str(e)}")


@router.get("/stats")
async def get_stats(symbol: str = "BTC/USDT", logic: str = "fifo", include_unrealized: bool = False):
    """Get trading statistics for a symbol."""
    try:
        try:
            symbol = await exchange_manager.normalize_symbol(symbol)
        except Exception:
            pass

        tracker = TradeTracker(symbol)
        
        # Match trades on the fly for stats if not standard FIFO
        strategy = logic.lower()
        if strategy not in ["fifo", "lifo", "atomic_fifo", "atomic_lifo"]:
            strategy = "atomic_fifo" if strategy == "atomic" else "fifo"

        if strategy != "fifo":
            with get_session_direct() as session:
                statement = select(Fill).where(Fill.symbol == symbol).order_by(Fill.timestamp)
                fills = session.exec(statement).all()
            trades_data = tracker.match_trades(fills, strategy)
            total_pnl = sum(t['pnl_net'] for t in trades_data) if trades_data else 0.0
            winning_trades = sum(1 for t in trades_data if t['pnl_net'] > 0) if trades_data else 0
            losing_trades = sum(1 for t in trades_data if t['pnl_net'] < 0) if trades_data else 0
            total_count = len(trades_data) if trades_data else 0
        else:
            with get_session_direct() as session:
                statement = select(Trade).where(Trade.symbol == symbol)
                trades = session.exec(statement).all()
                total_pnl = sum(t.pnl_net for t in trades) if trades else 0.0
                winning_trades = sum(1 for t in trades if t.pnl_net > 0) if trades else 0
                losing_trades = sum(1 for t in trades if t.pnl_net < 0) if trades else 0
                total_count = len(trades) if trades else 0

        # Calculate unrealized if requested
        unrealized_pnl = 0.0
        if include_unrealized:
            open_positions = tracker.compute_open_positions(logic=logic)
            if open_positions:
                try:
                    ticker = await exchange_manager.fetch_ticker(symbol)
                    current_price = float(ticker.get('last') or ticker.get('close') or 0)
                    
                    for op in open_positions:
                        # Only include true open positions (Buy without Sell)
                        # Orphan sells (is_orphan) are NOT included in floating PnL usually,
                        # but we can decide based on requirements.
                        # Rule 3 says "unrealized PnL (ganancia flotante)".
                        if op.get('entry_side') == 'buy' and current_price > 0:
                            net, _ = tracker.calculate_pnl(
                                entry_price=op['entry_price'],
                                entry_amount=op['entry_amount'],
                                entry_fee=op['entry_fee'] or 0.0,
                                exit_price=current_price,
                                exit_amount=op['entry_amount'],
                                exit_fee=0.0,
                                entry_side='buy'
                            )
                            unrealized_pnl += net
                except Exception:
                    pass
        
        final_pnl = total_pnl + unrealized_pnl
        
        return {
            "total_trades": total_count,
            "total_pnl": final_pnl,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": (winning_trades / total_count * 100) if total_count > 0 else 0.0,
            "average_pnl": final_pnl / total_count if total_count > 0 else 0.0,
            "unrealized_pnl": unrealized_pnl
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/bot/status")
async def get_bot_status():
    """Get the current running status and last evaluation of the bot."""
    return {
        "is_enabled": bot_instance.is_running,
        "last_run": bot_instance.last_run_status
    }


@router.post("/bot/start")
async def start_bot():
    """Manually start the bot if not already running."""
    await bot_instance.start()
    return {"status": "started"}


@router.post("/bot/stop")
async def stop_bot():
    """Manually stop the bot."""
    await bot_instance.stop()
    return {"status": "stopped"}


@router.get("/bot/logs", response_model=List[BotSignal])
async def get_bot_logs(limit: int = 20):
    """Get the most recent bot evaluation signals/logs."""
    with get_session_direct() as session:
        statement = select(BotSignal).order_by(BotSignal.created_at.desc()).limit(limit)
        results = session.exec(statement).all()
        return list(results)


@router.get("/bot/config")
async def get_bot_config():
    """Get the current dynamic bot configuration."""
    with Session(engine) as session:
        statement = select(BotConfig)
        config = session.exec(statement).first()
        return config


class BotConfigUpdate(BaseModel):
    symbol: Optional[str] = None
    interval: Optional[int] = None
    is_enabled: Optional[bool] = None
    trade_amount: Optional[float] = None


@router.post("/bot/config")
async def update_bot_config(config_update: BotConfigUpdate):
    """Update the bot configuration."""
    # Protective check
    if config_update.trade_amount is not None and config_update.trade_amount <= 0:
        raise HTTPException(status_code=400, detail="El monto de trading debe ser mayor a 0.")
        
    with Session(engine) as session:
        statement = select(BotConfig)
        config = session.exec(statement).first()
        if not config:
            config = BotConfig()
            session.add(config)
        
        if config_update.symbol is not None:
            config.symbol = config_update.symbol
        if config_update.interval is not None:
            config.interval = config_update.interval
        if config_update.is_enabled is not None:
            config.is_enabled = config_update.is_enabled
        if config_update.trade_amount is not None:
            config.trade_amount = config_update.trade_amount
        
        config.updated_at = datetime.utcnow()
        session.add(config)
        session.commit()
        session.refresh(config)
        return config


@router.get("/orders/open", response_model=List[OrderResponse])
async def get_open_orders(symbol: Optional[str] = None):
    """Get live open orders unified from Standard and Algo services."""
    try:
        if symbol:
            try:
                symbol = await exchange_manager.normalize_symbol(symbol)
            except Exception:
                pass
        
        # Fetch amalgamed results from exchange manager
        raw_orders = await exchange_manager.fetch_open_orders(symbol)
        
        # Cross-reference with Bot Logs (Same as before but using normalized list)
        with Session(engine) as session:
            statement = select(BotSignal).where(
                BotSignal.action_taken == "NEW_ORDER",
                BotSignal.success == True
            ).order_by(BotSignal.created_at.desc()).limit(100)
            recent_signals = session.exec(statement).all()
            
            logged_order_ids = set()
            for sig in recent_signals:
                if sig.exchange_response:
                    try:
                        res_data = json.loads(sig.exchange_response)
                        order_id = res_data.get('id') or res_data.get('orderId') or res_data.get('algoId')
                        if order_id:
                            logged_order_ids.add(str(order_id))
                    except:
                        pass

        orders = []
        for raw in raw_orders:
            # Use SOLID mapper factory
            mapper = get_order_mapper(raw)
            normalized = mapper.map(raw)
            
            # Additional enrichment
            normalized.is_bot_logged = normalized.id in logged_order_ids
            orders.append(normalized)
            
        return orders
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching open orders: {str(e)}")


@router.get("/orders/failed", response_model=List[BotSignal])
async def get_failed_orders(limit: int = 50):
    """Get recent failed order attempts from bot logs."""
    try:
        with Session(engine) as session:
            statement = select(BotSignal).where(
                BotSignal.success == False
            ).order_by(BotSignal.created_at.desc()).limit(limit)
            results = session.exec(statement).all()
            return list(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching failed orders: {str(e)}")


@router.get("/exchange/logs", response_model=List[ExchangeLog])
async def get_exchange_logs(limit: int = 100, offset: int = 0):
    """Get recent exchange interaction logs."""
    try:
        with get_session_direct() as session:
            statement = select(ExchangeLog).order_by(ExchangeLog.created_at.desc()).offset(offset).limit(limit)
            results = session.exec(statement).all()
            return list(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching exchange logs: {str(e)}")

@router.get("/debug/algo-orders")
async def debug_algo_orders(symbol: Optional[str] = None):
    """Debug endpoint to fetch raw algo orders response directly from SAPI."""
    try:
        if symbol:
            try:
                symbol = await exchange_manager.normalize_symbol(symbol)
            except Exception:
                pass
                
        exchange = await exchange_manager.get_exchange()
        params = {}
        if symbol:
            params['symbol'] = symbol.replace('/', '')
        
        # Raw request execution
        try:
            res = await exchange.sapiGetAlgoFuturesOpenOrders(params)
            return {"status": "success", "data": res}
        except Exception as e:
            # Fallback en caso de que SAPI no funcione y queramos usar request
            try:
                res = await exchange.request('algo/futures/openOrders', 'sapi', 'GET', params)
                return {"status": "success_fallback", "data": res}
            except Exception as e2:
                return {"status": "error", "message": str(e), "fallback_error": str(e2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical error in debug endpoint: {str(e)}")

class PostmanRequest(BaseModel):
    path: str
    api: str = "fapiPrivate"
    method: str = "GET"
    params: dict = {}

@router.post("/debug/postman")
async def debug_postman(payload: PostmanRequest):
    """Generic Postman-like proxy to test raw properties matching CCXT logic."""
    try:
        exchange = await exchange_manager.get_exchange()
        # Direct bypass proxy through CCXT wrapper
        res = await exchange.request(payload.path, payload.api, payload.method, payload.params)
        return {"status": "success", "data": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}
