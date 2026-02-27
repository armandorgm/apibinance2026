"""
Exchange connection management using CCXT.
Handles API keys, rate limits, and Binance Futures connection.
"""
import ccxt
from typing import Optional, List, Dict, Any
from app.core.config import settings
import time
from datetime import datetime


class ExchangeManager:
    """Manages connection to Binance Futures exchange via CCXT."""
    
    def __init__(self):
        self.exchange: Optional[ccxt.binance] = None
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests (rate limit protection)
    
    def get_exchange(self) -> ccxt.binance:
        """Get or create exchange instance."""
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
                    'defaultType': 'future',  # Use futures
                    'adjustForTimeDifference': True,  # Auto-sync time with Binance
                },
                'sandbox': settings.TESTNET,
            })
        return self.exchange
    
    def _rate_limit(self):
        """Simple rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time.time()
    
    async def fetch_my_trades(
        self, 
        symbol: str, 
        since: Optional[int] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch user's trades from Binance Futures.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            since: Timestamp in milliseconds (optional)
            limit: Maximum number of trades to fetch
            
        Returns:
            List of trade dictionaries
        """
        self._rate_limit()
        exchange = self.get_exchange()
        
        since_readable = "None"
        if since:
            since_readable = f"{since} ({datetime.fromtimestamp(since / 1000).strftime('%Y-%m-%d %H:%M:%S')})"
        print(f"--- [DEBUG] Fetching trades for {symbol} | Since: {since_readable} | Limit: {limit}")
        # #region agent log
        _log_path = r"c:\Users\arman\OneDrive\Documentos\Visual Studio 2022\apibinance2026\.cursor\debug.log"
        import json
        import time
        try:
            exchange.load_markets()
            pepe_symbols = [m for m in (exchange.symbols or []) if "PEPE" in m.upper()]
            with open(_log_path, "a", encoding="utf-8") as _f:
                _f.write(json.dumps({"message": "fetch_my_trades before call", "data": {"symbol": symbol, "options": exchange.options, "pepe_symbols_in_markets": pepe_symbols[:30]}, "hypothesisId": "B,C,E", "location": "exchange.py:fetch_my_trades", "timestamp": int(time.time() * 1000)}) + "\n")
        except Exception as _le:
            try:
                with open(_log_path, "a", encoding="utf-8") as _f:
                    _f.write(json.dumps({"message": "load_markets or log failed", "data": {"symbol": symbol, "log_err": str(_le)}, "hypothesisId": "B", "location": "exchange.py:fetch_my_trades", "timestamp": int(time.time() * 1000)}) + "\n")
            except Exception:
                pass
        # #endregion
        try:
            trades = exchange.fetch_my_trades(symbol, since=since, limit=limit)
            print(f"--- [DEBUG] Binance API returned {len(trades)} trades for {symbol}.")
            if trades:
                first_trade_dt = trades[0].get('datetime')
                last_trade_dt = trades[-1].get('datetime')
                print(f"--- [DEBUG]   -> First trade datetime: {first_trade_dt}")
                print(f"--- [DEBUG]   -> Last trade datetime: {last_trade_dt}")
            return trades
        except Exception as e:
            print(f"--- [DEBUG] ERROR fetching trades for {symbol}: {e}")
            # #region agent log
            try:
                with open(_log_path, "a", encoding="utf-8") as _f:
                    _f.write(json.dumps({"message": "fetch_my_trades exception", "data": {"symbol": symbol, "error_type": type(e).__name__, "error_str": str(e)}, "hypothesisId": "A,C,D,E", "location": "exchange.py:fetch_my_trades", "timestamp": int(time.time() * 1000)}) + "\n")
            except Exception:
                pass
            # #endregion
            raise Exception(f"Error fetching trades from Binance: {str(e)}")
    
    async def fetch_balance(self) -> Dict[str, Any]:
        """Fetch account balance."""
        self._rate_limit()
        exchange = self.get_exchange()
        
        try:
            balance = exchange.fetch_balance()
            return balance
        except Exception as e:
            raise Exception(f"Error fetching balance: {str(e)}")
    
    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch current ticker price."""
        self._rate_limit()
        exchange = self.get_exchange()
        
        try:
            ticker = exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            raise Exception(f"Error fetching ticker: {str(e)}")

    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to CCXT market format (e.g. 'BTCUSDT' -> 'BTC/USDT').

        If the incoming symbol already contains a slash, it's returned as-is.
        Otherwise we try to map the exchange market `id` to its `symbol`.
        """
        try:
            if '/' in symbol:
                return symbol
            exchange = self.get_exchange()
            # Ensure markets are loaded
            try:
                exchange.load_markets()
            except Exception:
                pass

            for market in (exchange.markets or {}).values():
                # market['id'] is exchange-specific id like 'BTCUSDT'
                if market.get('id') == symbol or market.get('id') == symbol.upper():
                    return market.get('symbol', symbol)
        except Exception:
            pass

        return symbol


# Global exchange manager instance
exchange_manager = ExchangeManager()
