import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.binance_native import binance_native
from app.core.exchange import exchange_manager

async def debug_leverage(symbol: str):
    print(f"--- Debugging Leverage for {symbol} ---")
    native_symbol = symbol.replace("/", "").replace(":USDC", "").replace(":USDT", "")
    print(f"Native symbol: {native_symbol}")
    
    try:
        print("\n--- BINANCE NATIVE (positionRisk) ---")
        positions = await binance_native.get_position_risk(native_symbol)
        if positions:
            pos = positions[0]
            print(f"Full Position: {pos}")
            leverage = pos.get("leverage")
            if leverage is None:
                notional = abs(float(pos.get("notional", 0.0)))
                initial_margin = float(pos.get("initialMargin", 0.0))
                if initial_margin > 0:
                    leverage = round(notional / initial_margin)
                else:
                    leverage = 1.0
            print(f"Detected/Calculated Leverage: {leverage}")
        
        print("\n--- CCXT (fetch_positions) ---")
        ccxt_positions = await exchange_manager.get_open_positions(symbol)
        if ccxt_positions:
            cpos = ccxt_positions[0]
            print(f"CCXT Position: {cpos}")
            print(f"CCXT Leverage: {cpos.get('leverage')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    symbol = "1000PEPE/USDC"
    asyncio.run(debug_leverage(symbol))
