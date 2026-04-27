"""
Test for the /sync endpoint — verifies that ExchangeManager.fetch_my_trades
exists and is callable, which is the prerequisite for the "Sincronizar con Binance"
button to function without AttributeError.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.exchange import ExchangeManager


class TestExchangeManagerFetchMyTrades:
    """Verifies ExchangeManager exposes fetch_my_trades as a public method."""

    def test_fetch_my_trades_method_exists(self):
        """The sync button calls exchange_manager.fetch_my_trades().
        This test fails if the method is missing (AttributeError)."""
        em = ExchangeManager()
        assert hasattr(em, "fetch_my_trades"), (
            "ExchangeManager is missing 'fetch_my_trades'. "
            "The /sync endpoint and sync button depend on this method."
        )

    def test_fetch_my_trades_is_coroutine(self):
        """fetch_my_trades must be async (awaitable) since routes.py awaits it."""
        import asyncio
        em = ExchangeManager()
        assert hasattr(em, "fetch_my_trades"), "Method missing — cannot check if async."
        assert asyncio.iscoroutinefunction(em.fetch_my_trades), (
            "fetch_my_trades must be an async method."
        )

    @pytest.mark.asyncio
    async def test_fetch_my_trades_delegates_to_ccxt(self):
        """Ensures fetch_my_trades correctly delegates to the CCXT exchange instance."""
        em = ExchangeManager()

        mock_exchange = AsyncMock()
        mock_exchange.fetch_my_trades = AsyncMock(return_value=[
            {"id": "1", "symbol": "BTC/USDT", "side": "buy", "amount": 0.01, "price": 50000}
        ])
        # Also mock load_markets and markets for normalize_symbol
        mock_exchange.load_markets = AsyncMock()
        mock_exchange.markets = {"BTC/USDT:USDT": {"id": "BTCUSDT", "symbol": "BTC/USDT:USDT"}}

        with patch.object(em, "get_exchange", return_value=mock_exchange):
            result = await em.fetch_my_trades("BTC/USDT:USDT", since=1000)
            assert len(result) == 1
            mock_exchange.fetch_my_trades.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_my_trades_accepts_params(self):
        """The /sync/historical endpoint passes extra params like endTime."""
        em = ExchangeManager()

        mock_exchange = AsyncMock()
        mock_exchange.fetch_my_trades = AsyncMock(return_value=[])
        mock_exchange.load_markets = AsyncMock()
        mock_exchange.markets = {}

        with patch.object(em, "get_exchange", return_value=mock_exchange):
            result = await em.fetch_my_trades(
                "BTC/USDT:USDT", since=1000, params={"endTime": 2000}
            )
            assert result == []

    @pytest.mark.asyncio
    async def test_check_margin_availability_terminates_backend_when_leverage_missing(self):
        """If leverage cannot be determined, the backend must shutdown via SystemExit."""
        em = ExchangeManager()
        em._native = MagicMock()
        em._native.get_available_balance = AsyncMock(return_value=1000.0)
        em._native.get_position_risk = AsyncMock(return_value=[])

        mock_exchange = AsyncMock()
        mock_exchange.fetch_positions = AsyncMock(return_value=[{"leverage": None}])

        em.get_market_id = AsyncMock(return_value="BTCUSDT")
        with patch.object(em, "get_exchange", return_value=mock_exchange):
            with pytest.raises(SystemExit) as exc:
                await em.check_margin_availability("BTCUSDT", notional_usd=10)

        assert "Leverage detection failed" in str(exc.value)
