"""
API routes for the Binance Futures Tracker.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.tracker_logic import FIFOTracker
from app.core.exchange import exchange_manager
from app.db.database import Fill, Trade, get_session_direct, create_db_and_tables
from sqlmodel import select
from pydantic import BaseModel


router = APIRouter()


class SyncResponse(BaseModel):
    """Response model for sync endpoint."""
    success: bool
    fills_added: int
    trades_created: int
    message: str


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
async def get_trade_history(symbol: str = "BTC/USDT"):
    """
    Get processed trade history.
    Returns list of individual trades with PnL calculations.
    """
    try:
        # Normalize incoming symbol to exchange market format (e.g. BTCUSDT -> BTC/USDT)
        try:
            symbol = exchange_manager.normalize_symbol(symbol)
        except Exception:
            pass
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
            tracker = FIFOTracker(symbol)
            open_positions = tracker.compute_open_positions()
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

                net_pnl, pnl_percentage = FIFOTracker(symbol).calculate_pnl(
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

        # Return closed trades first, then open/unrealized positions
        return closed + unrealized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trade history: {str(e)}")


@router.post("/sync", response_model=SyncResponse)
async def sync_trades(symbol: str = "BTC/USDT"):
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
            symbol = exchange_manager.normalize_symbol(symbol)
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
                        normalized_fill_symbol = exchange_manager.normalize_symbol(trade_data.get('symbol') or symbol)
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
        
        # Process fills into matched trades
        tracker = FIFOTracker(symbol)
        trades_created = tracker.process_and_save_trades()
        
        return SyncResponse(
            success=True,
            fills_added=fills_added,
            trades_created=trades_created,
            message=f"Sync completed. Added {fills_added} fills, created {trades_created} trades."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing trades: {str(e)}")


@router.get("/symbols")
async def get_symbols():
    """Get list of available symbols from database."""
    try:
        with get_session_direct() as session:
            statement = select(Fill.symbol).distinct()
            symbols = session.exec(statement).all()
            # Ensure returned symbols are normalized
            try:
                normalized = [exchange_manager.normalize_symbol(s) for s in symbols]
            except Exception:
                normalized = list(symbols)
            return {"symbols": normalized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching symbols: {str(e)}")


@router.get("/stats")
async def get_stats(symbol: str = "BTC/USDT"):
    """Get trading statistics for a symbol."""
    try:
        # Normalize requested symbol
        try:
            symbol = exchange_manager.normalize_symbol(symbol)
        except Exception:
            pass

        with get_session_direct() as session:
            statement = select(Trade).where(Trade.symbol == symbol)
            trades = session.exec(statement).all()
            
            if not trades:
                return {
                    "total_trades": 0,
                    "total_pnl": 0.0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "average_pnl": 0.0
                }
            
            total_pnl = sum(t.pnl_net for t in trades)
            winning_trades = sum(1 for t in trades if t.pnl_net > 0)
            losing_trades = sum(1 for t in trades if t.pnl_net < 0)
            
            return {
                "total_trades": len(trades),
                "total_pnl": total_pnl,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": (winning_trades / len(trades) * 100) if trades else 0.0,
                "average_pnl": total_pnl / len(trades) if trades else 0.0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
