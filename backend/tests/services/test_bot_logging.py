import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.strategy_engine import PipelineEngine
from app.db.database import BotPipeline, BotSignal

@pytest.mark.asyncio
async def test_successful_order_logging_via_engine(session):
    """
    Verifica que el PipelineEngine registre correctamente en BotSignal 
    cuando una acción de una regla se ejecuta con éxito.
    """
    engine = PipelineEngine()
    symbol = "BTC/USDT"
    
    # 1. Configuramos una Pipeline de prueba en la DB en memoria
    pipeline = BotPipeline(
        name="TEST_SUCCESS_RULE",
        symbol=symbol,
        is_active=True,
        trigger_event="POLLING",
        pipeline_config=json.dumps({
            "condition": {"provider_a": "PRICE", "operator": "GT", "provider_b": "0"},
            "action": {"type": "BUY_MIN_NOTIONAL"}
        })
    )
    session.add(pipeline)
    session.commit()

    # 2. Mockeamos el evaluador para que siempre dispare la regla
    # y la acción para que devuelva éxito.
    with patch("app.services.strategy_engine.RelationalEvaluator.evaluate", new_callable=AsyncMock) as mock_eval, \
         patch("app.services.strategy_engine.ACTIONS") as mock_actions:
        
        mock_eval.return_value = True
        
        mock_exec = AsyncMock()
        mock_exec.execute.return_value = {
            "success": True, 
            "result": {"id": "order_123", "status": "filled"}
        }
        mock_actions.get.return_value = mock_exec
        
        # 3. Ejecutamos la evaluación (esto debería disparar el logging en strategy_engine.py)
        await engine.evaluate_and_execute(symbol, 50000.0)
        
        # 4. Verificamos la persistencia de la señal
        # Refrescamos la sesión para ver los cambios del engine
        session.expire_all()
        signal = session.query(BotSignal).filter(BotSignal.rule_triggered == "TEST_SUCCESS_RULE").first()
        
        assert signal is not None
        assert signal.success is True
        assert "order_123" in signal.exchange_response
        assert signal.action_taken == "BUY_MIN_NOTIONAL"

@pytest.mark.asyncio
async def test_error_order_logging_via_engine(session):
    """Verifica que el PipelineEngine registre el fallo en BotSignal si la acción falla."""
    engine = PipelineEngine()
    symbol = "ETH/USDT"
    
    pipeline = BotPipeline(
        name="TEST_ERROR_RULE",
        symbol=symbol,
        is_active=True,
        trigger_event="POLLING",
        pipeline_config=json.dumps({
            "condition": {"provider_a": "PRICE", "operator": "GT", "provider_b": "0"},
            "action": {"type": "BUY_MIN_NOTIONAL"}
        })
    )
    session.add(pipeline)
    session.commit()

    with patch("app.services.strategy_engine.RelationalEvaluator.evaluate", new_callable=AsyncMock) as mock_eval, \
         patch("app.services.strategy_engine.ACTIONS") as mock_actions:
        
        mock_eval.return_value = True
        
        mock_exec = AsyncMock()
        mock_exec.execute.return_value = {
            "success": False, 
            "error": "Insufficient Funds"
        }
        mock_actions.get.return_value = mock_exec
        
        await engine.evaluate_and_execute(symbol, 2000.0)
        
        session.expire_all()
        signal = session.query(BotSignal).filter(BotSignal.rule_triggered == "TEST_ERROR_RULE").first()
        
        assert signal is not None
        assert signal.success is False
        assert signal.error_message == "Insufficient Funds"
