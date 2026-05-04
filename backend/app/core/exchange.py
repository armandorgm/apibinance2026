import ccxt.async_support as ccxt
import ccxt.pro as ccxtpro
import asyncio
from typing import Dict, Any, List, Optional
from app.core.logger import logger
import time
from app.core.binance_native import binance_native

class ExchangeLogger:
    @staticmethod
    def log_request(endpoint: str, params: Dict[str, Any], response: Any = None, error_message: str = None):
        if error_message:
            logger.error(f"[EXCHANGE] {endpoint} | Params: {params} | Error: {error_message}")
        else:
            logger.debug(f"[EXCHANGE] {endpoint} | Params: {params} | Response: {str(response)[:100]}...")

class ExchangeManager:
    """
    Manages CCXT instance and official Binance Native driver.
    """
    def __init__(self):
        self._exchange: Optional[ccxt.binance] = None
        self._pro_exchange: Optional[ccxtpro.binance] = None
        self._native = binance_native
        self._last_request_time = 0
        self._rate_limit_delay = 0.1  # 100ms between critical calls
        self._price_registry: Dict[str, float] = {} # In-memory tick storage (DIAS Optimization)

    def update_price(self, symbol: str, price: float, side_data: Optional[Dict[str, float]] = None):
        """Update the latest price and optional bid/ask in volatile memory."""
        self._price_registry[symbol] = price
        if side_data:
            # Store full ticker info if provided
            if not hasattr(self, '_ticker_registry'):
                self._ticker_registry = {}
            self._ticker_registry[symbol] = side_data

    def get_price(self, symbol: str) -> Optional[float]:
        """Retrieve the latest cached price from memory."""
        return self._price_registry.get(symbol)

    def get_ticker(self, symbol: str) -> Optional[Dict[str, float]]:
        """Retrieve full bid/ask/last from memory."""
        if hasattr(self, '_ticker_registry'):
            return self._ticker_registry.get(symbol)
        return None

    async def get_pro_exchange(self) -> ccxtpro.binance:
        if self._pro_exchange is None:
            from app.core.config import settings
            self._pro_exchange = ccxtpro.binance({
                'apiKey': settings.BINANCE_API_KEY,
                'secret': settings.BINANCE_API_SECRET,
                'options': {
                    'defaultType': 'future',
                    'adjustForTimeDifference': True,
                    'newListenKeyReleaseAsync': True,
                    'fetchCurrencies': False
                },
                'enableRateLimit': True
            })
        return self._pro_exchange

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
                    'recvWindow': 10000,              # 10s window for high latency
                    'fetchCurrencies': False          # Avoid -2015 error on Futures-only keys
                },
                'enableRateLimit': True
            })
        return self._exchange

    async def _execute_with_retry(self, func, *args, **kwargs) -> Any:
        """Helper to execute an async CCXT call with retries and exponential backoff."""
        max_attempts = 5  # Increased from 3 for consistency with Native engine
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                
                # Check for network-related errors that warrant a retry
                is_network_error = any(msg in err_str for msg in [
                    "10054", "reset", "timeout", "closed", 
                    "connection error", "broken pipe", "econnreset", "request timeout"
                ])
                
                if is_network_error and attempt < max_attempts - 1:
                    logger.warning(f"[EXCHANGE] Network issue detected (attempt {attempt+1}/{max_attempts}): {e}. Retrying...")
                    
                    # If we've failed significantly, try to reset the session
                    if attempt >= 2:
                        logger.info("[EXCHANGE] Persistent connection issues. Resetting CCXT sessions...")
                        await self.close() # This sets self._exchange and self._pro_exchange to None
                    
                    await asyncio.sleep(attempt + 1)
                    continue
                
                # Business logic errors or other fatal errors should be raised immediately
                if not is_network_error:
                    logger.error(f"[EXCHANGE] Fatal CCXT error (non-retryable): {e}")
                else:
                    logger.error(f"[EXCHANGE] Exhausted {max_attempts} retries for network error: {e}")
                raise e
        
        raise last_error


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
            # Ensure markets are loaded (resilient against multiple calls)
            if not exchange.markets:
                await self._execute_with_retry(exchange.load_markets)
            
            # 1. Direct match in markets (keys use standard format)
            if symbol in exchange.markets: return symbol
            
            # 2. Match by market ID (e.g. 1000PEPEUSDC) or Upper ID
            symbol_up = symbol.upper()
            for m in exchange.markets.values():
                if m.get('id') == symbol_up or m.get('id') == symbol:
                    return m.get('symbol')
        except Exception as e:
            logger.warning(f"[EXCHANGE] normalize_symbol failed for {symbol}: {e}")
        
        # 3. HEURISTIC FALLBACK (DIAS Robustness)
        # If market load failed or no match found, try common Binance patterns
        s_up = symbol.upper()
        if s_up.endswith('USDC'):
            base = s_up[:-4].replace('/', '')
            return f"{base}/USDC:USDC"
        if s_up.endswith('USDT'):
            base = s_up[:-4].replace('/', '')
            return f"{base}/USDT:USDT"
            
        return symbol

    async def get_market_id(self, symbol: str) -> str:
        """
        Translates CCXT standard (1000PEPE/USDC:USDC) to Binance ID (1000PEPEUSDC).
        Used for Native driver and WS subscriptions.
        """
        if not symbol: return ""
        try:
            exchange = await self.get_exchange()
            if not exchange.markets:
                await self._execute_with_retry(exchange.load_markets)
            
            # 1. Direct lookup if it's already a standard symbol in our markets
            if symbol in exchange.markets:
                return exchange.markets[symbol]['id']
            
            # 2. Heuristic fallback (DIAS Robustness)
            clean = symbol.replace('/', '').replace(':USDC', '').replace(':USDT', '')
            return clean.upper()
        except Exception as e:
            logger.warning(f"[EXCHANGE] get_market_id failed for {symbol}: {e}")
            return symbol.replace('/', '').replace(':USDC', '').replace(':USDT', '').upper()

    async def fetch_orders_by_symbol(self, symbol: str, since: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol)
        try:
            orders = await self._execute_with_retry(exchange.fetch_orders, norm_sym, since=since, limit=limit)
            return orders
        except Exception as e:
            if "market symbol" not in str(e).lower():
                logger.error(f"[EXCHANGE] Error fetching orders for {norm_sym}: {e}")
            return []

    async def fetch_my_trades(self, symbol: str, since: Optional[int] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol)
        try:
            return await self._execute_with_retry(exchange.fetch_my_trades, norm_sym, since=since, limit=limit)
        except Exception as e:
            logger.error(f"[EXCHANGE] Error in fetch_my_trades for {norm_sym}: {e}")
            return []

    async def fetch_balance(self) -> Dict[str, Any]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        try:
            res = await self._execute_with_retry(exchange.fetch_balance)
            logger.debug(f"[EXCHANGE] fetch_balance | Assets: {list(res.get('total', {}).keys())}")
            return res
        except Exception as e:
            logger.error(f"[EXCHANGE] Error fetching balance: {e}")
            raise e

    async def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol) if symbol else None
        try:
            positions = await self._execute_with_retry(exchange.fetch_positions, symbols=[norm_sym] if norm_sym else None)
            return [p for p in positions if float(p.get('contracts', 0)) != 0]
        except Exception as e:
            logger.error(f"[EXCHANGE] Error fetching positions: {e}")
            return []

    async def has_open_position(self, symbol: str) -> bool:
        """
        Unified check to verify if a symbol has an active position on Binance.
        Essential for Anti-2022 Position Guard.
        """
        positions = await self.get_open_positions(symbol)
        return len(positions) > 0

    async def get_position_cycle_start(self, symbol: str) -> Optional[int]:
        norm_sym = await self.normalize_symbol(symbol)
        positions = await self.get_open_positions(norm_sym)
        if not positions: return None
        
        pos = positions[0]
        net_pos = float(pos.get('info', {}).get('pa', pos.get('contracts', 0)))
        if net_pos == 0: return None

        exchange = await self.get_exchange()
        trades = await self._execute_with_retry(exchange.fetch_my_trades, norm_sym, limit=1000)
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
        Returns RAW Binance data tagged with _source='algo'.
        """
        await self._rate_limit()
        exchange = await self.get_exchange()
        
        params = {}
        if symbol:
            await self._execute_with_retry(exchange.load_markets)
            norm_sym = await self.normalize_symbol(symbol)
            market = exchange.market(norm_sym)
            params['symbol'] = market['id'] # e.g. 1000PEPEUSDC

        try:
            # Manual request for compatibility with CCXT 4.1.94
            # Endpoint: GET /fapi/v1/openAlgoOrders
            res = await self._execute_with_retry(exchange.request, 'openAlgoOrders', 'fapiPrivate', 'GET', params)
            raw_orders = res if isinstance(res, list) else res.get('orders', res)
            
            # Tag with _source for OrderFactory compatibility
            for o in raw_orders:
                o['_source'] = 'algo'
                o['is_algo'] = True # Legacy support
            
            return raw_orders
        except Exception as e:
            logger.error(f"[EXCHANGE] Error fetching algo orders: {e}")
            return []

    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a combined list of Standard orders (CCXT Unified) and Algo orders (Raw Binance).
        Use OrderFactory.create() to process the results of this method.
        """
        await self._rate_limit()
        exchange = await self.get_exchange()
        norm_sym = await self.normalize_symbol(symbol) if symbol else None

        try:
            # 1. Standard orders
            t_std = self._execute_with_retry(exchange.fetch_open_orders, norm_sym)
            # 2. Algo orders (TP/SL) 
            t_algo = self.fetch_algo_open_orders(symbol)

            std_res, algo_res = await asyncio.gather(t_std, t_algo, return_exceptions=True)

            standard_orders = std_res if not isinstance(std_res, Exception) else []
            algo_orders = algo_res if not isinstance(algo_res, Exception) else []

            # Tag standard orders
            for o in standard_orders:
                if '_source' not in o: o['_source'] = 'standard'

            combined = standard_orders + algo_orders

            ExchangeLogger.log_request('fetch_open_orders', {'symbol': norm_sym}, response=f"Total: {len(combined)} (Std: {len(standard_orders)}, Algo: {len(algo_orders)})")
            return combined

        except Exception as e:
            if "market symbol" not in str(e).lower():
                logger.error(f'[EXCHANGE] Critical error in fetch_open_orders: {e}')
            return []

    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        return await self._execute_with_retry(exchange.fetch_ticker, norm_sym)

    async def get_tick_size(self, symbol: str) -> float:
        """Returns the minimum price increment (tickSize) for a symbol."""
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        await self._execute_with_retry(exchange.load_markets)
        market = exchange.markets.get(norm_sym, {})
        # CCXT Binance Future format usually stores the tickSize directly in precision
        return market.get('precision', {}).get('price', 0.0001)

    async def price_to_precision(self, symbol: str, price: float) -> str:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        await self._execute_with_retry(exchange.load_markets)
        return exchange.price_to_precision(norm_sym, price)

    async def get_safe_min_notional_qty(self, symbol: str, price: float) -> float:
        """
        Calcula la cantidad exacta mínima requerida para superar el MIN_NOTIONAL dinámico del símbolo,
        ajustada matemáticamente al stepSize y respetando el minQty.
        """
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        await self._execute_with_retry(exchange.load_markets)
        market = exchange.markets.get(norm_sym, {})
        
        # Extraer límites de mercado de CCXT (Manejo robusto de diccionarios)
        precision_info = market.get('precision', {})
        limits_info = market.get('limits', {})
        amount_limits = limits_info.get('amount', {})
        cost_limits = limits_info.get('cost', {})
        
        # En Binance Futures via CCXT, 'precision'['amount'] suele contener el stepSize en formato numérico (ej. 0.001)
        step_size = float(precision_info.get('amount', 0.001))
        if step_size <= 0:
            step_size = 0.001 # Fallback to standard step size
            
        lot_size_min_qty = float(amount_limits.get('min', step_size))
        
        # Obtener el MIN_NOTIONAL dinámico, si no existe asume 5.0 por seguridad estándar
        min_notional = float(cost_limits.get('min', 5.0))
        
        # Aplicamos el buffer de seguridad (1.001) sobre el límite de costo
        safe_min_notional = min_notional * 1.001
        
        # 1. Calculamos la cantidad cruda necesaria usando el notional seguro
        raw_qty = safe_min_notional / price
        
        # 2. Ajustamos al stepSize (la parte algorítmica crítica propuesta por el usuario)
        remainder = raw_qty % step_size
        if remainder > 0:
            min_qty = raw_qty - remainder + step_size
        else:
            min_qty = raw_qty
            
        # 3. Validamos contra el minQty del LOT_SIZE
        final_qty = max(min_qty, lot_size_min_qty)
        
        return final_qty

    async def amount_to_precision(self, symbol: str, amount: float) -> str:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        await self._execute_with_retry(exchange.load_markets)
        return exchange.amount_to_precision(norm_sym, amount)

    async def fetch_order_raw(self, symbol: str, order_id: str) -> Dict[str, Any]:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        return await self._execute_with_retry(exchange.fetch_order, order_id, norm_sym)

    async def create_order(self, symbol: str, order_type: str, side: str, amount: str, price: str = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        norm_sym = await self.normalize_symbol(symbol)
        exchange = await self.get_exchange()
        return await self._execute_with_retry(exchange.create_order, norm_sym, order_type, side, float(amount), float(price) if price else None, params or {})

    async def close(self):
        """Standardized cleanup for CCXT instances and sessions (V5.9.23)."""
        if self._exchange:
            await self._exchange.close()
            logger.info("[EXCHANGE] Async CCXT session closed.")
            self._exchange = None
            
        if self._pro_exchange:
            await self._pro_exchange.close()
            logger.info("[EXCHANGE] Pro (WebSocket) CCXT session closed.")
            self._pro_exchange = None

exchange_manager = ExchangeManager()
