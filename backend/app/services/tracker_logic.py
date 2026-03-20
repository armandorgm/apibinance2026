"""
Core business logic for FIFO trade matching and PnL calculation.
This is the heart of the system - matches buys and sells using FIFO algorithm.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime
from app.db.database import Fill, Trade, get_session_direct
from sqlmodel import select
from collections import deque
from typing import Optional


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
        
        Args:
            entry_price: Entry price
            entry_amount: Entry amount
            entry_fee: Entry fee
            exit_price: Exit price
            exit_amount: Exit amount
            exit_fee: Exit fee
            entry_side: 'buy' or 'sell'
            
        Returns:
            Tuple of (net_pnl, pnl_percentage)
        """
        # Use the minimum amount to handle partial fills
        trade_amount = min(entry_amount, exit_amount)
        
        if entry_side == 'buy':
            # Long position: profit when exit_price > entry_price
            gross_pnl = (exit_price - entry_price) * trade_amount
        else:
            # Short position: profit when exit_price < entry_price
            gross_pnl = (entry_price - exit_price) * trade_amount
        
        # Net PnL after deducting both entry and exit fees
        net_pnl = gross_pnl - entry_fee - exit_fee
        
        # Calculate percentage return
        cost_basis = entry_price * trade_amount + entry_fee
        pnl_percentage = (net_pnl / cost_basis * 100) if cost_basis > 0 else 0.0
        
        return net_pnl, pnl_percentage
    
    def match_trades_fifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        """
        Match fills using FIFO algorithm to create complete trades.
        
        Args:
            fills: List of Fill objects sorted by timestamp
            
        Returns:
            List of matched trade dictionaries ready for database storage
        """
        # Separate buys and sells
        buy_queue = deque()
        sell_queue = deque()
        
        matched_trades = []
        
        for fill in fills:
            if fill.side == 'buy':
                buy_queue.append(fill)
            else:
                sell_queue.append(fill)
            
            # Try to match while we have both buys and sells
            while buy_queue and sell_queue:
                buy = buy_queue[0]
                sell = sell_queue[0]
                
                # Determine which side is the entry
                if buy.timestamp <= sell.timestamp:
                    # Buy happened first (long position)
                    entry = buy
                    exit = sell
                    entry_side = 'buy'
                else:
                    # Sell happened first (short position)
                    entry = sell
                    exit = buy
                    entry_side = 'sell'
                
                # Calculate trade amount (handle partial fills)
                trade_amount = min(entry.amount, exit.amount)
                
                # Calculate PnL
                net_pnl, pnl_percentage = self.calculate_pnl(
                    entry_price=entry.price,
                    entry_amount=trade_amount,
                    entry_fee=entry.fee,
                    exit_price=exit.price,
                    exit_amount=trade_amount,
                    exit_fee=exit.fee,
                    entry_side=entry_side
                )
                
                # Calculate duration
                duration_seconds = abs(exit.timestamp - entry.timestamp) // 1000
                
                # Create trade record
                trade_data = {
                    'symbol': self.symbol,
                    'entry_side': entry.side,
                    'entry_price': entry.price,
                    'entry_amount': trade_amount,
                    'entry_fee': entry.fee,
                    'entry_timestamp': entry.timestamp,
                    'entry_datetime': entry.datetime,
                    'exit_side': exit.side,
                    'exit_price': exit.price,
                    'exit_amount': trade_amount,
                    'exit_fee': exit.fee,
                    'exit_timestamp': exit.timestamp,
                    'exit_datetime': exit.datetime,
                    'pnl_net': net_pnl,
                    'pnl_percentage': pnl_percentage,
                    'duration_seconds': duration_seconds
                }
                
                matched_trades.append(trade_data)
                
                # Update remaining amounts
                entry.amount -= trade_amount
                exit.amount -= trade_amount
                
                # Remove fully consumed fills
                if entry.amount <= 0.00000001:  # Small epsilon for float comparison
                    buy_queue.popleft() if entry.side == 'buy' else sell_queue.popleft()
                if exit.amount <= 0.00000001:
                    sell_queue.popleft() if exit.side == 'sell' else buy_queue.popleft()
        
        return matched_trades

    def match_trades_lifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        """
        Match fills using LIFO algorithm to create complete trades.
        """
        # Working on shallow copies to avoid mutating DB objects directly if passing DB objects
        class _FillCopy:
            def __init__(self, f: Fill):
                self.side = f.side
                self.price = f.price
                self.amount = float(f.amount)
                self.fee = float(f.fee or 0.0)
                self.timestamp = f.timestamp
                self.datetime = f.datetime

        buy_stack = []
        sell_stack = []
        
        matched_trades = []
        
        for f in fills:
            fc = _FillCopy(f)
            if fc.side == 'buy':
                buy_stack.append(fc)
            else:
                sell_stack.append(fc)
            
            while buy_stack and sell_stack:
                buy = buy_stack[-1]
                sell = sell_stack[-1]
                
                if buy.timestamp <= sell.timestamp:
                    entry = buy
                    exit = sell
                    entry_side = 'buy'
                else:
                    entry = sell
                    exit = buy
                    entry_side = 'sell'
                
                trade_amount = min(entry.amount, exit.amount)
                
                net_pnl, pnl_percentage = self.calculate_pnl(
                    entry_price=entry.price,
                    entry_amount=trade_amount,
                    entry_fee=entry.fee,
                    exit_price=exit.price,
                    exit_amount=trade_amount,
                    exit_fee=exit.fee,
                    entry_side=entry_side
                )
                
                duration_seconds = abs(exit.timestamp - entry.timestamp) // 1000
                
                trade_data = {
                    'symbol': self.symbol,
                    'entry_side': entry.side,
                    'entry_price': entry.price,
                    'entry_amount': trade_amount,
                    'entry_fee': entry.fee,
                    'entry_timestamp': entry.timestamp,
                    'entry_datetime': entry.datetime,
                    'exit_side': exit.side,
                    'exit_price': exit.price,
                    'exit_amount': trade_amount,
                    'exit_fee': exit.fee,
                    'exit_timestamp': exit.timestamp,
                    'exit_datetime': exit.datetime,
                    'pnl_net': net_pnl,
                    'pnl_percentage': pnl_percentage,
                    'duration_seconds': duration_seconds
                }
                
                matched_trades.append(trade_data)
                
                entry.amount -= trade_amount
                exit.amount -= trade_amount
                
                if entry.amount <= 0.00000001:
                    buy_stack.pop() if entry.side == 'buy' else sell_stack.pop()
                if exit.amount <= 0.00000001:
                    sell_stack.pop() if exit.side == 'sell' else buy_stack.pop()
        
        return matched_trades
    
    def process_and_save_trades(self) -> int:
        """
        Process all fills for the symbol and save matched trades to database.
        
        Returns:
            Number of new trades created
        """
        with get_session_direct() as session:
            # Fetch all fills for this symbol, sorted by timestamp
            statement = select(Fill).where(Fill.symbol == self.symbol).order_by(Fill.timestamp)
            fills = session.exec(statement).all()
            
            if not fills:
                return 0
            
            # Match trades using FIFO
            matched_trades = self.match_trades_fifo(fills)
            
            # Check which trades already exist to avoid duplicates
            existing_trade_keys = set()
            existing_statement = select(Trade).where(Trade.symbol == self.symbol)
            existing_trades = session.exec(existing_statement).all()
            
            for existing in existing_trades:
                key = (
                    existing.entry_timestamp,
                    existing.exit_timestamp,
                    existing.entry_price,
                    existing.exit_price
                )
                existing_trade_keys.add(key)
            
            # Save new trades
            new_trades_count = 0
            for trade_data in matched_trades:
                key = (
                    trade_data['entry_timestamp'],
                    trade_data['exit_timestamp'],
                    trade_data['entry_price'],
                    trade_data['exit_price']
                )
                
                if key not in existing_trade_keys:
                    trade = Trade(**trade_data)
                    session.add(trade)
                    new_trades_count += 1
            
            session.commit()
            return new_trades_count

    def compute_open_positions(self, logic: str = "fifo") -> List[Dict[str, Any]]:
        """Compute open (unmatched) positions for the current symbol using the given logic.

        Returns a list of dicts with remaining entry fills.
        """
        with get_session_direct() as session:
            statement = select(Fill).where(Fill.symbol == self.symbol).order_by(Fill.timestamp)
            fills = session.exec(statement).all()

        if logic.lower() == "fifo":
            return self._compute_open_positions_fifo(fills)
        else:
            return self._compute_open_positions_lifo(fills)

    def _compute_open_positions_fifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        buy_queue = deque()
        sell_queue = deque()

        # Work on shallow copies to avoid mutating DB objects
        class _FillCopy:
            def __init__(self, f: Fill):
                self.side = f.side
                self.price = f.price
                self.amount = float(f.amount)
                self.fee = float(f.fee or 0.0)
                self.timestamp = f.timestamp
                self.datetime = f.datetime

        for f in fills:
            fc = _FillCopy(f)
            if fc.side == 'buy':
                buy_queue.append(fc)
            else:
                sell_queue.append(fc)

            # match as we go
            while buy_queue and sell_queue:
                buy = buy_queue[0]
                sell = sell_queue[0]

                if buy.timestamp <= sell.timestamp:
                    entry = buy
                    exit = sell
                else:
                    entry = sell
                    exit = buy

                trade_amount = min(entry.amount, exit.amount)

                # reduce amounts
                entry.amount -= trade_amount
                exit.amount -= trade_amount

                if entry.amount <= 0.00000001:
                    if entry is buy:
                        buy_queue.popleft()
                    else:
                        sell_queue.popleft()
                if exit.amount <= 0.00000001:
                    if exit is sell:
                        sell_queue.popleft()
                    else:
                        buy_queue.popleft()

        # collect remaining open positions
        open_positions: List[Dict[str, Any]] = []
        for q in (buy_queue, sell_queue):
            for remaining in q:
                open_positions.append({
                    'symbol': self.symbol,
                    'entry_side': remaining.side,
                    'entry_price': remaining.price,
                    'entry_amount': remaining.amount,
                    'entry_fee': remaining.fee,
                    'entry_timestamp': remaining.timestamp,
                    'entry_datetime': remaining.datetime,
                })

        return open_positions

    def _compute_open_positions_lifo(self, fills: List[Fill]) -> List[Dict[str, Any]]:
        buy_stack = []
        sell_stack = []

        class _FillCopy:
            def __init__(self, f: Fill):
                self.side = f.side
                self.price = f.price
                self.amount = float(f.amount)
                self.fee = float(f.fee or 0.0)
                self.timestamp = f.timestamp
                self.datetime = f.datetime

        for f in fills:
            fc = _FillCopy(f)
            if fc.side == 'buy':
                buy_stack.append(fc)
            else:
                sell_stack.append(fc)

            while buy_stack and sell_stack:
                buy = buy_stack[-1]
                sell = sell_stack[-1]

                if buy.timestamp <= sell.timestamp:
                    entry = buy
                    exit = sell
                else:
                    entry = sell
                    exit = buy

                trade_amount = min(entry.amount, exit.amount)

                entry.amount -= trade_amount
                exit.amount -= trade_amount

                if entry.amount <= 0.00000001:
                    if entry is buy:
                        buy_stack.pop()
                    else:
                        sell_stack.pop()
                if exit.amount <= 0.00000001:
                    if exit is sell:
                        sell_stack.pop()
                    else:
                        buy_stack.pop()

        open_positions: List[Dict[str, Any]] = []
        for q in (buy_stack, sell_stack):
            for remaining in q:
                open_positions.append({
                    'symbol': self.symbol,
                    'entry_side': remaining.side,
                    'entry_price': remaining.price,
                    'entry_amount': remaining.amount,
                    'entry_fee': remaining.fee,
                    'entry_timestamp': remaining.timestamp,
                    'entry_datetime': remaining.datetime,
                })

        return open_positions
