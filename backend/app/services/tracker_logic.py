"""
Core business logic for FIFO trade matching and PnL calculation.
This is the heart of the system - matches buys and sells using FIFO algorithm.
"""
from typing import List, Dict, Any, Tuple
from app.db.database import Fill, Trade, get_session_direct
from sqlmodel import select
from collections import deque


from abc import ABC, abstractmethod

class MatchStrategy(ABC):
    """Base interface for trade matching strategies."""
    @abstractmethod
    def match(self, tracker: 'TradeTracker', fills: List[Fill]) -> List[Dict[str, Any]]:
        pass

class AtomicMatchStrategy(MatchStrategy):
    """
    Matches trades ONLY if they have the exact same amount.
    Ideal for Binance Buy + Take Profit / Stop Loss orders.
    """
    def __init__(self, is_fifo: bool = True):
        self.is_fifo = is_fifo

    def match(self, tracker: 'TradeTracker', fills: List[Fill]) -> List[Dict[str, Any]]:
        grouped_orders = tracker._group_fills_by_order(fills)
        buys = [o for o in grouped_orders if o['side'] == 'buy']
        sells = [o for o in grouped_orders if o['side'] == 'sell']
        
        matched_trades = []
        used_buys = set() 

        for sell in sells:
            candidates = []
            for i, buy in enumerate(buys):
                if i in used_buys:
                    continue
                if buy['timestamp'] >= sell['timestamp']:
                    continue
                if abs(buy['amount'] - sell['amount']) < 1e-8:
                    candidates.append(i)
            
            if not candidates:
                continue
                
            chosen_idx = candidates[0] if self.is_fifo else candidates[-1]
            buy = buys[chosen_idx]
            used_buys.add(chosen_idx)
            
            pnl_data = tracker.calculate_pnl(
                entry_price=buy['price'], entry_amount=buy['amount'], entry_fee=buy['fee'],
                exit_price=sell['price'], exit_amount=sell['amount'], exit_fee=sell['fee'],
                entry_side='buy'
            )
            
            matched_trades.append(tracker._format_trade_data(buy, sell, pnl_data))

        return matched_trades

class FIFOMatchStrategy(MatchStrategy):
    """
    Standard FIFO (First-In-First-Out). 
    Matches earliest buys first, supporting partial fills.
    """
    def match(self, tracker: 'TradeTracker', fills: List[Fill]) -> List[Dict[str, Any]]:
        grouped_orders = tracker._group_fills_by_order(fills)
        # We need a copy of buys that we can "consume"
        buys = [dict(o) for o in grouped_orders if o['side'] == 'buy']
        sells = [dict(o) for o in grouped_orders if o['side'] == 'sell']
        
        matched_trades = []
        
        for sell in sells:
            remaining_sell_qty = sell['amount']
            
            for buy in buys:
                if remaining_sell_qty <= 0:
                    break
                if buy['amount'] <= 0 or buy['timestamp'] >= sell['timestamp']:
                    continue
                
                match_qty = min(buy['amount'], remaining_sell_qty)
                
                # Proportional fee for partial match
                buy_fee_share = (match_qty / buy['amount']) * buy['fee'] if buy['amount'] > 0 else 0
                sell_fee_share = (match_qty / sell['amount']) * sell['fee'] if sell['amount'] > 0 else 0
                
                pnl_data = tracker.calculate_pnl(
                    entry_price=buy['price'], entry_amount=match_qty, entry_fee=buy_fee_share,
                    exit_price=sell['price'], exit_amount=match_qty, exit_fee=sell_fee_share,
                    entry_side='buy'
                )
                
                matched_trades.append(tracker._format_trade_data(buy, sell, pnl_data, match_qty))
                
                buy['amount'] -= match_qty
                buy['fee'] -= buy_fee_share
                remaining_sell_qty -= match_qty

        return matched_trades

