"""
Core business logic for FIFO trade matching and PnL calculation.
This is the heart of the system - matches buys and sells using FIFO algorithm.
"""
from typing import List, Dict, Any, Tuple
from app.db.database import Fill, Trade, get_session_direct
from sqlmodel import select
from collections import deque


class TradeTracker:
    """
    Trade tracker supporting FIFO and LIFO logic.
    Matches buy and sell fills to calculate individual trade PnL.
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
    
    def match_trades_fifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        return self._match_trades(fills, is_fifo=True)

    def match_trades_lifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        return self._match_trades(fills, is_fifo=False)
        
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

    def _match_trades(self, fills: List[Fill], is_fifo: bool) -> List[Dict[str, Any]]:
        """
        Matches trades using Exact Match logic and Time Ordering (Buy must precede Sell).
        """
        grouped_orders = self._group_fills_by_order(fills)
        buys = [o for o in grouped_orders if o['side'] == 'buy']
        sells = [o for o in grouped_orders if o['side'] == 'sell']
        
        matched_trades = []
        used_buys = set() # Track indices of matched buys

        for sell in sells:
            # Find candidate buys that occurred BEFORE the sell and have the same amount
            candidates = []
            for i, buy in enumerate(buys):
                if i in used_buys:
                    continue
                
                # Rule: Buy must precede Sell
                if buy['timestamp'] >= sell['timestamp']:
                    continue
                
                # Rule: Exact Amount Match
                # Using a small epsilon for float comparison
                if abs(buy['amount'] - sell['amount']) < 1e-8:
                    candidates.append(i)
            
            if not candidates:
                continue # Unmatched sell
                
            # Selection logic:
            # FIFO: Earliest candidate buy
            # LIFO: Latest candidate buy
            if is_fifo:
                chosen_idx = candidates[0]
            else:
                chosen_idx = candidates[-1]
            
            buy = buys[chosen_idx]
            used_buys.add(chosen_idx)
            
            net_pnl, pnl_percentage = self.calculate_pnl(
                entry_price=buy['price'],
                entry_amount=buy['amount'],
                entry_fee=buy['fee'],
                exit_price=sell['price'],
                exit_amount=sell['amount'],
                exit_fee=sell['fee'],
                entry_side='buy'
            )
            
            duration_seconds = abs(sell['timestamp'] - buy['timestamp']) // 1000
            
            trade_data = {
                'symbol': self.symbol,
                'entry_side': 'buy',
                'entry_price': buy['price'],
                'entry_amount': buy['amount'],
                'entry_fee': buy['fee'],
                'entry_timestamp': buy['timestamp'],
                'entry_datetime': buy['datetime'],
                'exit_side': 'sell',
                'exit_price': sell['price'],
                'exit_amount': sell['amount'],
                'exit_fee': sell['fee'],
                'exit_timestamp': sell['timestamp'],
                'exit_datetime': sell['datetime'],
                'pnl_net': net_pnl,
                'pnl_percentage': pnl_percentage,
                'duration_seconds': duration_seconds
            }
            matched_trades.append(trade_data)

        return matched_trades
    
    def process_and_save_trades(self) -> int:
        """
        Process all fills for the symbol and save matched trades to database.
        """
        with get_session_direct() as session:
            statement = select(Fill).where(Fill.symbol == self.symbol).order_by(Fill.timestamp)
            fills = session.exec(statement).all()
            
            if not fills:
                return 0
            
            matched_trades = self.match_trades_fifo(fills)
            
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

    def compute_open_positions(self, logic: str = "fifo", fills: List[Fill] = None) -> List[Dict[str, Any]]:
        """Compute open (unmatched) positions for the current symbol using the given logic."""
        if fills is None:
            with get_session_direct() as session:
                statement = select(Fill).where(Fill.symbol == self.symbol).order_by(Fill.timestamp)
                fills = session.exec(statement).all()

        is_fifo = logic.lower() == "fifo"
        
        grouped_orders = self._group_fills_by_order(fills)
        buys = [o for o in grouped_orders if o['side'] == 'buy']
        sells = [o for o in grouped_orders if o['side'] == 'sell']
        
        used_buys = set()
        used_sells = set()

        # Re-run matching logic just to identify which are unmatched
        for s_idx, sell in enumerate(sells):
            candidates = []
            for b_idx, buy in enumerate(buys):
                if b_idx in used_buys:
                    continue
                if buy['timestamp'] < sell['timestamp'] and abs(buy['amount'] - sell['amount']) < 1e-8:
                    candidates.append(b_idx)
            
            if candidates:
                chosen_idx = candidates[0] if is_fifo else candidates[-1]
                used_buys.add(chosen_idx)
                used_sells.add(s_idx)
                    
        open_positions = []
        for i, b in enumerate(buys):
            if i not in used_buys:
                open_positions.append({
                    'symbol': self.symbol,
                    'entry_side': 'buy',
                    'entry_price': b['price'],
                    'entry_amount': b['amount'],
                    'entry_fee': b['fee'],
                    'entry_timestamp': b['timestamp'],
                    'entry_datetime': b['datetime'],
                })
            
        for i, s in enumerate(sells):
            if i not in used_sells:
                open_positions.append({
                    'symbol': self.symbol,
                    'entry_side': 'sell',
                    'entry_price': s['price'],
                    'entry_amount': s['amount'],
                    'entry_fee': s['fee'],
                    'entry_timestamp': s['timestamp'],
                    'entry_datetime': s['datetime'],
                    'is_orphan': True # Marker for UI
                })

        return open_positions
