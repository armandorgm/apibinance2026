"""
Exchange connection management using CCXT Async.
Handles API keys, rate limits, and Binance Futures connection.
"""
import ccxt.async_support as ccxt
from typing import Optional, List, Dict, Any
from app.core.config import settings
import asyncio
import time
from datetime import datetime


class ExchangeManager:
    """Manages connection to Binance Futures exchange via CCXT Async."""
    
    def __init__(self):
        self.exchange: Optional[ccxt.binance] = None
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests (rate limit protection)
    
    async def get_exchange(self) -> ccxt.binance:
        """Get or create exchange instance asynchronously."""
        if self.exchange is None:
            api_key = settings.BINANCE_API_KEY or ""
            api_secret = settings.BINANCE_API_SECRET or ""
            masked_key = f"***{api_key[-3:]}" if len(api_key) >= 3 else "***"
            masked_secret = f"***{api_secret[-3:]}" if len(api_secret) >= 3 else "***"
            print(
                f"[Binance API] Using API key ending with {masked_key} "
                f"and secret ending with {masked_secret}"
            )

            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                    'adjustForTimeDifference': True,
                },
                'sandbox': settings.TESTNET,
            })
            # Force a time sync immediately upon initialization.
            try:
                print("\n[Binance API] Forcing initial time synchronization...")
                await self.exchange.load_time_difference()
                print("[Binance API] Time synchronized successfully.\n")
            except Exception as e:
                print(f"[Binance API] Could not force time sync on init: {e}\n")
        return self.exchange
    
    async def close(self):
        """Close exchange connection."""
        if self.exchange:
            await self.exchange.close()
            self.exchange = None

    async def _rate_limit(self):
        """Non-blocking rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time.time()
    
    async def fetch_my_trades(
        self, 
        symbol: str, 
        since: Optional[int] = None,
        limit: int = 1000,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch user's trades from Binance Futures (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        since_readable = f"{since} ({datetime.fromtimestamp(since / 1000).strftime('%Y-%m-%d %H:%M:%S')})" if since else "None"
        print(f"--- [DEBUG] Fetching trades for {symbol} | Since: {since_readable} | Limit: {limit}")
        
        try:
            trades = await exchange.fetch_my_trades(symbol, since=since, limit=limit, params=params or {})
            print(f"--- [DEBUG] Binance API returned {len(trades)} trades for {symbol}.")
            return trades
        except Exception as e:
            print(f"--- [DEBUG] ERROR fetching trades for {symbol}: {e}")
            raise Exception(f"Error fetching trades from Binance: {str(e)}")
    
    async def fetch_balance(self) -> Dict[str, Any]:
        """Fetch account balance (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        return await exchange.fetch_balance()
    
    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch current ticker price (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        return await exchange.fetch_ticker(symbol)

    async def create_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = 'market',
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new order on Binance Futures (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        try:
            order = await exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params or {}
            )
            print(f"--- [DEBUG] Order created: {order['id']} ({side} {amount} {symbol})")
            return order
        except Exception as e:
            print(f"--- [DEBUG] ERROR creating order for {symbol}: {e}")
            raise Exception(f"Error creating order on Binance: {str(e)}")

    async def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch current open positions from Binance Futures (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        positions = await exchange.fetch_positions(symbols=[symbol] if symbol else None)
        return [p for p in positions if float(p.get('contracts', 0)) > 0 or float(p.get('notional', 0)) > 0]

    async def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to CCXT market format (Async)."""
        if '/' in symbol:
            return symbol
        try:
            exchange = await self.get_exchange()
            await exchange.load_markets()
            for market in (exchange.markets or {}).values():
                if market.get('id') == symbol or market.get('id') == symbol.upper():
                    return market.get('symbol', symbol)
        except Exception:
            pass
        return symbol


# Global exchange manager instance
exchange_manager = ExchangeManager()
