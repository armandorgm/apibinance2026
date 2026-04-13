import ccxt.async_support as ccxt
import asyncio
from typing import Dict, Any, List, Optional
from app.core.logger import logger
import time

class ExchangeLogger:
    @staticmethod
    def log_request(endpoint: str, params: Dict[str, Any], response: Any = None, error_message: str = None):
        if error_message:
            logger.error(f"[EXCHANGE] {endpoint} | Params: {params} | Error: {error_message}")
        else:
            logger.debug(f"[EXCHANGE] {endpoint} | Params: {params} | Response: {str(response)[:100]}...")

class ExchangeManager:
    """
    Manages Binance Futures connection via CCXT.
    V5.9 Stability Release: Handles clock sync (-1021) and symbol resilience.
    """
    def __init__(self):
        self._exchange: Optional[ccxt.binance] = None
        self._last_request_time = 0
        self._rate_limit_delay = 0.1  # 100ms between critical calls

    async def get_exchange(self) -> ccxt.binance:
        if self._exchange is None:
            from app.core.config import settings
            self._exchange = ccxt.binance({
                'apiKey': settings.BINANCE_API_KEY,
                'secret': settings.BINANCE_API_SECRET,
                'options': {
                    'defaultType': 'future',
                    'warnOnFetchOpenOrdersWithoutSymbol': False,
                    'adjustForTimeDifference': True,  # Fix for Error -1021
                    'recvWindow': 10000               # 10s window for high latency
                },
                'enableRateLimit': True
            })
        return self._exchange

    async def _rate_limit(self):
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    async def normalize_symbol(self, symbol: str) -> str:
        """
        Translates Binance direct ID (e.g. 1000PEPEUSDC) to CCXT standard (1000PEPE/USDC:USDC).
        Ensures resilience as requested by USER.
        """
        if not symbol or len(symbol) < 3: return symbol
        if '/' in symbol and ':' in symbol: return symbol # Already standard
        
        try:
            exchange = await self.get_exchange()
            await exchange.load_markets()
            # 1. Direct match in markets (keys use standard format)
            if symbol in exchange.markets: return symbol
            
            # 2. Match by market ID (e.g. 1000PEPEUSDC) or Upper ID
            symbol_up = symbol.upper()
            for m in exchange.markets.values():
                if m.get('id') == symbol_up or m.get('id') == symbol:
                    return m.get('symbol')
        except Exception: pass
        return symbol

    async def fetch_orders_by_symbol(self, symbol: str, since: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol)
        try:
            orders = await exchange.fetch_orders(norm_sym, since=since, limit=limit)
            return orders
        except Exception as e:
            if "market symbol" not in str(e).lower():
                logger.error(f"[EXCHANGE] Error fetching orders for {norm_sym}: {e}")
            return []

    async def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol) if symbol else None
        try:
            positions = await exchange.fetch_positions(symbols=[norm_sym] if norm_sym else None)
            return [p for p in positions if float(p.get('contracts', 0)) != 0]
        except Exception as e:
            logger.error(f"[EXCHANGE] Error fetching positions: {e}")
            return []

    async def get_position_cycle_start(self, symbol: str) -> Optional[int]:
        norm_sym = await self.normalize_symbol(symbol)
        positions = await self.get_open_positions(norm_sym)
        if not positions: return None
        
        pos = positions[0]
        net_pos = float(pos.get('info', {}).get('pa', pos.get('contracts', 0)))
        if net_pos == 0: return None

        exchange = await self.get_exchange()
        trades = await exchange.fetch_my_trades(norm_sym, limit=1000)
        trades.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

        running_qty = net_pos
        last_valid_ts = None
        for t in trades:
            side = t.get('side', '').lower()
            qty = float(t.get('amount', 0))
            if side == 'buy': running_qty -= qty
            else: running_qty += qty
            if (net_pos > 0 and running_qty <= 0) or (net_pos < 0 and running_qty >= 0):
                return t.get('timestamp')
            last_valid_ts = t.get('timestamp')
        return last_valid_ts

    async def fetch_algo_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches conditional orders (TP/SL) from Binance Algo Service via CCXT native method.
        """
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        params = {}
        if symbol:
            # Native methods often require Binance ID, load_markets ensures we have them
            await exchange.load_markets()
            norm_sym = await self.normalize_symbol(symbol)
            market = exchange.market(norm_sym)
            params['symbol'] = market['id'] # e.g. 1000PEPEUSDC

        try:
            # Direct call to fapiprivate_get_openalgoorders (CCXT 4.5+)
            raw_orders = await exchange.fapiprivate_get_openalgoorders(params)
            
            # Normalize to match CCXT's fetchFetchOpenOrders structure if possible, 
            # but for now we'll just ensure they have the basics
            unified_algo = []
            for o in raw_orders:
                # CCXT usually doesn't unify these yet, so we map essential fields
                unified_algo.append({
                    'id': str(o.get('algoId')),
                    'symbol': symbol or o.get('symbol'),
                    'type': o.get('orderType'),
                    'side': o.get('side'),
                    'amount': float(o.get('quantity', 0)),
                    'price': float(o.get('triggerPrice', 0)),
                    'status': 'open' if o.get('algoStatus') == 'NEW' else o.get('algoStatus'),
                    'info': o,
                    'is_algo': True
                })
            return unified_algo
        except Exception as e:
            logger.error(f"[EXCHANGE] Error fetching algo orders: {e}")
            return []

    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol) if symbol else None

        try:
            # 1. Standard orders
            t_std = exchange.fetch_open_orders(norm_sym)
            # 2. Algo orders (TP/SL) using our new native-based method
            t_algo = self.fetch_algo_open_orders(symbol)

            std_res, algo_res = await asyncio.gather(t_std, t_algo, return_exceptions=True)

            standard_orders = std_res if not isinstance(std_res, Exception) else []
            combined = algo_res if not isinstance(algo_res, Exception) else []

            # Deduplicate by ID
            seen_ids = {str(o.get('id')) for o in combined if o.get('id')}
            
            for o in standard_orders:
                oid = str(o.get('id'))
                if oid not in seen_ids:
                    combined.append(o)
                    seen_ids.add(oid)

            ExchangeLogger.log_request('fetch_open_orders_unified', {'symbol': norm_sym}, response=combined)
            return combined

        except Exception as e:
            if "market symbol" not in str(e).lower():
                logger.error(f'[EXCHANGE] Critical error in fetch_open_orders: {e}')
            return []

    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        return await exchange.fetch_ticker(norm_sym)

    async def price_to_precision(self, symbol: str, price: float) -> str:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        await exchange.load_markets()
        return exchange.price_to_precision(norm_sym, price)

    async def amount_to_precision(self, symbol: str, amount: float) -> str:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        await exchange.load_markets()
        return exchange.amount_to_precision(norm_sym, amount)

    async def fetch_order_raw(self, symbol: str, order_id: str) -> Dict[str, Any]:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        return await exchange.fetch_order(order_id, norm_sym)

    async def create_order(self, symbol: str, order_type: str, side: str, amount: str, price: str = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        return await exchange.create_order(norm_sym, order_type, side, float(amount), float(price) if price else None, params)

exchange_manager = ExchangeManager()
