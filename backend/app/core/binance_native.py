import asyncio
import hmac
import hashlib
import time
import requests
from typing import Dict, Any, Optional
from binance.um_futures import UMFutures
from app.core.config import settings
from app.core.logger import logger

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
        
        # Initialize the official client
        self.client = UMFutures(
            key=self.api_key,
            secret=self.api_secret,
            base_url=self.base_url
        )

    async def modify_limit_order(self, symbol: str, side: str, quantity: float, price: float, order_id: str = None, orig_client_id: str = None) -> Dict[str, Any]:
        """
        Specialized: PUT /fapi/v1/order
        Updates an existing order's price and quantity without changing orderId.
        """
        try:
            # Wrap synchronous call in a thread
            loop = asyncio.get_event_loop()
            
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
            
            # log API call weight if needed in future
            response = await loop.run_in_executor(None, lambda: self.client.modify_order(**params))
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
            loop = asyncio.get_event_loop()
            
            api_params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": quantity,
            }
            if price:
                api_params["price"] = price
            
            # Merge extra params (reduceOnly, newClientOrderId, etc.)
            if params:
                api_params.update(params)
                
            response = await loop.run_in_executor(None, lambda: self.client.new_order(**api_params))
            return {"success": True, "result": response}
            
        except Exception as e:
            logger.error(f"[NATIVE] Create Order failed: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_order(self, symbol: str, order_id: str = None, client_id: str = None) -> Dict[str, Any]:
        """Check order status directly from Binance."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.get_order(symbol=symbol, orderId=order_id, origClientOrderId=client_id))
            return {"success": True, "result": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Singleton managed by ExchangeManager
binance_native = BinanceNativeEngine()
