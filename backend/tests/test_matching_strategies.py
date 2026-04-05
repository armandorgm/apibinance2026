"""
Tests parametrizados para las estrategias de matching (FIFO, LIFO, Atomic FIFO, Atomic LIFO).
Carpeta espejo: tests/ -> backend/app/services/tracker_logic.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from datetime import datetime
from app.services.tracker_logic import TradeTracker, FIFOMatchStrategy, LIFOMatchStrategy, AtomicMatchStrategy
from app.db.database import Fill

BASE_TS = 1700000000000  # arbitrary base timestamp in ms

def make_fill(tid, side, amount, price, ts_offset, order_id=None, **kwargs):
    ts = BASE_TS + ts_offset
    fill = Fill(
        trade_id=tid,
        symbol="TEST/USDT",
        side=side,
        amount=amount,
        price=price,
        cost=amount * price,
        fee=round(amount * price * 0.001, 6),
        fee_currency="USDT",
        timestamp=ts,
        datetime=datetime.fromtimestamp(ts / 1000),
        order_id=order_id or tid,
    )
    # Extra metadata (not saved to DB in tests)
    for k, v in kwargs.items():
        object.__setattr__(fill, k, v)
    return fill


class TestExactMatch:
    """Escenario 1: buy == sell en cantidad exacta → todos matchean."""

    def _exact_fills(self):
        return [
            make_fill("b1", "buy",  1.0, 100.0,    0, "buy_order_1"),
            make_fill("s1", "sell", 1.0, 120.0, 1000, "sell_order_1"),
        ]

    @pytest.mark.parametrize("strategy", ["fifo", "lifo", "atomic_fifo", "atomic_lifo"])
    def test_exact_match_all_strategies(self, strategy):
        tracker = TradeTracker("TEST/USDT")
        trades = tracker.match_trades(self._exact_fills(), strategy)
        assert len(trades) == 1, f"[{strategy}] Expected 1 trade, got {len(trades)}"
        t = trades[0]
        assert t['entry_price'] == 100.0
        assert t['exit_price'] == 120.0
        assert t['pnl_net'] > 0, "Long trade with positive pnl expected"


class TestPartialMatch:
    """
    Escenario 2: buy=2.0, sell=1.0 (cantidad diferente).
    FIFO/LIFO deben producir 1 trade parcial; Atomic NO debe producir ninguno.
    """

    def _partial_fills(self):
        return [
            make_fill("b1", "buy",  2.0, 100.0,    0, "buy_order_big"),
            make_fill("s1", "sell", 1.0, 120.0, 1000, "sell_order_partial"),
        ]

    @pytest.mark.parametrize("strategy", ["fifo", "lifo"])
    def test_partial_match_fifo_lifo(self, strategy):
        tracker = TradeTracker("TEST/USDT")
        trades = tracker.match_trades(self._partial_fills(), strategy)
        assert len(trades) == 1, f"[{strategy}] Expected 1 partial trade, got {len(trades)}"
        assert trades[0]['entry_amount'] == 1.0, "Matched amount should be 1.0 (partial)"

    @pytest.mark.parametrize("strategy", ["atomic_fifo", "atomic_lifo"])
    def test_no_match_atomic_on_partial(self, strategy):
        tracker = TradeTracker("TEST/USDT")
        trades = tracker.match_trades(self._partial_fills(), strategy)
        assert len(trades) == 0, f"[{strategy}] Atomic should NOT match partial qty, got {len(trades)}"


class TestNoMatchSellBeforeBuy:
    """Escenario 3: sell ocurre antes que buy → ninguna estrategia debe matchear."""

    def _inverted_fills(self):
        return [
            make_fill("s1", "sell", 1.0, 120.0,    0, "sell_early"),
            make_fill("b1", "buy",  1.0, 100.0, 1000, "buy_late"),
        ]

    @pytest.mark.parametrize("strategy", ["fifo", "lifo", "atomic_fifo", "atomic_lifo"])
    def test_no_match_when_sell_before_buy(self, strategy):
        tracker = TradeTracker("TEST/USDT")
        trades = tracker.match_trades(self._inverted_fills(), strategy)
        assert len(trades) == 0, f"[{strategy}] Should not match sell-before-buy, got {len(trades)}"


class TestFIFOvsLIFOOrder:
    """
    FIFO debe usar el buy más antiguo; LIFO debe usar el buy más reciente.
    Setup: 2 buys a precios distintos, 1 sell parcial que cubre solo 1 buy.
    """

    def _two_buys_one_sell(self):
        return [
            make_fill("b1", "buy",  1.0,  90.0,    0, "buy_old"),  # FIFO elegirá este
            make_fill("b2", "buy",  1.0, 110.0, 1000, "buy_new"),  # LIFO elegirá este
            make_fill("s1", "sell", 1.0, 130.0, 2000, "sell_1"),
        ]

    def test_fifo_picks_oldest_buy(self):
        tracker = TradeTracker("TEST/USDT")
        trades = tracker.match_trades(self._two_buys_one_sell(), "fifo")
        assert len(trades) == 1
        assert trades[0]['entry_price'] == 90.0, f"FIFO should pick oldest buy (90), got {trades[0]['entry_price']}"

    def test_lifo_picks_newest_buy(self):
        tracker = TradeTracker("TEST/USDT")
        trades = tracker.match_trades(self._two_buys_one_sell(), "lifo")
        assert len(trades) == 1
        assert trades[0]['entry_price'] == 110.0, f"LIFO should pick newest buy (110), got {trades[0]['entry_price']}"


class TestOpenPositions:
    """Verificar que compute_open_positions respeta la estrategia."""

    def _fills_with_open(self):
        return [
            make_fill("b1", "buy",  1.0,  90.0,    0, "buy_old"),
            make_fill("b2", "buy",  1.0, 110.0, 1000, "buy_new"),
            make_fill("s1", "sell", 1.0, 130.0, 2000, "sell_1"),
        ]

    def test_fifo_leaves_correct_open(self):
        tracker = TradeTracker("TEST/USDT")
        fills = self._fills_with_open()
        open_pos = tracker.compute_open_positions(logic="fifo", fills=fills)
        open_buys = [p for p in open_pos if p['entry_side'] == 'buy']
        assert len(open_buys) == 1
        # FIFO consumed b1 (90), so b2 (110) remains open
        assert open_buys[0]['entry_price'] == 110.0, "FIFO should leave buy@110 open"

    def test_lifo_leaves_correct_open(self):
        tracker = TradeTracker("TEST/USDT")
        fills = self._fills_with_open()
        open_pos = tracker.compute_open_positions(logic="lifo", fills=fills)
        open_buys = [p for p in open_pos if p['entry_side'] == 'buy']
        assert len(open_buys) == 1
        # LIFO consumed b2 (110), so b1 (90) remains open
        assert open_buys[0]['entry_price'] == 90.0, "LIFO should leave buy@90 open"


class TestOriginCentricRules:
    """Escenario: Órdenes que NO pueden ser entrada (es decir, AlgoOrders)."""

    def test_algo_order_cannot_be_entry(self):
        tracker = TradeTracker("TEST/USDT")
        fills = [
            # Una compra que es ALGO (Stop Loss Inverso o similar) o simplemente marcada como no-entrada
            make_fill("b1", "buy",  1.0, 100.0,    0, "buy_algo", can_be_entry=False, originator="AUTO_ALGO"),
            make_fill("s1", "sell", 1.0, 120.0, 1000, "sell_1"),
        ]
        
        # Ninguna estrategia debería matchear b1 con s1 porque b1 no es entrada válida
        for strategy in ["fifo", "lifo", "atomic_fifo"]:
            trades = tracker.match_trades(fills, strategy)
            assert len(trades) == 0, f"[{strategy}] Algo order should NOT be an entry candidate"

    def test_manual_order_can_be_entry(self):
        tracker = TradeTracker("TEST/USDT")
        fills = [
            make_fill("b1", "buy",  1.0, 100.0,    0, "buy_manual", can_be_entry=True, originator="MANUAL"),
            make_fill("s1", "sell", 1.0, 120.0, 1000, "sell_1"),
        ]
        
        trades = tracker.match_trades(fills, "fifo")
        assert len(trades) == 1, "Manual order SHOULD be an entry candidate"
        assert trades[0]['originator'] == "MANUAL"
