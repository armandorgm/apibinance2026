# Binance API Changelog (AI-Optimized)

History of changes to Binance Futures (USDⓈ-M, COIN-M), Options, and Portfolio Margin (PAPI).

## 2026-04-15 [Options]
* Weight: DELETE /eapi/v1/batchOrders (1 -> 5).

## 2026-04-14 [PAPI] (Eff: 2026-04-28)
+ NEW REST: /papi/v1/um/algo/order, /papi/v1/um/algo/algoOrder, etc.
+ NEW WS: ALGO_UPDATE event.
- DEPRECATED: /papi/v1/um/conditional/* (replaced by algo endpoints).

## 2026-04-13 [PAPI/Pro]
+ NEW REST: /sapi/v1/portfolio/margin-call-level (POST/GET/DELETE).

## 2026-04-10 [COIN-M/PAPI] (Eff: 2026-04-14)
* Rule: CM dualSidePosition must match UM. Rejected if different.
* WS: Liquidations (!forceOrder@arr) pushed only largest one in 1000ms.

## 2026-04-09 [PAPI]
* WS: Margin Order Update (executionReport) fields added: Cs, pl, pL, pY, eR.

## 2026-04-08 [PAPI]
+ NEW REST: POST /papi/v1/um/stock/contract (TradFi-Perps contract).

## 2026-04-06 [All Futures/PAPI]
* REST: ForceOrders endpoints now only support past 90 days query.

## 2026-04-02 [USD-M Futures]
- WS: Legacy URL decommissioning date: 2026-04-23.

## 2026-03-19 [All Futures]
* HIST: /historicalTrades data availability reduced (3m -> 1m).

## 2026-03-16 [USD-M Futures]
* WS: Mark Price Stream adds `ap` (moving average).

## 2026-03-11 [Options] (Eff: 2026-03-19)
+ STP: Self-Trade Prevention added (EXPIRE_MAKER/TAKER/BOTH).
+ STATUS: NEW EXPIRED_IN_MATCH.
* REST: selfTradePreventionMode param added to order endpoints (POST/GET/PUT/DELETE /eapi/v1/order*).
* WS: Field `V` in ORDER_TRADE_UPDATE.

## 2026-03-05 [USD-M Futures]
* WS: URL PATH added (/public, /market, /private base paths).

## 2026-01-09 [PAPI/Pro]
+ NEW REST: /sapi/v1/portfolio/delta-mode (POST/GET).

## 2026-01-07 [Options]
+ NEW REST: GET /eapi/v1/commission.

## 2025-12-29 [USD-M Futures]
- REMOVED: MAX_NUM_ALGO_ORDERS from exchangeInfo (Global limit: 200).
* WS: Field `nq` in @aggTrade (excludes RPI orders).

## 2025-12-11 [USD-M Futures]
+ NEW REST: /fapi/v1/tradingSchedule, /fapi/v1/stock/contract.
+ NEW WS: tradingSession.

## 2025-12-10 [USD-M Futures]
- DEPRECATED: CONDITIONAL_ORDER_TRIGGER_REJECT (moved to ALGO_UPDATE).

## 2025-12-09 [COIN-M Futures]
* WS: er (expire reason) field available in ORDER_TRADE_UPDATE.

## 2025-11-25 [USD-M Futures] (Eff: 2025-11-26)
+ REST: /fapi/v1/commissionRate (includes RPI fee).
+ NEW REST/WS: RPI Depth (/fapi/v1/rpiDepth, @rpiDepth@500ms).

## 2025-11-19 [USD-M Futures]
+ NEW REST: GET /fapi/v1/symbolAdlRisk.

## 2025-11-18 [USD-M Futures]
+ NEW: RPI Orders introduced.
* REST: /fapi/v1/order* supports RPI TIF.
* WS: IsRPITrade boolean added. RPI orders excluded from depth/ticker.

## 2025-11-12 [Options]
* INFO: Options system rebuild. New Demo API env launched.

## 2025-11-10 [PAPI]
- DEPRECATED: BFUSD mint/redeem (migrated to Earn).

## 2025-11-06 [USD-M Futures] (Eff: 2025-12-09)
* MIGRATION: Conditional orders (STOP/TAKE_PROFIT/TRAILING) -> Algo Service.
+ NEW REST: /fapi/v1/algoOrder, /fapi/v1/algoOpenOrders, etc.
- BLOCKED: Old endpoints (/fapi/v1/order) return -4120 for SL/TP orders.
+ WS: ALGO_UPDATE event added.

## 2025-10-21 [All/PAPI] (Eff: 2025-10-23)
- REMOVED: priceMatch OPPONENT_10/20 temporarily removed.

## 2025-10-20 [USD-M Futures]
* WS: er (expire reason) field available in ORDER_TRADE_UPDATE.

## 2025-10-14 [USD-M Futures]
* ERR: -1008 message updated (system-level protection).

## 2025-10-09 [All Futures]
+ SYMBOLS: Chinese characters supported (requires UTF-8 URL encoding).

## 2025-08-11 [PAPI]
- DEPRECATED: BFUSD mint/redeem (migrated to Earn on 2025-08-13).

## 2025-07-25 [USD-M Futures]
+ ERR: -4109 (Account inactive). Transfer funds to reactivate.

## 2025-07-02 [USD-M Futures]
* REST: /futures/data/openInterestHist adds CMCCirculatingSupply.
* WS: Max streams per connection 200 -> 1024.

## 2025-04-23 [USD-M Futures]
+ NEW REST: /fapi/v1/insuranceBalance, /fapi/v1/constituents.

## 2025-04-15 [PAPI/Pro]
+ NEW REST: /sapi/v1/portfolio/earn-asset-transfer, /sapi/v1/portfolio/earn-asset-balance.

## 2025-02-28 [PAPI]
+ NEW REST: GET /sapi/v1/portfolio/pmloan-history.

## 2025-02-20 [COIN-M Futures] (Eff: 2025-02-25)
+ NEW WS API: wss://ws-dapi.binance.com/ws-dapi/v1 (Order placement via WS).

## 2025-01-20 [PAPI]
+ NEW REST: GET /papi/v1/portfolio/negative-balance-exchange-record.

## 2025-01-13 [All Futures] (Eff: 2025-01-14)
* LIMIT: /historicalTrades limit reduced 1000 -> 500 (default 100).

## 2025-01-06 [PAPI]
+ NEW REST: GET papi/v1/rateLimit/order.

## 2024-12-19 [PAPI/Pro]
+ NEW REST: BFUSD mint/redeem.

## 2024-12-17 [Options]
+ NEW REST: GET /eapi/v1/blockTrades.
* WS: Field `X` (trade type) in @trade.

## 2024-12-02 [USD-M Futures]
+ ERR: -4116 (Duplicate ClientOrderId), -4117 (Stop trigger in process).

## 2024-11-04 [All Futures]
- DEPRECATED: /fapi/v1/pmExchangeInfo, /dapi/v1/pmExchangeInfo (on 2024-11-15).

## 2024-11-01 [Options]
+ NEW REST: Block trade endpoints (create/execute/query).

## 2024-10-29 [PAPI/Pro]
* LIMIT: /repay-futures-switch rate limit -> 20/day.

## 2024-10-24 [Options] (Eff: 2024-10-28)
- REMOVED: `id` fields from contracts/assets/symbols in exchangeInfo and WS.

## 2024-10-21 [All Futures] (Eff: 2024-10-30)
* LIMIT: /userTrades only supports last 6 months.
+ NEW REST: Async download endpoints for order/trade history.

## 2024-10-15 [PAPI/Pro]
+ NEW REST: SPAN Account Info, Balance Info, Async download for UM history.

## 2024-10-14 [USD-M Futures]
* LIMIT: /convert/getQuote rate limit -> 360/h, validTime restricted to 10s.

## 2024-10-11 [COIN-M Futures]
+ STP: Self-Trade Prevention introduced.
+ STATUS: NEW EXPIRED_IN_MATCH.
+ NEW: Price Match support (OPPONENT, QUEUE, etc.).
* REST/WS: params/fields added for STP and priceMatch.

## 2024-10-10 [USD-M Futures]
* LIMIT: /aggTrades history limited to 1 year. /positionMargin/history limited to 30 days.

## 2024-10-08 [COIN-M Futures]
* LIMIT: /allOrders, /userTrades period max 7 days (default 7d). AllOrders/Order history max 3 months.

## 2024-09-27 [All Futures]
- DEPRECATED WS: listenkey@account, @balance, @position requests.

## 2024-09-19 [PAPI]
+ NEW REST: POST /papi/v1/margin/repay-debt.

## 2024-09-06 [PAPI]
+ NEW: priceMatch support for PAPI UM orders (place/modify).
* WS: Field `pm` added to order update events.

## 2024-09-05 [PAPI Pro]
+ NEW REST: GET /sapi/v2/portfolio/collateralRate.

## 2024-09-03 [USD-M Futures]
+ NEW WS: TRADE_LITE event (lower latency trade-only updates).

## 2024-08-26 [USD-M Futures]
+ NEW REST: Future Convert endpoints (GET/POST).

## 2024-08-23 [PAPI]
+ NEW REST: Toggle BNB Burn, AccountConfig, SymbolConfig, /papi/v2/um/account (performance focus).

## 2024-08-07 [USD-M Futures] (Eff: 2024-09-03)
* WEIGHT: account/balance/position endpoints increased (5->10).
- DEPRECATED WS: <listenKey>@account, @balance, @position requests.

## 2024-07-24 [USD-M Futures]
+ NEW: /fapi/v3/account, /fapi/v3/balance, /fapi/v3/positionRisk (performance focus).
+ NEW REST: /fapi/v1/symbolConfig, /fapi/v1/accountConfig.
- DEPRECATED: fapi/v2 account/balance/positionRisk.

## 2024-07-17 [PAPI]
- REMOVED: `marginAsset` from /papi/v1/userTrades response.

## 2024-06-19 [USD-M Futures]
- REMOVED: `marginAsset` from /fapi/v1/userTrades response.

## 2024-05-22 [USD-M Futures]
+ NEW REST/WS API: Toggle BNB Burn (/fapi/v1/feeBurn).

## 2024-04-19 [USD-M Futures] (Eff: 2024-04-25)
* WS/REST: `listenKey` field integrated into Keep-alive response.

## 2024-04-09 [All/PAPI]
* GTC: 1-year validity period for GTC orders. Auto-canceled if older.

## 2024-04-01 [USD-M Futures]
+ NEW WS API: wss://ws-fapi.binance.com/ws-fapi/v1 (Order placement via WS).

## 2024-03-11 [USD-M Futures]
+ NEW REST: GET /fapi/v1/rateLimit/order.

## 2024-02-09 [USD-M Futures]
* WS: Upgrade - Server pings every 3m. Client must copy payload in pong.

## 2024-01-24 [USD-M Futures]
* TESTNET: WS baseurl updated to "wss://fstream.binancefuture.com".

## 2024-01-19 [PAPI]
+ NEW REST: UM/CM order modification support (PUT).

## 2024-01-11 [PAPI]
+ STP: Self-Trade Prevention introduced. New status EXPIRED_IN_MATCH.
+ GTD: Good Till Date support added for UM orders.
+ NEW: breakEvenPrice added to account/positionRisk responses.
* WS: Fields `V`, `gtd`, `bep` added to events.

## 2024-01-08 [USD-M Futures] (Eff: 2023-01-11)
* REST: UM Order modify (PUT) adds `priceMatch` support.

## 2023-12-12 [USD-M Futures]
* WS: !bookTicker update speed -> every 5s (Dec 20). Individual symbols remain real-time.

## 2023-11-15 [USD-M Futures]
+ NEW REST: GET /fapi/v2/ticker/price (lower latency).
- DEPRECATED WS: domain wss://fstream-auth.binance.com (Dec 15). Use wss://fstream.binance.com.

## 2023-11-01 [USD-M/COIN-M]
* REST: /fundingRate adds `markPrice` field.
+ NEW REST: GET /futures/data/basis (USD-M).

## 2023-10-19 [All/Options]
+ NEW REST: /futures/data/delivery-price.
* WEIGHT: Market data endpoints IP weight updated to 1000/5min/IP.
* WS: Options service upgrade (pings, connection formats).

## 2023-10-16 [All Futures]
+ NEW REST: GET /fapi/v1/constituents, GET /dapi/v1/constituents.

## 2023-10-11 [USD-M Futures]
* WEIGHT: Download endpoints (order/trade/income async) weight updated 5->1000.

## 2023-09-25 [All Futures]
+ NEW REST: GET /fapi/v1/fundingInfo, GET /dapi/v1/fundingInfo.

## 2023-09-22 [PAPI]
* REST/WS: `liquidationPrice`, `notionalCoef` added. `updateId U` added to balance events.

## 2023-09-20 [All Futures]
* REST: ticker/bookTicker response adds `lastUpdateId`.

## 2023-09-19 [USD-M Futures]
+ ERR: -1008 (Server overloaded) for order/batchOrder endpoints.

## 2023-09-07 [COIN-M Futures]
+ NEW REST: Async download for COIN-M transaction history.

## 2023-09-05 [USD-M Futures]
+ ENABLED: STP, Price Match, GTD, Breakeven Price.

## 2023-09-04 [PAPI]
* LIMIT: Overall PAPI order ratelimit reduced 2400 -> 1200 /min.

## 2023-08-31 [All Futures]
* WS: Ping frame frequency 5m -> 3m. Pong window 15m -> 10m.

## 2023-08-29 [Options/USD-M]
+ STP: Self-Trade Prevention introduced (USD-M).
+ WS: `riskLevel` field and RISK_LEVEL_CHANGE event added (Options).

## 2023-08-25 [COIN-M Futures]
* WS: Service upgrade - illegal_parameter paths and trailing / no longer supported.

## 2023-08-19 [USD-M Futures]
* WS: Service upgrade - trailing / no longer supported.

## 2023-08-18 [PAPI]
+ NEW REST: Query Margin Account Order/Trades endpoints.

## 2023-08-14 [All Futures]
* REST: /income adds `page` parameter for pagination.

## 2023-07-28 [PAPI]
+ NEW REST: POST /papi/v1/asset-collection.

## 2023-07-21 [Options]
+ NEW REST: Async download for Options transaction history.

## 2023-07-20 [PAPI]
+ NEW REST: /adlQuantile (UM/CM).

## 2023-07-19 [COIN-M Futures]
* REST: /leverageBracket adds `notionalCoef`.

## 2023-07-18 [PAPI/USD-M]
+ NEW REST: /repay-futures-switch, /repay-futures-negative-balance (PAPI).
* REST: USD-M /leverageBracket adds `notionalCoef`.

## 2023-07-13 [Options/PAPI]
* WS: Options streams timestamps added. PAPI riskLevelChange event added.

## 2023-07-12 [COIN-M Futures]
+ NEW: breakEvenPrice `bep` added to position reports (REST/WS).

## 2023-07-11 [PAPI]
+ NEW REST: POST /papi/v1/ping.

## 2023-07-04 [USD-M Futures]
* LIMIT: /order, /allOrders, /userTrades restricted to recent 3 months. Use async download for older.

## 2023-06-28 [USD-M Futures] (Eff: 2023-07-15)
- DEPRECATED: fapi v1 account/balance/positionRisk. Use v2.

## 2023-06-22 [All Futures]
- WS: Raw stream /ws?<streamName> no longer supported. Invalid JSON causes disconnection.

## 2023-06-19 [PAPI]
* REST: Conditional order endpoints add `CONTRACT_PRICE`, `priceProtect`.

## 2023-06-14 [All Futures]
* WS: markPrice stream adds `i` (index price). NEW !assetIndex stream (USD-M).

## 2023-06-01 [PAPI]
+ NEW REST: /um/income, /cm/income, /um/account, /cm/account.

## 2023-05-31 [USD-M Futures]
+ WS: CONDITIONAL_ORDER_TRIGGER_REJECT event added.

## 2023-05-05 [USD-M Futures]
+ NEW REST: UM limit order modify (PUT /fapi/v1/order*).
+ WS: NEW `AMENDMENT` execution type.

## 2023-04-17 [All Futures]
* RULE: recvWindow check performed at matching engine level. New errors -4188/-5028.

## 2023-03-28 [USD-M Futures]
* REBATE: Referral rebates now aggregated every 20m in ACCOUNT_UPDATE (not real-time).

## 2023-03-08 [USD-M Futures] (Eff: 2023-03-22)
* FOK/GTX: If execution fails, order is rejected directly (no WS message, not in history).

## 2022-12-16 [All Futures]
+ NEW WS: !contractInfo (symbol info updates).

## 2022-11-29 [All Futures]
+ NEW WS: STRATEGY_UPDATE, GRID_UPDATE events.

## 2021-05-06 [USD-M Futures]
+ NEW: Multi-Assets margin mode introduced.
+ NEW REST: /fapi/v1/multiAssetsMargin.
* WS: ACCOUNT_UPDATE adds auto-exchange reason `m`.

## 2020-12-08 [USD-M Futures]
+ NEW: Continuous contract kline streams/endpoints.
+ ENUM: PERPETUAL, CURRENT_MONTH, NEXT_QUARTER, etc.

## 2020-05-18 [USD-M Futures]
+ NEW: `closePosition=true` support for SL/TP Market orders.

## 2020-04-06 [USD-M Futures]
+ NEW: Hedge Mode support.
* REST: /positionSide/dual to change mode.

## 2019-12-12 [USD-M Futures]
+ NEW REST: DELETE /fapi/v1/allOpenOrders, batchOrders DELETE.
* REDUCE_ONLY: Supported in TP/SL orders.

## 2019-10-08 [USD-M Futures]
* REDUCE_ONLY: Supported in LIMIT orders.
+ NEW: TAKE_PROFIT order type.
