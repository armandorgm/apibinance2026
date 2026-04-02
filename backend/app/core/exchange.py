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
from app.services.exchange_logger import ExchangeLogger


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
                    'warnOnFetchOpenOrdersWithoutSymbol': False,
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
            ExchangeLogger.log_request("fetch_my_trades", {"symbol": symbol, "since": since, "limit": limit, "params": params}, response=trades)
            return trades
        except Exception as e:
            print(f"--- [DEBUG] ERROR fetching trades for {symbol}: {e}")
            ExchangeLogger.log_request("fetch_my_trades", {"symbol": symbol, "since": since, "limit": limit, "params": params}, error_message=str(e))
            raise Exception(f"Error fetching trades from Binance: {str(e)}")
    
    async def fetch_balance(self) -> Dict[str, Any]:
        """Fetch account balance (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        try:
            b = await exchange.fetch_balance()
            ExchangeLogger.log_request("fetch_balance", {}, response=b)
            return b
        except Exception as e:
            ExchangeLogger.log_request("fetch_balance", {}, error_message=str(e))
            raise e
    
    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch current ticker price (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        try:
            t = await exchange.fetch_ticker(symbol)
            ExchangeLogger.log_request("fetch_ticker", {"symbol": symbol}, response=t)
            return t
        except Exception as e:
            ExchangeLogger.log_request("fetch_ticker", {"symbol": symbol}, error_message=str(e))
            raise e

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
            ExchangeLogger.log_request("create_order", {"symbol": symbol, "side": side, "amount": amount, "price": price, "type": order_type}, response=order)
            return order
        except Exception as e:
            print(f"--- [DEBUG] ERROR creating order for {symbol}: {e}")
            ExchangeLogger.log_request("create_order", {"symbol": symbol, "side": side, "amount": amount, "price": price, "type": order_type}, error_message=str(e))
            raise Exception(f"Error creating order on Binance: {str(e)}")

    async def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch current open positions from Binance Futures (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        try:
            positions = await exchange.fetch_positions(symbols=[symbol] if symbol else None)
            res = [p for p in positions if float(p.get('contracts', 0)) > 0 or float(p.get('notional', 0)) > 0]
            ExchangeLogger.log_request("get_open_positions", {"symbol": symbol}, response=res)
            return res
        except Exception as e:
            ExchangeLogger.log_request("get_open_positions", {"symbol": symbol}, error_message=str(e))
            raise e

    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch current open orders from Binance Futures (Async).
        Unifies Standard Service (v1/openOrders) and Algo Service (v1/openAlgoOrders).
        """
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        # We fetch both in parallel for efficiency
        import asyncio
        import json
        
        try:
            # 1. Standard Orders via CCXT standard method
            t_std = exchange.fetch_open_orders(symbol)
            
            # 2. Algo Orders (Conditional TP/SL/Trailing)
            # Binance Algo endpoint might not exist depending on the CCXT version or account type
            t_algo = None
            if hasattr(exchange, 'fapiPrivateGetOpenAlgoOrders'):
                # Wrap it in an async function to make it awaitable like t_std
                async def fetch_algo():
                    return await exchange.fapiPrivateGetOpenAlgoOrders({'symbol': symbol.replace('/', '') if symbol else None})
                t_algo = fetch_algo()
            
            # Awaits in parallel if both exist
            if t_algo:
                std_res, algo_res = await asyncio.gather(t_std, t_algo, return_exceptions=True)
            else:
                std_res = await t_std
                algo_res = []
            
            # Process standard results
            standard_orders = std_res if not isinstance(std_res, Exception) else []
            if isinstance(std_res, Exception):
                print(f"[EXCHANGE] Error fetching standard orders: {std_res}")
                # Re-raise if it's the primary channel and the only one we depend on
                raise std_res
                
            # Process algo results (Binance returns list of orders or object with 'orders' field)
            algo_orders = []
            if not isinstance(algo_res, Exception):
                algo_orders = algo_res if isinstance(algo_res, list) else algo_res.get('orders', [])
            else:
                print(f"[EXCHANGE] Error fetching algo orders: {algo_res}")

            # Return combined list for the API layer to normalize
            # We tag them so the mapper knows the source
            for o in standard_orders: o['_source'] = 'standard'
            for o in algo_orders: o['_source'] = 'algo'
            
            combined = standard_orders + algo_orders
            ExchangeLogger.log_request("fetch_open_orders", {"symbol": symbol}, response=combined)
            return combined
            
        except Exception as e:
            print(f"[EXCHANGE] Critical error in fetch_open_orders: {e}")
            ExchangeLogger.log_request("fetch_open_orders", {"symbol": symbol}, error_message=str(e))
            # If all fails, return empty to not crash the UI
            return []


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
