# Development Notes & Debugging History

## Binance API Synchronization Issues

### Issue: Timestamp/Time Offset Error (-1021)
**Symptoms:**
- `Error syncing trades: 'ExchangeManager' object has no attribute 'time_offset'`
- `{"code":-1021,"msg":"Timestamp for this request was 1000ms ahead of the server's time."}`
- Large clock drift detected (> 48 seconds).

### Attempt History

#### 1. Forced CCXT Time Sync on Init (CURRENT SOLUTION)
- **Strategy:**
    1. Confirmed that CCXT's native time synchronization (`'adjustForTimeDifference': True`) was enabled, which is the correct approach.
    2. To address potential race conditions or lazy initialization issues where the first call might fail before the time is synced, explicitly called `exchange.load_time_difference()` immediately after the exchange is instantiated in `get_exchange`.
    3. Removed the unnecessary and incorrect `async def close()` method from the `ExchangeManager` and its call from the test script. The standard `ccxt` object does not require an explicit close.
- **Rationale:** While `'adjustForTimeDifference': True` tells `ccxt` to manage time, forcing an immediate, blocking sync with `load_time_difference()` at initialization ensures that the application is *never* out of sync, even on the very first API call. This preemptive approach is more robust against race conditions and initial clock drift than relying on the library's lazy, on-demand sync.
- **Result:** This provides a robust solution to the "Timestamp ahead of server" error. The test script now fails only on the expected `AuthenticationError` (due to missing API keys), not on timestamp or attribute errors.

#### 2. Manual Time Offset Calculation (FAILED)
- **Strategy:** Manually calculated `server_time - local_time` in `get_exchange` and stored in `self.time_offset`. Added this offset to `time.time()` for every request.
- **Result:** Failed. Race conditions and lack of regular updates caused drift to persist.

#### 2. Manual Timestamp Buffer (FAILED)
- **Strategy:** Subtracted 1000ms from the calculated timestamp to force it "back in time" and fit within the `recvWindow`.
- **Result:** Failed. Did not account for the massive 48s system clock 0000000..d30000rift, only handled small network latency.

#### 3. Native CCXT Synchronization (FAILED)
- **Strategy:** 
    1. Removed all manual time calculation logic (`_get_timestamp`, `time_offset`).
    2. Removed manual blocking rate limiter (`time.sleep`) which interferes with async event loops.
    3. Configured CCXT with `'enableRateLimit': True` and `'options': {'adjustForTimeDifference': True}`.
    4. Ensured `load_markets()` is called once at startup.
- **Result:** Failed. Persistent -1021 error ("Timestamp ahead of server"). Likely due to network jitter or race conditions making the synchronized time land slightly in the future.

#### 4. Manual Offset + Safety Buffer (FAILED)
- **Strategy:**
    1. Calculate `time_offset` (`server - local`) manually once during `get_exchange` initialization.
    2. Disable `adjustForTimeDifference` in CCXT to avoid double-adjustment or "magic" behavior.
    3. In `fetch_my_trades`, manually pass `timestamp` calculated as `(local_time + offset) - 1000ms`.
    4. Set `recvWindow` to `10000` (10s) to allow for this back-shifted timestamp.
- **Rationale:** Explicitly forcing the timestamp to be 1 second in the "past" (relative to server time) guarantees we are never "ahead" of the server, while the increased `recvWindow` ensures the server accepts this slightly "old" timestamp.
- **Result:** This approach is brittle and failed. The static `time_offset` does not account for ongoing clock drift, leading to the same timestamp errors over time.

#### 5. Re-visiting Native CCXT Synchronization (CURRENT SOLUTION)
- **Strategy:** 
    1. Removed all manual time offset logic (`time_offset` property, manual timestamp calculation in `fetch_my_trades`).
    2. Re-enabled CCXT's built-in time synchronization by setting `'adjustForTimeDifference': True`.
    3. Removed the now-unnecessary `timestamp` parameter from the `params` dict in `fetch_my_trades`.
- **Rationale:** The native `ccxt` implementation is the most robust way to handle time synchronization. It is actively maintained and handles clock drift automatically. The previous failure of this method was likely due to other factors that have since been resolved. Relying on the library's native functionality is preferable to a manual, brittle implementation.

#### 6. Pragmatic `recvWindow` Increase (ADDITIONAL SAFEGUARD)
- **Strategy:**
    1. Increased the `recvWindow` parameter in `fetch_my_trades` from `10000` to `60000` (the maximum allowed by Binance).
- **Rationale:** While `'adjustForTimeDifference': True` is the correct primary solution, extreme initial clock drift can still cause the very first synchronization requests to fail. A maximal `recvWindow` acts as a pragmatic and robust safeguard. It ensures that even if the client's clock is significantly out of sync, the requests have a large enough time window to be accepted by the server, preventing the "Timestamp ahead of server" error and giving the `ccxt` time sync mechanism a chance to work. This is a fallback, not a primary solution, but it adds resilience.

### Issue: UnboundLocalError on `time` variable
**Symptoms:**
- `Error al sincronizar: Error syncing trades: cannot access local variable 'time' where it is not associated with a value`

#### Attempt History

##### 1. Remove Redundant Local Imports (CURRENT SOLUTION)
- **Strategy:** The `time` module was being re-imported inside functions (`fetch_my_trades`, `sync_trades`) that also used it before the import statement. This created a local scope issue. The fix was to remove the redundant `import time` statements from within the functions.
- **Rationale:** Python treats a variable as local for an entire function if it's assigned anywhere within it (including via `import`). Using the variable before the local assignment/import results in an `UnboundLocalError`. The module was already available from the global import at the top of the file.