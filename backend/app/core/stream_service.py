import asyncio
import json
import traceback
from typing import Dict, Any, Optional, Set
from app.core.config import settings
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from app.core.logger import logger

class StreamManager:
    """
    Manages centralized WebSocket subscriptions using Binance Native Client.
    Ensures 'one and only one' connection per category (Market vs User Data).
    Optimized for high-frequency @bookTicker precision.
    """
    def __init__(self):
        self.market_client: Optional[UMFuturesWebsocketClient] = None
        self.user_client: Optional[UMFuturesWebsocketClient] = None
        self.subscribed_symbols: Set[str] = set()
        self.is_running = False

    async def start(self):
        """Starts the consolidated native streaming clients."""
        if self.is_running: return
        self.is_running = True
        
        # 1. Start Market Data Client (Aggregated)
        self.market_client = UMFuturesWebsocketClient(
            on_message=self._handle_market_message,
            on_error=lambda _, e: print(f"[STREAM] Market WS Error: {e}")
        )
        
        # 2. Start User Data Client (Orders)
        await self._start_user_stream_native()
        
        # 3. Capture the main event loop for thread-safe callbacks
        self._loop = asyncio.get_running_loop()
        
        logger.info("[STREAM] StreamManager started (Native Mode).")

    async def _start_user_stream_native(self):
        """Initializes User Data Stream using the native listenKey mechanism."""
        try:
            from app.core.binance_native import binance_native
            loop = asyncio.get_event_loop()
            # Request new listen key via REST
            res = await loop.run_in_executor(None, binance_native.client.new_listen_key)
            listen_key = res.get("listenKey")
            
            if listen_key:
                self.user_client = UMFuturesWebsocketClient(on_message=self._handle_user_message)
                self.user_client.user_data(listen_key=listen_key)
                logger.info("[STREAM] User Data Stream active with listenKey.")
        except Exception as e:
            logger.error(f"[STREAM] Failed to start User Data Stream: {e}")

    async def stop(self):
        self.is_running = False
        if self.market_client: self.market_client.stop()
        if self.user_client: self.user_client.stop()
        print("[STREAM] StreamManager stopped.")

    async def subscribe(self, symbol: str):
        """Subscribe to high-frequency bookTicker for a symbol."""
        if symbol not in self.subscribed_symbols:
            self.subscribed_symbols.add(symbol)
            if self.market_client:
                # Get Native ID (e.g. 1000PEPEUSDC)
                from app.core.exchange import exchange_manager
                market_id = await exchange_manager.get_market_id(symbol)
                self.market_client.book_ticker(symbol=market_id.lower())
                logger.info(f"[STREAM] Registered {symbol} for native @bookTicker stream (Success).")

    async def unsubscribe(self, symbol: str):
        """Unsubscribe from bookTicker (release resources)."""
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)
            logger.info(f"[STREAM] Unregistered {symbol} from tracking.")

    async def recover_active_subscriptions(self):
        """
        Public method to ensure all active processes are being tracked.
        1. WebSocket re-subscription for chasing symbols.
        2. REST-based 'Hard-Sync' to detect filled/expired orders missed by WS.
        """
        print("[STREAM] Recovering active subscriptions from DB...")
        from app.db.database import get_session_direct, BotPipelineProcess
        from app.core.exchange import exchange_manager
        from app.services.pipeline_engine.registry import ACTIONS

        try:
            with get_session_direct() as session:
                active_procs = session.query(BotPipelineProcess).filter(
                    BotPipelineProcess.status == "CHASING"
                ).all()
                
                if not active_procs:
                    print("[STREAM] No active chasing processes to recover.")
                    return

                symbols_to_resub = {p.symbol for p in active_procs}
                for sym in symbols_to_resub:
                    await self.subscribe(sym)
                
                print(f"[STREAM] Proactive Hard-Sync: checking {len(active_procs)} processes.")
                
                for p in active_procs:
                    if not p.entry_order_id or p.entry_order_id == "INITIAL_REJECTED":
                        continue
                        
                    try:
                        order_info = await exchange_manager.fetch_order_raw(p.symbol, p.entry_order_id)
                        status = order_info.get("status")
                        filled = order_info.get("filled", 0)
                        
                        if status == "closed":
                            if filled > 0:
                                print(f"[STREAM] Hard-sync: Order {p.entry_order_id} is FILLED. Advancing.")
                                handler_key = "ADAPTIVE_OTO_V2" if "NATIVE" in (p.sub_status or "") else "ADAPTIVE_OTO"
                                handler = ACTIONS.get(handler_key)
                                if handler:
                                    await handler.handle_fill(p, session)
                            else:
                                print(f"[STREAM] Hard-sync: Order {p.entry_order_id} is EXPIRED/CANCELED. Clearing ID.")
                                p.entry_order_id = None
                                session.commit()
                        
                    except Exception as e:
                        print(f"[STREAM] Hard-sync check failed for {p.entry_order_id}: {e}")

                print(f"[STREAM] Successful recovery for {len(symbols_to_resub)} symbols.")
        except Exception as e:
            print(f"[STREAM] Recovery failed: {e}")

    async def _get_market_id_async(self, symbol: str) -> str:
        from app.core.exchange import exchange_manager
        return await exchange_manager.get_market_id(symbol)

    def _handle_market_message(self, _, message):
        """Process real-time bid/ask from Binance. Dual-Key broadcast (V5.9.27)."""
        try:
            # Handle both string and pre-parsed dict from binance connector
            data = json.loads(message) if isinstance(message, str) else message
            
            if isinstance(data, dict) and "s" in data: # bookTicker event
                symbol_raw = data["s"]
                bid = float(data["b"])
                ask = float(data["a"])
                
                # V5.9.27: Thread-safe dispatch to the main loop
                if hasattr(self, '_loop') and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self._process_tick_native_raw(symbol_raw, bid, ask), 
                        self._loop
                    )
        except Exception:
            pass

    async def _process_tick_native_raw(self, symbol_raw: str, bid: float, ask: float):
        from app.core.exchange import exchange_manager
        ccxt_symbol = await exchange_manager.normalize_symbol(symbol_raw)
        
        ticker_data = {"bid": bid, "ask": ask, "last": (bid + ask) / 2}
        exchange_manager.update_price(ccxt_symbol, ticker_data["last"], side_data=ticker_data)
        
        # V5.9.21: Internal and external distribution with both ID formats
        await self._process_tick_native(ccxt_symbol, symbol_raw, ticker_data)

    async def _process_tick_native(self, symbol: str, raw_symbol: str, data: dict):
        from app.services.bot_service import bot_instance
        await bot_instance.evaluate_stream_tick(symbol, data["ask"])
        
        from app.services.notification_service import notification_manager
        await notification_manager.broadcast("ticker_update", {
            "symbol": symbol,        # CCXT Format (e.g. BTC/USDT)
            "raw_symbol": raw_symbol, # Binance ID (e.g. BTCUSDT)
            "bid": data["bid"],
            "ask": data["ask"],
            "last": data["last"]
        })

    def _handle_user_message(self, _, message):
        """Process Order Updates (ORDER_TRADE_UPDATE)."""
        try:
            data = json.loads(message)
            if data.get("e") == "ORDER_TRADE_UPDATE":
                oi = data["o"]
                status_map = {"FILLED": "filled", "CANCELED": "canceled", "EXPIRED": "expired", "NEW": "open"}
                status = status_map.get(oi["X"], "unknown")
                
                if status in ["filled", "canceled", "expired"]:
                    order_data = {
                        "id": str(oi["i"]),
                        "symbol": oi["s"],
                        "status": status,
                        "side": oi["S"].lower(),
                        "price": float(oi["L"]) if oi["L"] != "0" else float(oi["ap"]),
                        "z": float(oi.get("z", 0.0)) if oi.get("z") else 0.0 # Safe extraction (V5.9.29)
                    }
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self._process_order_native(order_data))
        except Exception:
            pass

    async def _process_order_native(self, order_data: dict):
        from app.services.bot_service import bot_instance
        await bot_instance.evaluate_stream_order(order_data)
        
        from app.services.notification_service import notification_manager
        await notification_manager.broadcast("order_update", order_data)

# Global singleton
stream_manager = StreamManager()