class LIFOMatchStrategy(MatchStrategy):
    """
    Standard LIFO (Last-In-First-Out).
    Matches latest buys first, supporting partial fills.
    """
    def match(self, tracker: 'TradeTracker', fills: List[Fill]) -> List[Dict[str, Any]]:
        grouped_orders = tracker._group_fills_by_order(fills)
        buys = [dict(o) for o in grouped_orders if o['side'] == 'buy']
        sells = [dict(o) for o in grouped_orders if o['side'] == 'sell']
        
        matched_trades = []
        
        for sell in sells:
            remaining_sell_qty = sell['amount']
            # Sort buys by timestamp DESC for LIFO
            candidate_buys = sorted(
                [b for b in buys if b['timestamp'] < sell['timestamp'] and b['amount'] > 0],
                key=lambda x: x['timestamp'], 
                reverse=True
            )
            
            for buy in candidate_buys:
                if remaining_sell_qty <= 0:
                    break
                
                match_qty = min(buy['amount'], remaining_sell_qty)
                
                buy_fee_share = (match_qty / buy['amount']) * buy['fee'] if buy['amount'] > 0 else 0
                sell_fee_share = (match_qty / sell['amount']) * sell['fee'] if sell['amount'] > 0 else 0
                
                pnl_data = tracker.calculate_pnl(
                    entry_price=buy['price'], entry_amount=match_qty, entry_fee=buy_fee_share,
                    exit_price=sell['price'], exit_amount=match_qty, exit_fee=sell_fee_share,
                    entry_side='buy'
                )
                
                matched_trades.append(tracker._format_trade_data(buy, sell, pnl_data, match_qty))
                
                buy['amount'] -= match_qty
                buy['fee'] -= buy_fee_share
                remaining_sell_qty -= match_qty

        return matched_trades


