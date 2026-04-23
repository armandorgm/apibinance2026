"""
Automated Bot Service.
Runs the PipelineEngine in a background loop.
"""
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import select, Session

from app.core.config import settings
from app.core.exchange import exchange_manager
from app.db.database import engine, BotConfig
from app.services.strategy_engine import PipelineEngine


class TradingBot:
    def __init__(self):
        self.engine = PipelineEngine()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_run_status: Dict[str, Any] = {"status": "inactive"}

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        
        # Start Stream listener (Orders logic in background)
        from app.core.stream_service import stream_manager
        await stream_manager.start()
        await stream_manager.recover_active_subscriptions()
        
        self._task = asyncio.create_task(self._run_loop())
        print(f"[BOT] Started Pipeline Engine, Stream Service & Recovery")

    async def stop(self):
        self.is_running = False
        
        # Stop Stream listener
        from app.core.stream_service import stream_manager
        await stream_manager.stop()
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("[BOT] Stopped Pipeline Engine & Stream Service")


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
                return

            symbol = config.symbol
            
        symbol = await exchange_manager.normalize_symbol(symbol)
            
        # 1. Gather global minimal context (e.g., current price for general logging or offset)
        try:
            ticker = await exchange_manager.fetch_ticker(symbol)
            current_price = ticker.get('last', 0.0)
        except Exception as e:
            current_price = 0.0

        # print(f"[BOT] Evaluating Pipelines for {symbol} at {datetime.utcnow()}")
        
        # 2. Evaluate and Execute Rules
        results = await self.engine.evaluate_and_execute(symbol, float(current_price))
        
        self.last_run_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "actions_executed": len(results),
            "results": results
        }

    async def evaluate_stream_tick(self, symbol: str, current_price: float):
        """Called directly by the StreamManager when a new tick is received."""
        # Use PipelineEngine to specifically process ON_TICK or CHASE pipelines
        # Currently, Action handles its own chase logic so we route it through engine.
        from app.services.strategy_engine import PipelineEngine
        try:
            await self.engine.evaluate_stream_event(symbol, current_price=current_price)
        except Exception as e:
            print(f"[BOT] Error evaluating stream tick: {e}")

    async def evaluate_stream_order(self, order_data: Dict[str, Any]):
        """Called directly by the StreamManager when an order updates."""
        try:
            await self.engine.evaluate_stream_order(order_data)
        except Exception as e:
            print(f"[BOT] Error evaluating stream order update: {e}")

# Global bot instance
bot_instance = TradingBot()

