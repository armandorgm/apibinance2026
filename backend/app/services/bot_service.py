"""
Automated Bot Service.
Runs the strategy engine in a background loop and executes orders.
"""
import asyncio
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import select, Session

from app.core.config import settings
from app.core.exchange import exchange_manager
from app.db.database import engine, BotSignal, Fill, Trade, BotConfig
from app.services.strategy_engine import StrategyEngine, TradingContext, RuleActionResult


class TradingBot:
    def __init__(self):
        self.engine = StrategyEngine()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_run_status: Dict[str, Any] = {"status": "inactive"}

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        print(f"[BOT] Started")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("[BOT] Stopped")

    async def _run_loop(self):
        while self.is_running:
            try:
                await self.evaluate_and_execute()
            except Exception as e:
                print(f"[BOT] Error in loop: {e}")
                traceback.print_exc()
            
            # Dynamic sleep based on config
            with Session(engine) as session:
                statement = select(BotConfig)
                config = session.exec(statement).first()
                sleep_time = config.interval if config else settings.BOT_INTERVAL
                
            await asyncio.sleep(sleep_time)

    async def evaluate_and_execute(self):
        # 0. Get Config from DB
        with Session(engine) as session:
            statement = select(BotConfig)
            config = session.exec(statement).first()
            
            if not config or not config.is_enabled:
                # Bot is disabled in DB, skip execution
                return

            symbol = config.symbol
            trade_amount = config.trade_amount
            
        # Normalize symbol (e.g. 1000PEPEUSDC -> PEPE/USDT:USDT)
        symbol = await exchange_manager.normalize_symbol(symbol)
            
        print(f"[BOT] Evaluating {symbol} at {datetime.utcnow()}")
        
        # 1. Gather Context
        context = await self._gather_context(symbol)
        
        # 2. Evaluate Rules
        result = self.engine.evaluate(context)
        
        # 3. Log Activity and Execute if needed
        await self._process_result(symbol, trade_amount, result, context)
        
        self.last_run_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "rule_triggered": result.rule_name,
            "action": result.action,
            "context": context.model_dump()
        }

    async def _gather_context(self, symbol: str) -> TradingContext:
        # Get active positions from exchange
        positions = await exchange_manager.get_open_positions(symbol)
        active_count = len(positions)
        
        # Get last purchase time from database fills
        with Session(engine) as session:
            statement = select(Fill).where(Fill.symbol == symbol, Fill.side == 'buy').order_by(Fill.timestamp.desc()).limit(1)
            last_fill = session.exec(statement).first()
            last_time = last_fill.timestamp if last_fill else int((datetime.utcnow().timestamp() - 86400*2) * 1000) # Default to 2 days ago if none

        # Mocking last_range for now as it's not persisted yet
        # In a real app, this would come from a 'Settings' or 'State' table
        last_range = [1.0, 4.0] 

        return TradingContext(
            last_purchase_time=last_time,
            active_trades_count=active_count,
            last_range=last_range
        )

    async def _process_result(self, symbol: str, trade_amount: float, result: RuleActionResult, context: TradingContext):
        if not result.trigger:
            return

        print(f"[BOT] TRIGGER: {result.rule_name} -> Action: {result.action}")
        
        success = True
        error_msg = None
        exchange_req = None
        exchange_res = None
        
        try:
            if result.action == "NEW_ORDER":
                # Execute market buy using the configured trade_amount
                exchange_req = json.dumps({
                    "symbol": symbol,
                    "side": "buy",
                    "amount": trade_amount,
                    "order_type": "market"
                })
                
                order_response = await exchange_manager.create_order(
                    symbol=symbol,
                    side="buy",
                    amount=trade_amount,
                    order_type="market"
                )
                # Capture the response from the exchange
                exchange_res = json.dumps(order_response)
            elif result.action == "UPDATE_RANGE":
                # Logic for updating range (e.g. updating a DB setting or internal state)
                print(f"[BOT] Updating range to {result.params.get('new_range')}")
        except Exception as e:
            success = False
            # Better error capturing for CCXT/Binance exceptions
            error_msg = str(e)
            
            # Try to extract the JSON response from CCXT exceptions if present
            if hasattr(e, 'response') and e.response:
                try:
                    exchange_res = json.dumps(e.response)
                except:
                    pass
            elif hasattr(e, 'body') and e.body:
                try:
                    # Sometimes the body is a string that can be parsed as JSON
                    exchange_res = e.body if isinstance(e.body, str) else json.dumps(e.body)
                except:
                    pass
            
            print(f"[BOT] EXECUTION ERROR: {error_msg}")

        # Save to database
        with Session(engine) as session:
            signal = BotSignal(
                symbol=symbol,
                rule_triggered=result.rule_name,
                action_taken=result.action,
                params_snapshot=json.dumps(result.params) if result.params else None,
                exchange_request=exchange_req,
                exchange_response=exchange_res,
                success=success,
                error_message=error_msg
            )
            session.add(signal)
            session.commit()


# Global bot instance
bot_instance = TradingBot()
