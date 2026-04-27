import pytest
from unittest.mock import AsyncMock, patch
from app.services.scheduled_scaler_bot import ScheduledScalerBot


@pytest.mark.asyncio
async def test_infer_side_and_tp_shuts_down_when_leverage_missing():
    bot = ScheduledScalerBot()

    class DummyEngine:
        pass

    engine = DummyEngine()
    engine.get_position_risk = AsyncMock(return_value=[{
        "symbol": "BTCUSDT",
        "leverage": None,
        "notional": 0.0,
        "initialMargin": 0.0,
        "positionAmt": 1.0,
        "markPrice": 100.0,
    }])

    with patch("app.core.exchange.exchange_manager.get_native_symbol", return_value="BTCUSDT"):
        with pytest.raises(SystemExit) as exc:
            await bot._infer_side_and_tp("BTC/USDT:USDT", engine)

    assert "Unable to determine leverage" in str(exc.value)
