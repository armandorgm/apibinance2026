import asyncio
import json
from app.core.binance_native import binance_native

async def debug_leverage():
    symbol = "ETHUSDC"
    print(f"Fetching position risk for {symbol}...")
    positions = await binance_native.get_position_risk(symbol)
    print("Full Position Risk Response:")
    print(json.dumps(positions, indent=2))
    
    if positions:
        leverage = positions[0].get("leverage")
        print(f"\nExtracted leverage field: {leverage} (Type: {type(leverage)})")
    else:
        print("\nNo positions found.")

if __name__ == "__main__":
    asyncio.run(debug_leverage())
