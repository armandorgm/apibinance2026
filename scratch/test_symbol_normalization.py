import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

def mock_get_native_symbol(symbol: str) -> str:
    # Logic from exchange.py
    base_quote = symbol.split(':')[0]
    native = base_quote.replace('/', '')
    return native.upper()

def old_heuristic(symbol: str) -> str:
    # Logic that was failing
    clean = symbol.replace('/', '').replace(':USDC', '').replace(':USDT', '')
    return clean.upper()

test_symbols = [
    "BTC/USDT:USDT",
    "1000PEPE/USDT:USDT",
    "1000PEPE/USDC:USDC",
    "ETH/USDT",
    "PEPE/USDT:USDT"
]

print(f"{'Original':<25} | {'Old Heuristic':<20} | {'New Native Symbol':<20}")
print("-" * 70)
for sym in test_symbols:
    old = old_heuristic(sym)
    new = mock_get_native_symbol(sym)
    print(f"{sym:<25} | {old:<20} | {new:<20}")
