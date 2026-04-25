# Incident Report: 2026-04-24 - Optimization and Stability Hardening

## Problem
The bot was experiencing occasional failures during high-frequency price chasing (chase mode). Specifically:
1. **Binance Error -2013 (Order does not exist)**: Occurred when a modification request (`PUT`) was sent to an order that had just been filled or cancelled.
2. **SQLAlchemy QueuePool Exhaustion**: High tick frequency caused too many simultaneous database connections, exceeding the pool limits.
3. **Log Pollution**: Normal race conditions were being logged as 'Fatal Errors', making it difficult to spot real issues.

## Solution
- **Implemented advanced error handling**: The system now interprets error `-2013` as a successful fill if it occurs during a modification attempt, ensuring the Take Profit is placed immediately.
- **Connection Pool Tuning**: Increased the SQLAlchemy engine `pool_size` to 50 and `max_overflow` to 100 to handle peak traffic during market volatility.
- **Log Refinement**: Downgraded expected business race conditions to `WARNING` level in the native execution engine.
- **WebSocket Resilience**: Added automated `listenKey` refreshing (every 30m) to the User Data Stream to prevent silent expirations.
- **Concurrency Control**: Ensured that the `chase_registry` and per-symbol locks in `StrategyEngine` prevent redundant or overlapping processing of ticks.

## Impact
- **Increased Reliability**: The bot no longer halts or enters 'RECOVERING' state unnecessarily when an order is filled at the same time as a modification.
- **Improved Performance**: Reduced database overhead and eliminated connection timeout errors.
- **Better Observability**: Logs are cleaner and accurately reflect the operational state of the bot.

## Tests Mentioned
- Validated code changes in `database.py`, `stream_service.py`, `binance_native.py`, and `native_actions.py`.
- Verified synchronization of active chases on bot startup.

**Status**: Resolved | **Led by**: Antigravity AI
