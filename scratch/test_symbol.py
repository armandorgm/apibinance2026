
import asyncio
import os
import sys

# Change to backend directory to load .env
os.chdir(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

from app.core.binance_native import binance_native
from app.core.exchange import exchange_manager

async def test_symbol():
    symbol_ccxt = "1000PEPE/USDC:USDC"
    
    # Current implementation
    native_current = exchange_manager.get_native_symbol(symbol_ccxt)
    print(f"CCXT: {symbol_ccxt} -> Native Current: {native_current}")
    
    # Try fetching risk with current
    try:
        risk_current = await binance_native.get_position_risk(native_current)
        print(f"Risk (Current): {'Found' if risk_current else 'Not Found'}")
        if risk_current:
            print(f"Leverage (Current): {risk_current[0].get('leverage')}")
            print(f"Full response (Current): {risk_current[0]}")
    except Exception as e:
        print(f"Error (Current): {e}")

    # Try fetching risk with "native" (with slash)
    native_with_slash = symbol_ccxt.split(':')[0]
    print(f"CCXT: {symbol_ccxt} -> Native With Slash: {native_with_slash}")
    try:
        risk_slash = await binance_native.get_position_risk(native_with_slash)
        print(f"Risk (Slash): {'Found' if risk_slash else 'Not Found'}")
        if risk_slash:
            print(f"Leverage (Slash): {risk_slash[0].get('leverage')}")
    except Exception as e:
        print(f"Error (Slash): {e}")

if __name__ == "__main__":
    asyncio.run(test_symbol())
