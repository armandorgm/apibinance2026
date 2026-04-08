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
    
    async def fetch_order_raw(self, symbol: str, order_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene la orden por id (futures) para leer el tipo nativo Binance."""
        if not order_id:
            return None
        await self._rate_limit()
        exchange = await self.get_exchange()
        try:
            o = await exchange.fetch_order(order_id, symbol)
            ExchangeLogger.log_request(
                "fetch_order",
                {"symbol": symbol, "orderId": order_id},
                response=o,
            )
            return o if isinstance(o, dict) else None
        except Exception as e:
            ExchangeLogger.log_request(
                "fetch_order",
                {"symbol": symbol, "orderId": order_id},
                error_message=str(e),
            )
            return None

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
        amount: Any,
        price: Optional[Any] = None,
        order_type: str = 'market',
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new order on Binance Futures (Async)."""
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        # Consistent float conversion for Binance API compatibility
        f_amount = float(amount) if amount is not None else 0.0
        f_price = float(price) if price is not None else None
        
        try:
            # Using positional arguments for CCXT to avoid any keyword mapping confusion
            # Signature: symbol, type, side, amount, price=None, params={}
            order = await exchange.create_order(
                symbol,
                order_type,
                side,
                f_amount,
                f_price,
                params or {}
            )
            print(f"--- [DEBUG] Order created: {order['id']} ({side} {f_amount} {symbol})")
            ExchangeLogger.log_request("create_order", {"symbol": symbol, "side": side, "amount": f_amount, "price": f_price, "type": order_type}, response=order)
            return order
        except Exception as e:
            print(f"--- [DEBUG] ERROR creating order for {symbol}: {e}")
            ExchangeLogger.log_request("create_order", {"symbol": symbol, "side": side, "amount": f_amount, "price": f_price, "type": order_type}, error_message=str(e))
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

    async def _fapi_conditional_open_orders(
        self, exchange: ccxt.binance, symbol: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        USD-M / USDC-M conditional TP/SL/trailing (Binance GET /fapi/v1/openAlgoOrders).
        Returns raw dicts with orderType, side, triggerPrice, algoType CONDITIONAL, etc.
        """
        params: Dict[str, Any] = {'algoType': 'CONDITIONAL'}
        if symbol:
            await exchange.load_markets()
            params['symbol'] = exchange.market(symbol)['id']
        try:
            res = await exchange.fapiPrivateGetOpenAlgoOrders(params)
        except Exception as e1:
            try:
                res = await exchange.request('openAlgoOrders', 'fapiPrivate', 'GET', params)
            except Exception as e2:
                ExchangeLogger.log_request(
                    'fapiPrivateGetOpenAlgoOrders',
                    params,
                    error_message=f'{e1} | fallback: {e2}',
                )
                return []
        ExchangeLogger.log_request('fapiPrivateGetOpenAlgoOrders', params, response=res)
        if isinstance(res, list):
            return res
        if isinstance(res, dict) and 'orders' in res:
            return res['orders'] if isinstance(res['orders'], list) else []
        return []

    async def _sapi_algo_futures_open_orders(
        self, exchange: ccxt.binance, symbol: Optional[str]
    ) -> List[Dict[str, Any]]:
        """SAPI algo/futures open orders (e.g. VP) — separate product from FAPI CONDITIONAL."""
        params: Dict[str, Any] = {}
        if symbol:
            params['symbol'] = symbol.replace('/', '').split(':')[0]
        try:
            res = await exchange.sapiGetAlgoFuturesOpenOrders(params)
            ExchangeLogger.log_request('sapiGetAlgoFuturesOpenOrders', params, response=res)
        except Exception as e:
            ExchangeLogger.log_request('sapiGetAlgoFuturesOpenOrders', params, error_message=str(e))
            return []
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            orders = res.get('orders', [])
            return orders if isinstance(orders, list) else []
        return []

    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch current open orders from Binance Futures (Async).
        Merges:
        - v1/openOrders (libro estándar vía CCXT)
        - v1/openAlgoOrders?algoType=CONDITIONAL (TP/SL/trailing — incluye TAKE_PROFIT_MARKET con side SELL)
        - sapi/v1/algo/futures/openOrders (otros algoritmos p. ej. VP, sin solaparse con CONDITIONAL)
        """
        await self._rate_limit()
        exchange = await self.get_exchange()

        try:
            t_std = exchange.fetch_open_orders(symbol)

            async def safe_conditional():
                if getattr(exchange, 'id', '') != 'binance':
                    return []
                return await self._fapi_conditional_open_orders(exchange, symbol)

            async def safe_sapi_algo():
                if getattr(exchange, 'id', '') != 'binance':
                    return []
                return await self._sapi_algo_futures_open_orders(exchange, symbol)

            std_res, fapi_algo_res, sapi_algo_res = await asyncio.gather(
                t_std, safe_conditional(), safe_sapi_algo(), return_exceptions=True
            )

            standard_orders = std_res if not isinstance(std_res, Exception) else []
            if isinstance(std_res, Exception):
                print(f'[EXCHANGE] Error fetching standard orders: {std_res}')
                raise std_res

            fapi_algo: List[Dict[str, Any]] = (
                fapi_algo_res if not isinstance(fapi_algo_res, Exception) else []
            )
            if isinstance(fapi_algo_res, Exception):
                print(f'[EXCHANGE] Error fetching FAPI openAlgoOrders: {fapi_algo_res}')

            sapi_algo: List[Dict[str, Any]] = (
                sapi_algo_res if not isinstance(sapi_algo_res, Exception) else []
            )
            if isinstance(sapi_algo_res, Exception):
                print(f'[EXCHANGE] Error fetching SAPI algo futures orders: {sapi_algo_res}')

            for o in standard_orders:
                o['_source'] = 'standard'
            for o in fapi_algo:
                o['_source'] = 'algo'
            for o in sapi_algo:
                o['_source'] = 'algo'

            seen_ids = set()
            combined: List[Dict[str, Any]] = []

            def add_unique(order: Dict[str, Any]) -> None:
                oid = order.get('algoId') or order.get('orderId') or order.get('id')
                sym = order.get('symbol', '')
                key = (sym, str(oid)) if oid else None
                if key:
                    if key in seen_ids:
                        return
                    seen_ids.add(key)
                combined.append(order)

            for o in standard_orders:
                add_unique(o)
            for o in fapi_algo:
                add_unique(o)
            for o in sapi_algo:
                add_unique(o)

            ExchangeLogger.log_request('fetch_open_orders', {'symbol': symbol}, response=combined)
            return combined

        except Exception as e:
            print(f'[EXCHANGE] Critical error in fetch_open_orders: {e}')
            ExchangeLogger.log_request('fetch_open_orders', {'symbol': symbol}, error_message=str(e))
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

    async def price_to_precision(self, symbol: str, price: float) -> str:
        """Convert price to the precision required by the exchange (Async)."""
        exchange = await self.get_exchange()
        await exchange.load_markets()
        return exchange.price_to_precision(symbol, price)

    async def amount_to_precision(self, symbol: str, amount: float) -> str:
        """Convert amount to the precision required by the exchange (Async)."""
        exchange = await self.get_exchange()
        await exchange.load_markets()
        return exchange.amount_to_precision(symbol, amount)


# Global exchange manager instance
exchange_manager = ExchangeManager()