class TradeTracker:
    """
    Trade tracker that delegates matching logic to modular strategies.
    Supports FIFO, LIFO, and ATOMIC (Exact Match).
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
    
    def calculate_pnl(
        self,
        entry_price: float,
        entry_amount: float,
        entry_fee: float,
        exit_price: float,
        exit_amount: float,
        exit_fee: float,
        entry_side: str
    ) -> Tuple[float, float]:
        """
        Calculate PnL for a matched trade pair.
        """
        trade_amount = min(entry_amount, exit_amount)
        
        if entry_side == 'buy':
            gross_pnl = (exit_price - entry_price) * trade_amount
        else:
            gross_pnl = (entry_price - exit_price) * trade_amount
        
        net_pnl = gross_pnl - entry_fee - exit_fee
        cost_basis = entry_price * trade_amount + entry_fee
        pnl_percentage = (net_pnl / cost_basis * 100) if cost_basis > 0 else 0.0
        
        return net_pnl, pnl_percentage

    def _group_fills_by_order(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        """
        Group individual fills by their order_id to reconstruct full orders.
        """
        orders = {}
        for fill in fills:
            oid = fill.order_id or f"manual_{fill.timestamp}_{fill.trade_id}"
            if oid not in orders:
                orders[oid] = {
                    'order_id': oid,
                    'symbol': fill.symbol,
                    'side': fill.side,
                    'amount': 0.0,
                    'price_sum': 0.0,
                    'cost': 0.0,
                    'fee': 0.0,
                    'timestamp': fill.timestamp,
                    'datetime': fill.datetime,
                    'fill_count': 0
                }
            
            o = orders[oid]
            o['amount'] += fill.amount
            o['cost'] += fill.cost
            o['fee'] += fill.fee
            o['fill_count'] += 1
            # Weighted average price
            if o['amount'] > 0:
                o['price'] = o['cost'] / o['amount']
            else:
                o['price'] = fill.price
            
            # Keep earliest timestamp for the order
            if fill.timestamp < o['timestamp']:
                o['timestamp'] = fill.timestamp
                o['datetime'] = fill.datetime
        
        return sorted(orders.values(), key=lambda x: x['timestamp'])

    def _format_trade_data(self, buy: Dict, sell: Dict, pnl_data: Tuple[float, float], amount: float = 0.0) -> Dict[str, Any]:
        """Helper to format matched trade data consistency."""
        net_pnl, pnl_percentage = pnl_data
        trade_amount = amount if amount > 0 else buy['amount']
        return {
            'symbol': self.symbol,
            'entry_side': 'buy',
            'entry_price': buy['price'],
            'entry_amount': trade_amount,
            'entry_fee': (trade_amount / buy['amount'] * buy['fee']) if amount and buy['amount'] > 0 else buy['fee'],
            'entry_timestamp': buy['timestamp'],
            'entry_datetime': buy['datetime'],
            'exit_side': 'sell',
            'exit_price': sell['price'],
            'exit_amount': trade_amount,
            'exit_fee': (trade_amount / sell['amount'] * sell['fee']) if amount and sell['amount'] > 0 else sell['fee'],
            'exit_timestamp': sell['timestamp'],
            'exit_datetime': sell['datetime'],
            'pnl_net': net_pnl,
            'pnl_percentage': pnl_percentage,
            'duration_seconds': abs(sell['timestamp'] - buy['timestamp']) // 1000
        }

    def match_trades(self, fills: List[Fill], strategy_name: str = "atomic_fifo") -> List[Dict[str, Any]]:
        """
        Main entry point for matching trades using a named strategy.
        """
        strategies = {
            "fifo": FIFOMatchStrategy(),
            "lifo": LIFOMatchStrategy(),
            "atomic_fifo": AtomicMatchStrategy(is_fifo=True),
            "atomic_lifo": AtomicMatchStrategy(is_fifo=False),
        }
        
        strategy = strategies.get(strategy_name.lower(), strategies["atomic_fifo"])
        return strategy.match(self, fills)

    def match_trades_fifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        """Legacy support for FIFO call, delegates to strategy."""
        return self.match_trades(fills, "fifo")

    def match_trades_lifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        """Legacy support for LIFO call, delegates to strategy."""
        return self.match_trades(fills, "lifo")
    
    def process_and_save_trades(self, strategy_name: str = "atomic_fifo") -> int:
        """
        Process all fills for the symbol and save matched trades to database.
        """
        with get_session_direct() as session:
            statement = select(Fill).where(Fill.symbol == self.symbol).order_by(Fill.timestamp)
            fills = session.exec(statement).all()
            
            if not fills:
                return 0
            
            # Use the new modular matching logic
            matched_trades = self.match_trades(fills, strategy_name)
            
            existing_trade_keys = set()
            existing_statement = select(Trade).where(Trade.symbol == self.symbol)
            existing_trades = session.exec(existing_statement).all()
            
            for existing in existing_trades:
                key = (
                    existing.entry_timestamp,
                    existing.exit_timestamp,
                    existing.entry_price,
                    existing.exit_price,
                    existing.entry_amount
                )
                existing_trade_keys.add(key)
            
            new_trades_count = 0
            for trade_data in matched_trades:
                key = (
                    trade_data['entry_timestamp'],
                    trade_data['exit_timestamp'],
                    trade_data['entry_price'],
                    trade_data['exit_price'],
                    trade_data['entry_amount']
                )
                
                if key not in existing_trade_keys:
                    trade = Trade(**trade_data)
                    session.add(trade)
                    new_trades_count += 1
            
            session.commit()
            return new_trades_count

    def compute_open_positions(self, logic: str = "atomic_fifo", fills: List[Fill] = None) -> List[Dict[str, Any]]:
        """
        Compute open (unmatched) positions using the same strategy as the main matching.
        Delegates to match_trades() to identify which orders were consumed, then
        reports the leftover buys (open longs) and orphan sells (sells without a prior buy).
        """
        if fills is None:
            with get_session_direct() as session:
                statement = select(Fill).where(Fill.symbol == self.symbol).order_by(Fill.timestamp)
                fills = list(session.exec(statement).all())

        # Run the same strategy to find matched trades
        matched_trades = self.match_trades(fills, logic)

        # Collect the entry/exit timestamps that were consumed in matches
        used_entry_timestamps = set()
        used_exit_timestamps = set()
        for t in matched_trades:
            used_entry_timestamps.add(t['entry_timestamp'])
            used_exit_timestamps.add(t['exit_timestamp'])

        # Group fills into orders (same as matching does internally)
        grouped_orders = self._group_fills_by_order(fills)
        buys = [o for o in grouped_orders if o['side'] == 'buy']
        sells = [o for o in grouped_orders if o['side'] == 'sell']

        open_positions = []

        # Unmatched buys → open long positions
        for b in buys:
            if b['timestamp'] not in used_entry_timestamps:
                open_positions.append({
                    'symbol': self.symbol,
                    'entry_side': 'buy',
                    'entry_price': b['price'],
                    'entry_amount': b['amount'],
                    'entry_fee': b['fee'],
                    'entry_timestamp': b['timestamp'],
                    'entry_datetime': b['datetime'],
                })

        # Unmatched sells → orphan sells (closed before history or data gap)
        for s in sells:
            if s['timestamp'] not in used_exit_timestamps:
                open_positions.append({
                    'symbol': self.symbol,
                    'entry_side': 'sell',
                    'entry_price': s['price'],
                    'entry_amount': s['amount'],
                    'entry_fee': s['fee'],
                    'entry_timestamp': s['timestamp'],
                    'entry_datetime': s['datetime'],
                    'is_orphan': True,  # Marker for UI
                })

        return open_positions
