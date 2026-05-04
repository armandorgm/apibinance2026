# Incident Report: 2026-05-04 - Reactor Symbol Mismatch

## Problem
The `CloseFillReactor` (Bot B) was skipping follow-up chases because of a symbol formatting mismatch.
- Closed symbol (from WebSocket/CCXT): `1000PEPE/USDC:USDC`
- Enabled symbol (from User Config): `1000PEPE/USDC`
The reactor was using a strict string comparison on "normalized" symbols, but `normalize_symbol` didn't handle the case where a slash was present but the settle suffix was missing, leading to `1000PEPE/USDC:USDC != 1000PEPE/USDC`.

## Solution
1. **Robust Comparison**: Modified `CloseFillReactor.on_position_closed` to compare **Market IDs** (e.g., `1000PEPEUSDC`) instead of CCXT symbols. Market IDs are extracted using `exchange_manager.get_market_id`, which is immune to formatting variations.
2. **Heuristic Improvement**: Enhanced `exchange_manager.normalize_symbol` heuristic fallback to correctly append the `:USDC` or `:USDT` suffix even if the input symbol already contains a slash (e.g., `BASE/QUOTE` -> `BASE/QUOTE:QUOTE`).

## Impact
- The Reactor now correctly triggers follow-up cycles regardless of whether the user provided the full CCXT string or a simplified Binance-style pair.
- Improved overall robustness of symbol handling across the backend.

## Tests
- Verified syntax via `py_compile`.
- Logic review: `get_market_id` correctly maps both formats to the same Binance ID.
