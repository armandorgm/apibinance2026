from typing import List, Union, Any
from abc import ABC, abstractmethod

def _get_field(item: Any, field: str) -> Any:
    """Helper to safely get a field from either a dict or an object/Pydantic model."""
    if isinstance(item, dict):
        return item.get(field)
    return getattr(item, field)


class TradeSorterStrategy(ABC):
    """
    Abstract Strategy to sort a unified list of closed and unrealized trades.
    Follows OCP (Open/Closed Principle).
    """
    @abstractmethod
    def sort(self, trades: List[Any]) -> List[Any]:
        pass

class SortByEntryDateDesc(TradeSorterStrategy):
    """Sorts trades chronologicaly descending (most recent first)"""
    def sort(self, trades: List[Any]) -> List[Any]:
        return sorted(trades, key=lambda x: _get_field(x, 'entry_datetime'), reverse=True)

class SortByEntryDateAsc(TradeSorterStrategy):
    """Sorts trades chronologicaly ascending (oldest first)"""
    def sort(self, trades: List[Any]) -> List[Any]:
        return sorted(trades, key=lambda x: _get_field(x, 'entry_datetime'), reverse=False)

class SortByPnLDesc(TradeSorterStrategy):
    """Sorts trades by their Net PnL (highest profit first)"""
    def sort(self, trades: List[Any]) -> List[Any]:
        return sorted(trades, key=lambda x: _get_field(x, 'pnl_net'), reverse=True)


class HistoryFormatter:
    """
    Context class that uses a TradeSorterStrategy for ordering.
    Follows SRP for presentation layer.
    """
    def __init__(self, sorter: TradeSorterStrategy = None):
        self.sorter = sorter or SortByEntryDateDesc()

    def set_sorter(self, sorter: TradeSorterStrategy):
        self.sorter = sorter

    def format_and_sort(self, closed_trades: List[Any], open_trades: List[Any]) -> List[Any]:
        """Combines closed and open trades uniformly, then applies the sorting strategy."""
        combined = closed_trades + open_trades
        return self.sorter.sort(combined)

class TradeResponseFormatter(HistoryFormatter):
    """
    Legacy wrapper for compatibility handling TradeResponse objects.
    Now purely delegates to parent.
    """
    pass

