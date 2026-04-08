import asyncio
import json
from unittest.mock import AsyncMock, patch
from app.services.bot_service import bot_instance
from app.services.strategy_engine import RuleActionResult
from app.services.bot_service import TradingContext
from app.db.database import get_session_direct, BotSignal
from sqlmodel import select

async def test_successful_order_logging():
    print("\n--- Testing Successful Order Logging ---")
    mock_response = {"id": "12345", "status": "closed", "symbol": "BTC/USDT"}
    
    with patch("app.core.exchange.exchange_manager.create_order", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        # Manually call _process_result
        result = RuleActionResult(
            trigger=True,
            rule_name="TEST_SUCCESS",
            action="NEW_ORDER",
            params={"test": True}
        )
        context = TradingContext(last_purchase_time=0, active_trades_count=0, last_range=[0,0])
        
        await bot_instance._process_result("BTC/USDT", result, context)
        
        # Verify DB
        with get_session_direct() as session:
            statement = select(BotSignal).where(BotSignal.rule_triggered == "TEST_SUCCESS").order_by(BotSignal.created_at.desc()).limit(1)
            signal = session.exec(statement).first()
            
            if signal:
                print(f"Signal ID: {signal.id}")
                print(f"Request: {signal.exchange_request}")
                print(f"Response: {signal.exchange_response}")
                print(f"Success: {signal.success}")
                
                req_json = json.loads(signal.exchange_request)
                res_json = json.loads(signal.exchange_response)
                
                if req_json["symbol"] == "BTC/USDT" and res_json["id"] == "12345":
                    print("SUCCESS: JSON strings are valid and match.")
                else:
                    print("FAILURE: JSON content mismatch.")
            else:
                print("FAILURE: Signal not found in DB.")

async def test_error_order_logging():
    print("\n--- Testing Error Order Logging ---")
    
    with patch("app.core.exchange.exchange_manager.create_order", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("Simulated Binance Error")
        
        # Manually call _process_result
        result = RuleActionResult(
            trigger=True,
            rule_name="TEST_ERROR",
            action="NEW_ORDER",
            params={"test": True}
        )
        context = TradingContext(last_purchase_time=0, active_trades_count=0, last_range=[0,0])
        
        await bot_instance._process_result("BTC/USDT", result, context)
        
        # Verify DB
        with get_session_direct() as session:
            statement = select(BotSignal).where(BotSignal.rule_triggered == "TEST_ERROR").order_by(BotSignal.created_at.desc()).limit(1)
            signal = session.exec(statement).first()
            
            if signal:
                print(f"Signal ID: {signal.id}")
                print(f"Request: {signal.exchange_request}")
                print(f"Response: {signal.exchange_response}")
                print(f"Success: {signal.success}")
                print(f"Error: {signal.error_message}")
                
                if signal.exchange_request and "BTC/USDT" in signal.exchange_request:
                    print("SUCCESS: exchange_request logged even on error.")
                else:
                    print("FAILURE: exchange_request is missing on error.")
                    
                if signal.exchange_response is None:
                    print("SUCCESS: exchange_response is null as expected on hard exception.")
            else:
                print("FAILURE: Signal not found in DB.")

if __name__ == "__main__":
    asyncio.run(test_successful_order_logging())
    asyncio.run(test_error_order_logging())
