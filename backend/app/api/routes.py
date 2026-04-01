"""
API routes for the Binance Futures Tracker.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from app.services.bot_service import bot_instance
from sqlmodel import select, Session
from pydantic import BaseModel
from app.db.database import Fill, Trade, BotSignal, BotConfig, get_session_direct, create_db_and_tables, engine
from app.services.tracker_logic import TradeTracker
from app.core.exchange import exchange_manager
from app.services.history_formatter import TradeResponseFormatter, SortByEntryDateDesc, SortByEntryDateAsc, SortByPnLDesc

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
            closed = [TradeResponse(**{**t, 'id': i, 'created_at': t['entry_datetime']}) for i, t in enumerate(matched_trades)]
        else:
            with get_session_direct() as session:
                statement = (
                    select(Trade)
                    .where(Trade.symbol == symbol)
                    .order_by(Trade.entry_datetime.desc())
                )
                trades = session.exec(statement).all()

            # Build closed trades from DB
            closed = [TradeResponse(**trade.model_dump()) for trade in trades]

        # Compute open positions and unrealized PnL
        try:
            open_positions = tracker.compute_open_positions(logic=logic)
        except Exception:
            open_positions = []

        unrealized = []
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

                unrealized.append(TradeResponse(
                    id=0,
                    symbol=symbol,
                    entry_side=entry_side,
                    entry_price=entry_price,
                    entry_amount=entry_amount,
                    entry_fee=entry_fee,
                    entry_datetime=op['entry_datetime'],
                    # Use empty string instead of null to avoid frontend `.toUpperCase()` errors
                    exit_side='',
                    # show current market price as provisional exit price for UI
                    exit_price=current_price if current_price else None,
                    exit_amount=None,
                    exit_fee=None,
                    exit_datetime=None,
                    pnl_net=net_pnl,
                    pnl_percentage=pnl_percentage,
                    duration_seconds=0,
                    created_at=op['entry_datetime']
                ))

        # Return combined trades processed by the Strategy Pattern formatter
        if sort_by == "oldest":
            strategy = SortByEntryDateAsc()
        elif sort_by == "pnl_desc":
            strategy = SortByPnLDesc()
        else:
            strategy = SortByEntryDateDesc() # default to recent
            
        formatter = TradeResponseFormatter(sorter=strategy)
        return formatter.format_and_sort(closed, unrealized)
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
        
        # Process fills into matched trades using selected strategy
        tracker = TradeTracker(symbol)
        trades_created = tracker.process_and_save_trades(strategy_name=logic)
        
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
        
        tracker = TradeTracker(symbol)
        # Bug fix: pass the selected strategy so historical sync respects it
        trades_created = tracker.process_and_save_trades(strategy_name=logic)
        
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
