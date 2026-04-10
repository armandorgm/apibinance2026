"""
CCXT Pro WebSocket Streaming Service for high-frequency chasing.
"""
import asyncio
import ccxt.pro as ccxt
import traceback
from typing import Dict, Any, Optional, Set
from app.core.config import settings

class StreamManager:
    """
    Manages dynamic WebSocket subscriptions to Binance Futures.
    Reacts to ticks and order updates instantly without polling delays.
    """
    def __init__(self):
        self.exchange: Optional[ccxt.binance] = None
        self.subscribed_symbols: Set[str] = set()
        self._watch_tasks: Dict[str, asyncio.Task] = {}
        self._orders_task: Optional[asyncio.Task] = None
        self.is_running = False

    async def get_exchange(self) -> ccxt.binance:
        if self.exchange is None:
            api_key = settings.BINANCE_API_KEY or ""
            api_secret = settings.BINANCE_API_SECRET or ""
            
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                },
                'sandbox': settings.TESTNET,
            })
        return self.exchange

    async def start(self):
        """Starts the connection and generic order listener."""
        if self.is_running:
            return
        self.is_running = True
        self._orders_task = asyncio.create_task(self._watch_orders_loop())
        print("[STREAM] StreamManager generic orders listener started.")

    async def stop(self):
        self.is_running = False
        for task in self._watch_tasks.values():
            task.cancel()
        if self._orders_task:
            self._orders_task.cancel()
        
        if self.exchange:
            await self.exchange.close()
            self.exchange = None
        print("[STREAM] StreamManager stopped.")

    def subscribe(self, symbol: str):
        """Request the engine to start watching ticks for a symbol."""
        if symbol in self.subscribed_symbols:
            return
        self.subscribed_symbols.add(symbol)
        task = asyncio.create_task(self._watch_ticker_loop(symbol))
        self._watch_tasks[symbol] = task
        print(f"[STREAM] Subscribed to ticker stream for {symbol}")

    def unsubscribe(self, symbol: str):
        """Cut the stream for a symbol when no longer needed."""
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
            task = self._watch_tasks.pop(symbol, None)
            if task:
                task.cancel()
            print(f"[STREAM] Unsubscribed from ticker stream for {symbol}")

    async def _watch_ticker_loop(self, symbol: str):
        """Background coroutine receiving ticks for the given symbol."""
        exchange = await self.get_exchange()
        while self.is_running and symbol in self.subscribed_symbols:
            try:
                # CCXT watchTicker streams live data
                ticker = await exchange.watch_ticker(symbol)
                # print(f"[STREAM] Tick received for {symbol}: {ticker.get('last')}")
                
                # Trigger Pipeline Engine Evaluation for the specific Chase process!
                from app.services.bot_service import bot_instance
                await bot_instance.evaluate_stream_tick(symbol, ticker.get('last'))
                
            except ccxt.NetworkError:
                await asyncio.sleep(1) # Reconnect delay
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[STREAM] Ticker loop error on {symbol}: {e}")
                await asyncio.sleep(1)

    async def _watch_orders_loop(self):
        """Global listener for order status changes via User Data Stream."""
        exchange = await self.get_exchange()
        while self.is_running:
            try:
                orders = await exchange.watch_orders()
                for order in orders:
                    # Print or process FILL and CANCELED events
                    status = order.get('status')
                    print(f"[STREAM] Order Update: {order.get('id')} -> {status}")
                    
                    if status in ['closed', 'canceled', 'rejected', 'expired']:
                        from app.services.bot_service import bot_instance
                        await bot_instance.evaluate_stream_order(order)
                        
            except ccxt.NetworkError:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[STREAM] Orders loop error: {e}")
                traceback.print_exc()
                await asyncio.sleep(1)


# Global stream manager
stream_manager = StreamManager()
