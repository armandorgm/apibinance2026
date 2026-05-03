# Incident Report: 2026-04-25 - Scaler Bot Margin Error

## Problem
The `ScheduledScalerBot` (Bot C) was consistently failing with the error "Margin is insufficient" when attempting to open positions. Investigation revealed that the bot was sending the contract quantity (e.g., 1302 contracts) as the `amount` parameter to `ChaseV2Service.init_chase`. However, `ChaseV2Service` expects `amount` to be the USD Notional value.

This resulted in `ChaseV2Service` calculating a quantity of `1302 / 0.0038 ≈ 342,631` contracts, which exceeded the account's available margin.

## Solution
1. **Implemented Unit Sync**: Modified `backend/app/services/scheduled_scaler_bot.py` to calculate the USD Notional (`min_qty * current_price`) before invoking `init_chase`.
2. **Enhanced Debugging**: Confirmed that `ChaseV2Service` has sufficient logging to track the conversion of amount to quantity.
3. **Verification**: Successfully executed a full cycle for `1000PEPE/USDC` on the backend. The logs confirmed an entry of `1303` contracts (minimum notional) and a successful Take Profit placement.

## Impact
- **Stability**: Scaler Bot now operates within normal margin limits.
- **Safety**: Prevented potential accidental over-leveraging due to unit mismatches.
- **Observability**: Improved logs allow for faster diagnosis of similar quantity issues in the future.

## Tests
- [x] Manual backend execution with real-time logs.
- [x] Verification of `qty` math: `5.005 USD / 0.0038407 Price = 1303.148 Qty` (Correct).
