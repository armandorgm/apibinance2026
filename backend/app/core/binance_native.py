import asyncio
import hmac
import hashlib
import time
import requests
from typing import Dict, Any, Optional
from binance.um_futures import UMFutures
from app.core.config import settings
from app.core.logger import logger

import binance.lib.utils as binance_utils

class BinanceNativeEngine:
    """
    Official Binance Native Execution Engine.
    Uses 'binance-futures-connector' for high-reliability trade operations.
    Specialized for: Modify Order (PUT), Take Profit (POST reduceOnly).
    """
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = False):
        self.api_key = api_key or settings.BINANCE_API_KEY
        self.api_secret = api_secret or settings.BINANCE_API_SECRET
        self.base_url = "https://fapi.binance.com" if not testnet else "https://testnet.binancefuture.com"
        
        # 1. Calculate time offset to prevent -1021 Timestamp errors
        self.time_offset = 0
        try:
            # Syncing with REST API server time
            response = requests.get(f"{self.base_url}/fapi/v1/time", timeout=5)
            if response.status_code == 200:
                server_time = response.json()["serverTime"]
                local_time = int(time.time() * 1000)
                self.time_offset = server_time - local_time
                logger.info(f"[NATIVE] Time Sync: Offset={self.time_offset}ms")
        except Exception as e:
            logger.warning(f"[NATIVE] Time sync failed: {e}")

        # 2. Monkey-patch the binance connector's internal timestamp generator
        # We patch it in multiple places to ensure it's picked up
        self._original_get_timestamp = binance_utils.get_timestamp
        binance_utils.get_timestamp = self._get_synced_timestamp
        
        # Also patch in the specific library modules if they imported it by name
        try:
            import binance.um_futures as um_futures
            um_futures.get_timestamp = self._get_synced_timestamp
            
            import binance.api as binance_api
            binance_api.get_timestamp = self._get_synced_timestamp
            
            import binance.websocket.websocket_client as ws_client
            ws_client.get_timestamp = self._get_synced_timestamp
        except:
            pass

        # 3. Initialize the official client
        self.client = UMFutures(
            key=self.api_key,
            secret=self.api_secret,
            base_url=self.base_url
        )

    def _get_synced_timestamp(self):
        """Replacement for binance.lib.utils.get_timestamp"""
        return int(time.time() * 1000) + self.time_offset

    async def _execute_with_retry(self, func, *args, **kwargs) -> Any:
        """Helper to execute a synchronous client call with retries and exponential backoff."""
        max_attempts = 5  # Increased from 3
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
            except Exception as e:
                err_str = str(e).lower()
                # Check for network-related errors that warrant a retry
                # WinError 10054, ConnectionResetError, Timeout, etc.
                is_network_error = any(msg in err_str for msg in ["10054", "reset", "timeout", "closed", "connection error", "broken pipe"])
                
                if is_network_error and attempt < max_attempts - 1:
                    logger.warning(f"[NATIVE] Network issue detected (attempt {attempt+1}/{max_attempts}): {e}. Retrying in {attempt + 1}s...")
                    
                    # If we've failed twice, try to recreate the client
                    if attempt >= 2:
                        logger.info("[NATIVE] Persistent connection issues. Resetting UMFutures client session...")
                        self.client = UMFutures(key=self.api_key, secret=self.api_secret, base_url=self.base_url)
                    
                    await asyncio.sleep(attempt + 1)
                    continue
                
                # If it's not a network error or we've exhausted retries, raise it
                if not is_network_error:
                    # Check for Timestamp error (-1021)
                    if "-1021" in err_str and attempt < max_attempts - 1:
                        logger.warning(f"[NATIVE] Timestamp sync issue (-1021). Re-syncing time and retrying (attempt {attempt+1})...")
                        await self._sync_time()
                        continue

                    # Filter out common business errors from being logged as 'Fatal'
                    is_business_error = any(code in err_str for code in ["-2013", "-2012", "-5022"])
                    if is_business_error:
                        logger.warning(f"[NATIVE] Business error (handled by flow): {e}")
                    else:
                        logger.error(f"[NATIVE] Fatal API error (non-retryable): {e}")
                else:
                    logger.error(f"[NATIVE] Exhausted {max_attempts} retries for network error: {e}")
                raise e

    async def _sync_time(self):
        """Internal helper to re-calculate time offset."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(f"{self.base_url}/fapi/v1/time", timeout=5))
            if response.status_code == 200:
                server_time = response.json()["serverTime"]
                local_time = int(time.time() * 1000)
                self.time_offset = server_time - local_time
                logger.info(f"[NATIVE] Time Re-Sync: Offset={self.time_offset}ms")
        except Exception as e:
            logger.warning(f"[NATIVE] Time re-sync failed: {e}")


    async def modify_limit_order(self, symbol: str, side: str, quantity: float, price: float, order_id: str = None, orig_client_id: str = None) -> Dict[str, Any]:
        """
        Specialized: PUT /fapi/v1/order
        Updates an existing order's price and quantity without changing orderId.
        """
        try:
            params = {
                "symbol": symbol,
                "side": side.upper(),
                "quantity": quantity,
                "price": price,
            }
            if order_id:
                params["orderId"] = int(order_id)
            elif orig_client_id:
                params["origClientOrderId"] = orig_client_id
            
            response = await self._execute_with_retry(self.client.modify_order, **params)
            logger.info(f"[NATIVE] Order {order_id or orig_client_id} modified successfully at price {price}")
            return {"success": True, "result": response}
            
        except Exception as e:
            logger.error(f"[NATIVE] Modify Order failed: {e}")
            return {"success": False, "error": str(e)}

    async def create_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, params: dict = None) -> Dict[str, Any]:
        """
        Standard: POST /fapi/v1/order
        Used mainly for taking profit (OTO) with reduceOnly.
        """
        try:
            api_params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": quantity,
                "recvWindow": 10000  # Standard safety window
            }
            if price:
                api_params["price"] = price
            
            # Merge extra params (reduceOnly, newClientOrderId, etc.)
            if params:
                api_params.update(params)
                
            logger.info(f"[NATIVE] Executing order raw params: {api_params}")
            response = await self._execute_with_retry(self.client.new_order, **api_params)
            return {"success": True, "result": response}
            
        except Exception as e:
            logger.error(f"[NATIVE] Create Order failed: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_order(self, symbol: str, order_id: str = None, client_id: str = None) -> Dict[str, Any]:
        """Check order status directly from Binance."""
        if not order_id and not client_id:
            return {"success": False, "error": "Either order_id or client_id must be provided"}
        try:
            params = {"symbol": symbol}
            if order_id: params["orderId"] = order_id
            if client_id: params["origClientOrderId"] = client_id
            
            return await self._execute_with_retry(self.client.get_order, **params)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def cancel_order(self, symbol: str, order_id: str = None, client_id: str = None) -> Dict[str, Any]:
        """Cancel an open order via Binance Native."""
        if not order_id and not client_id:
            return {"success": False, "error": "Either order_id or client_id must be provided"}
        try:
            params = {"symbol": symbol}
            if order_id:
                params["orderId"] = int(order_id)
            elif client_id:
                params["origClientOrderId"] = client_id
            
            response = await self._execute_with_retry(self.client.cancel_order, **params)
            logger.info(f"[NATIVE] Order {order_id or client_id} canceled successfully")
            return {"success": True, "result": response}
        except Exception as e:
            logger.error(f"[NATIVE] Cancel Order failed: {e}")
            return {"success": False, "error": str(e)}


    async def get_available_balance(self, asset: str) -> float:
        """
        GET /fapi/v2/balance — returns availableBalance for the given asset.
        Used by ScheduledScalerBot to check margin availability before placing orders.
        """
        try:
            # Increase recvWindow to be more tolerant of drift
            response = await self._execute_with_retry(self.client.balance, recvWindow=10000)
            for entry in response:
                if entry.get("asset", "").upper() == asset.upper():
                    return float(entry.get("availableBalance", 0.0))
            logger.warning(f"[NATIVE] Asset {asset} not found in balance response.")
            return 0.0
        except Exception as e:
            logger.error(f"[NATIVE] get_available_balance failed: {e}")
            return 0.0

    async def get_open_orders(self, symbol: str) -> list:
        """
        GET /fapi/v1/openOrders — fetches all open standard orders for a symbol.
        Used by ScheduledScalerBot to find nearest open TP (reduceOnly=True LIMIT).
        NOTE: Uses plural get_orders() because get_open_orders() in this lib is singular /fapi/v1/openOrder.
        """
        try:
            logger.info(f"[NATIVE] Fetching open orders for symbol: '{symbol}'")
            # Using get_orders (plural) to avoid 'orderId is mandatory' error from singular get_open_orders
            response = await self._execute_with_retry(self.client.get_orders, symbol=symbol)
            return response if isinstance(response, list) else []
        except Exception as e:
            logger.error(f"[NATIVE] get_open_orders failed for {symbol}: {e}")
            return []

    async def get_position_risk(self, symbol: str) -> list:
        """
        GET /fapi/v2/positionRisk — returns position data for a symbol.
        positionAmt > 0 → LONG (buy), positionAmt < 0 → SHORT (sell), 0 → flat.
        Used by ScheduledScalerBot to infer the current position side.
        """
        try:
            response = await self._execute_with_retry(self.client.get_position_risk, symbol=symbol)
            return response if isinstance(response, list) else []
        except Exception as e:
            logger.error(f"[NATIVE] get_position_risk failed: {e}")
            return []


binance_native = BinanceNativeEngine()
