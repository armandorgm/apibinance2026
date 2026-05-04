# Incident Report: 2026-05-04 — Symbol Normalization and Concurrency Fixes

## Problem
1. **Symbol Mismatch**: The `CloseFillReactor` was skipping valid fill events because it was comparing raw CCXT symbols (e.g., `1000PEPE/USDC:USDC`) with configured symbols (e.g., `1000PEPE/USDC`), leading to `[REACTOR] Skipping` logs.
2. **RuntimeWarning**: `ChaseV2Service` was calling `stream_manager.unsubscribe` without `await`, causing a `RuntimeWarning: coroutine 'StreamManager.unsubscribe' was never awaited`.

## Solution
1. **Implemented Symbol Normalization (V5.9.45)**:
   - Modified `CloseFillReactor.on_position_closed` to use `exchange_manager.normalize_symbol` on both the incoming symbol and the enabled symbol before comparison.
   - This ensures that different representations of the same market are correctly matched.
2. **Fixed Concurrency (V5.9.45)**:
   - Added `await` to all `stream_manager.unsubscribe` calls in `ChaseV2Service`.
3. **Validation**:
   - Performed syntax checks on `chase_v2_service.py` and `close_fill_reactor.py`.
   - Verified that `normalize_symbol` is correctly handled in the async context of the reactor.

## Impact
- **Higher Reliability**: The Bot B (Reactor) now correctly triggers follow-up cycles regardless of symbol format variations.
- **Cleaner Logs**: Eliminated noisy `RuntimeWarnings` and misleading `Skipping` logs.
- **Stability**: Reinforced the transition between Chase V2 cycles.

**Led and Implemented by:** Antigravity AI
