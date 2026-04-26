# Incident Report: 2026-04-26 - USDC Symbol and Leverage Detection Issues

## Problem
1.  **Invalid Symbol Error**: The Native Execution Engine rejected symbols like `1000PEPE/USDC:USDC` because they weren't correctly normalized to Binance's native format (`1000PEPEUSDC`).
2.  **Leverage 1x Bug**: Leverage detection failed for USDC symbols because the API returned an empty risk list for inactive positions, defaulting to `1x` margin requirement and causing unnecessary "Insufficient Margin" errors.
3.  **NameError in Scaler Bot**: A `NameError: name 'min_qty' is not defined` crashed the bot cycle due to incorrect variable scoping.

## Solution
1.  **Robust Normalization**: Implemented a centralized `get_native_symbol` method that correctly strips settlement info and slashes.
2.  **Smart Leverage Fallback**: Added a multi-level detection logic (Native -> CCXT -> Config Default) to ensure leverage is always accurately detected or reasonably assumed (3.0x).
3.  **Variable Initialization**: Fixed scoping in `ScheduledScalerBot` to ensure `min_qty` is always defined.

## Impact
- **Improved Reliability**: Bots can now correctly trade USDC-settled symbols.
- **Accurate Margin Calculation**: Higher leverage is now correctly detected, reducing false "Insufficient Margin" warnings.
- **System Stability**: Fixed a crash in the Scaler Bot cycle.

## Tests
- Verified symbol normalization: `1000PEPE/USDC:USDC` -> `1000PEPEUSDC`.
- Verified leverage fallback: Correctly uses `3.0x` when API data is unavailable.
- Verified Scaler Bot logic: `min_qty` is correctly defined and used.
