# Binance API - Complete Guide to Pending Orders & Take Profit / Stop Loss Endpoints

*Last Updated: April 2, 2026*

---

## TABLE OF CONTENTS
1. [SPOT Trading Endpoints](#spot-trading-endpoints)
2. [FUTURES Trading Endpoints](#futures-trading-endpoints)
3. [Order Types Reference](#order-types-reference)
4. [Key Terms & Definitions](#key-terms--definitions)

---

## SPOT TRADING ENDPOINTS

### 1. NEW ORDER - Single Order
**Endpoint:** `POST /api/v3/order`

**Purpose:** Create a single new order (LIMIT, MARKET, STOP_LOSS, TAKE_PROFIT, etc.)

**Key Parameters for Pending/TP/SL Orders:**
- `type`: Order type (STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT)
- `stopPrice`: Trigger price for STOP_LOSS, TAKE_PROFIT orders
- `trailingDelta`: For trailing stop orders (optional, alternative to stopPrice)
- `price`: Limit price (required for LIMIT variants)

**Response Contains:**
- `stopPrice`: Shows the trigger price if applicable
- `trailingDelta`: Delta value if set
- `type`: Order type

---

### 2. TEST NEW ORDER
**Endpoint:** `POST /api/v3/order/test`

**Purpose:** Validate order parameters without executing

**Parameters:** Same as POST /api/v3/order

---

### 3. CANCEL ORDER
**Endpoint:** `DELETE /api/v3/order`

**Purpose:** Cancel an existing order (including pending orders)

**Key Parameters:**
- `orderId` or `origClientOrderId`: Identify which order to cancel

---

### 4. CANCEL ALL OPEN ORDERS
**Endpoint:** `DELETE /api/v3/openOrders`

**Purpose:** Cancel all open orders on a symbol (includes order lists)

---

### 5. CANCEL & REPLACE ORDER
**Endpoint:** `POST /api/v3/order/cancelReplace`

**Purpose:** Cancel existing order and place new order simultaneously

**Key for Pending Orders:**
- Can replace STOP_LOSS/TAKE_PROFIT orders with new conditions

---

### 6. ORDER AMEND - KEEP PRIORITY
**Endpoint:** `PUT /api/v3/order/amend/keepPriority`

**Purpose:** Reduce quantity of existing open order while maintaining queue position

---

## ORDER LISTS (Multiple Orders)

### 7. NEW OCO (ONE-CANCELS-OTHER) - DEPRECATED
**Endpoint:** `POST /api/v3/order/oco`

**Purpose:** Create 2-order list (limit + stop-loss leg)

**Stop Loss & Take Profit Orders Here:**
- One leg: `STOP_LOSS` or `STOP_LOSS_LIMIT` (required)
- Other leg: `LIMIT_MAKER` or `TAKE_PROFIT_LIMIT` (required)

**Parameters:**
- `stopPrice`: Stop loss trigger price
- `price`: Limit price
- `stopLimitPrice`: Limit price for stop loss leg
- `trailingDelta`: For trailing stops

---

### 8. NEW ORDER LIST - OCO
**Endpoint:** `POST /api/v3/orderList/oco`

**Purpose:** Place one-cancels-the-other pair (modern version)

**Order Type Combinations:**
- **Above Order:** STOP_LOSS, STOP_LOSS_LIMIT, LIMIT_MAKER, TAKE_PROFIT, TAKE_PROFIT_LIMIT
- **Below Order:** STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT

**Parameters:**
- `aboveStopPrice` / `belowStopPrice`: Trigger prices
- `abovePrice` / `belowPrice`: Limit prices
- `aboveTrailingDelta` / `belowTrailingDelta`: Trailing deltas

**Price Restrictions (SELL side):**
- LIMIT_MAKER/TAKE_PROFIT_LIMIT price > Last Price > STOP_LOSS stopPrice
- OR TAKE_PROFIT stopPrice > Last Price > STOP_LOSS stopPrice

---

### 9. NEW ORDER LIST - OTO
**Endpoint:** `POST /api/v3/orderList/oto`

**Purpose:** One-Triggers-the-Other - working order triggers pending order

**Order Structure:**
- **Working Order:** LIMIT or LIMIT_MAKER (goes on book immediately)
- **Pending Order:** Can be STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT, MARKET, etc.
  - ⚠️ Cannot use MARKET with quoteOrderQty

**Key Behavior:**
- Pending order appears as `PENDING_NEW` status
- Only activates when working order is fully filled

---

### 10. NEW ORDER LIST - OTOCO
**Endpoint:** `POST /api/v3/orderList/otoco`

**Purpose:** One-Triggers-One-Cancels-the-Other (3 orders)

**Order Structure:**
- **Working Order:** LIMIT or LIMIT_MAKER (goes on book immediately)
- **Pending Above:** STOP_LOSS, STOP_LOSS_LIMIT, LIMIT_MAKER, TAKE_PROFIT, TAKE_PROFIT_LIMIT
- **Pending Below:** STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT
  - Forms OCO pair when activated

**Key Behavior:**
- Pending orders are OCO pair
- Only activate when working order fills
- One triggers, other cancels automatically

---

### 11. NEW ORDER LIST - OPO
**Endpoint:** `POST /api/v3/orderList/opo`

**Purpose:** One-Pending-Other - two orders placed simultaneously

**Order Structure:**
- **Working Order:** LIMIT or LIMIT_MAKER
- **Pending Order:** Any type except MARKET with quoteOrderQty

**Key Behavior:**
- Both orders go on book immediately
- No cascading trigger mechanism

---

### 12. NEW ORDER LIST - OPOCO
**Endpoint:** `POST /api/v3/orderList/opoco`

**Purpose:** One-Pending-One-Cancels-the-Other (3 orders)

**Order Structure:**
- **Working Order:** LIMIT or LIMIT_MAKER (on book immediately)
- **Pending Above:** STOP_LOSS, STOP_LOSS_LIMIT, LIMIT_MAKER, TAKE_PROFIT, TAKE_PROFIT_LIMIT
- **Pending Below:** STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT
  - Forms OCO pair

**Key Behavior:**
- Working order on book immediately
- Pending orders form OCO pair
- Cancels all others when one triggers

---

### 13. CANCEL ORDER LIST
**Endpoint:** `DELETE /api/v3/orderList`

**Purpose:** Cancel entire order list (all orders in it)

**Parameters:**
- `orderListId` or `listClientOrderId`: Identify which list to cancel

---

### 14. NEW ORDER USING SOR
**Endpoint:** `POST /api/v3/sor/order`

**Purpose:** Place order using Smart Order Routing (splits across venues)

⚠️ **Note:** Only supports LIMIT and MARKET orders (no stop loss/take profit)

---

## FUTURES TRADING ENDPOINTS

### 15. NEW ALGO ORDER (CONDITIONAL ORDERS)
**Endpoint:** `POST /fapi/v1/algoOrder` OR `/dapi/v1/algoOrder`

**Purpose:** Create conditional orders (REQUIRED for Futures STOP_LOSS, TAKE_PROFIT as of Dec 9, 2025)

**Conditional Order Types for TP/SL:**
- `STOP_MARKET` (Stop Loss Market)
- `TAKE_PROFIT_MARKET` (Take Profit Market)
- `STOP` (Traditional Stop Loss Limit)
- `TAKE_PROFIT` (Traditional Take Profit Limit)
- `TRAILING_STOP_MARKET` (Trailing Stop)

**Key Parameters:**
- `orderType`: Type of algo order
- `side`: BUY or SELL
- `symbol`: Trading pair
- `quantity`: Order size
- `triggerPrice`: Price to trigger the order
- `callbackRate`: For trailing stops (in BIPS)
- `activatePrice`: Activation price for trailing stops
- `positionSide`: LONG, SHORT (for Futures)
- `closePosition`: true/false (close position on trigger)
- `reduceOnly`: true/false

**Response Contains:**
- `algoId`: Unique algo order ID
- `algoType`: "CONDITIONAL"
- `orderType`: The type (TAKE_PROFIT, STOP_MARKET, etc.)
- `algoStatus`: NEW, TRIGGERED, CANCELED, etc.
- `triggerPrice`: The trigger price
- `actualOrderId`: Order ID if triggered (when executed)

---

### 16. QUERY CURRENT OPEN ALGO ORDERS
**Endpoint:** `GET /fapi/v1/algoOrders` OR `/dapi/v1/algoOrders`

**Purpose:** Get all active pending algo orders

**Query Parameters:**
- `symbol`: (optional) Filter by symbol
- `limit`: (optional) Number of results

**Response Contains:**
- List of all pending STOP_MARKET, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET orders
- Status: NEW (pending), TRIGGERED (activated)

---

### 17. QUERY ALL ALGO ORDERS
**Endpoint:** `GET /fapi/v1/algoOrders` with `startTime` / `endTime`

**Purpose:** Query historical algo orders (active + closed)

---

### 18. CANCEL ALGO ORDER
**Endpoint:** `DELETE /fapi/v1/algoOrder` OR `/dapi/v1/algoOrder`

**Purpose:** Cancel pending algo order

**Parameters:**
- `algoId` or `clientAlgoId`: Identify order to cancel

---

### 19. NEW ORDER (Futures)
**Endpoint:** `POST /fapi/v1/order` OR `/dapi/v1/order`

⚠️ **IMPORTANT:** As of Dec 9, 2025, this endpoint NO LONGER accepts:
- STOP_MARKET
- TAKE_PROFIT_MARKET
- STOP
- TAKE_PROFIT
- TRAILING_STOP_MARKET

Use `/fapi/v1/algoOrder` instead (Error code: -4120)

**Still Supports:**
- LIMIT
- MARKET
- LIMIT_MAKER

---

## ORDER TYPES REFERENCE

### PENDING ORDER TYPES & WHAT TRIGGERS THEM

#### SPOT TRADING

| Order Type | Trigger Name | How It Triggers | Executes As |
|---|---|---|---|
| **STOP_LOSS** | Stop Loss | Price reaches stopPrice | MARKET order |
| **STOP_LOSS_LIMIT** | Stop Loss Limit | Price reaches stopPrice | LIMIT order (requires price param) |
| **TAKE_PROFIT** | Take Profit | Price reaches stopPrice | MARKET order |
| **TAKE_PROFIT_LIMIT** | Take Profit Limit | Price reaches stopPrice | LIMIT order (requires price param) |
| **TRAILING_STOP_MARKET** | Trailing Stop Market | Price moves adversely by trailingDelta% | MARKET order |

---

#### FUTURES TRADING (Algo Orders)

| Order Type | Trigger Name | How It Triggers | Executes As |
|---|---|---|---|
| **STOP_MARKET** | Stop Loss Market | triggerPrice reached | MARKET order |
| **TAKE_PROFIT_MARKET** | Take Profit Market | triggerPrice reached | MARKET order |
| **STOP** | Stop Loss Limit | triggerPrice reached | LIMIT order |
| **TAKE_PROFIT** | Take Profit Limit | triggerPrice reached | LIMIT order |
| **TRAILING_STOP_MARKET** | Trailing Stop Market | Price moves adversely by callbackRate% | MARKET order |

---

### STOP LOSS ORDER CONFIGURATIONS

#### Spot - STOP_LOSS (Market)
```
Parameters:
- type: "STOP_LOSS"
- quantity: Amount to sell/buy
- stopPrice: Trigger price (REQUIRED)
- trailingDelta: Optional, for trailing version
```

#### Spot - STOP_LOSS_LIMIT
```
Parameters:
- type: "STOP_LOSS_LIMIT"
- quantity: Amount
- stopPrice: Trigger price
- price: Limit price to execute at
- timeInForce: GTC, FOK, IOC (REQUIRED for limit)
```

#### Futures - STOP_MARKET (Algo Order)
```
Parameters:
- orderType: "STOP_MARKET"
- triggerPrice: Trigger price
- quantity: Position size
- side: SELL (for long position) or BUY (for short)
- positionSide: LONG or SHORT
```

---

### TAKE PROFIT ORDER CONFIGURATIONS

#### Spot - TAKE_PROFIT (Market)
```
Parameters:
- type: "TAKE_PROFIT"
- quantity: Amount to sell/buy
- stopPrice: Trigger price (REQUIRED)
- trailingDelta: Optional, for trailing version
```

#### Spot - TAKE_PROFIT_LIMIT
```
Parameters:
- type: "TAKE_PROFIT_LIMIT"
- quantity: Amount
- stopPrice: Trigger price
- price: Limit price to execute at
- timeInForce: GTC, FOK, IOC (REQUIRED for limit)
```

#### Futures - TAKE_PROFIT_MARKET (Algo Order)
```
Parameters:
- orderType: "TAKE_PROFIT_MARKET"
- triggerPrice: Trigger price
- quantity: Position size
- side: SELL (for long position) or BUY (for short)
- positionSide: LONG or SHORT
```

---

### TRAILING STOP CONFIGURATIONS

#### Spot - TRAILING_STOP_MARKET
```
Parameters:
- type: "TRAILING_STOP_MARKET"
- quantity: Amount
- trailingDelta: Price change in BIPS (100 = 1%)
- stopPrice: Optional, starting stop price
```

**How it works:**
- For BUY orders: Tracks lowest price, triggers if price rises by trailingDelta%
- For SELL orders: Tracks highest price, triggers if price falls by trailingDelta%

---

#### Futures - TRAILING_STOP_MARKET (Algo Order)
```
Parameters:
- orderType: "TRAILING_STOP_MARKET"
- callbackRate: Callback rate in BIPS (same as trailingDelta)
- activatePrice: Activation price
- quantity: Position size
```

---

## KEY TERMS & DEFINITIONS

### Pending Order
An order that is placed but not yet triggered. Common statuses:
- `NEW`: Order waiting for trigger conditions
- `PENDING_NEW`: Waiting in order list to become active
- `TRIGGERED`: Conditions met, order executing

### Stop Price vs Trigger Price
- **Spot API:** Uses `stopPrice` parameter
- **Futures API (Algo Orders):** Uses `triggerPrice` parameter
- Both represent the price level that activates the order

### Order List vs Single Order
- **Single Order:** Individual trade execution
- **Order List:** Multiple linked orders:
  - **OCO:** One executes, other cancels
  - **OTO:** First executes, second activates
  - **OTOCO:** First executes, triggers OCO pair
  - **OPO:** Both on book independently
  - **OPOCO:** One on book, one-cancels-other pending

### OCO (One-Cancels-the-Other)
Two orders where execution of one automatically cancels the other. Common use case:
```
BUY 1 BTC @ 50,000    (above order)
SELL 1 BTC @ 45,000   (below order - stop loss)
```
If price goes to 50,000, upper order fills and lower cancels (profit taken).
If price goes to 45,000, lower order fills and upper cancels (loss prevented).

---

## PENDING ORDER STATUS VALUES

| Status | Meaning |
|---|---|
| `NEW` | Order placed and waiting |
| `PARTIALLY_FILLED` | Some quantity executed |
| `FILLED` | Fully executed |
| `CANCELED` | User or system canceled |
| `PENDING_CANCEL` | Cancellation in progress |
| `PENDING_NEW` | In order list, waiting to activate |
| `REJECTED` | Exchange rejected |
| `EXPIRED` | Time window passed (GTD orders) |

---

## PRACTICAL EXAMPLES

### Example 1: Simple Stop Loss on Spot
```
POST /api/v3/order

Parameters:
- symbol: "BTCUSDT"
- side: "SELL"
- type: "STOP_LOSS"
- quantity: "0.01"
- stopPrice: "45000"
- timestamp: 1712000000000

Result:
- Order placed in PENDING state
- When BTC falls to 45,000 (or below), automatically sells 0.01 BTC at market price
```

---

### Example 2: OCO with Take Profit & Stop Loss (Spot)
```
POST /api/v3/orderList/oco

Parameters:
- symbol: "ETHUSDT"
- side: "SELL"
- quantity: "1.0"
- price: "3500"              (limit price for take profit)
- stopPrice: "3000"          (stop loss trigger)
- stopLimitPrice: "2950"     (stop loss limit price)
- timestamp: 1712000000000

Result:
- If ETH rises to 3500: Limit order sells at 3500, stop order cancels
- If ETH falls to 3000: Stop order triggers, limit order cancels
```

---

### Example 3: Futures Take Profit Market Order
```
POST /fapi/v1/algoOrder

Parameters:
- symbol: "BTCUSDT"
- orderType: "TAKE_PROFIT_MARKET"
- side: "SELL"
- positionSide: "LONG"
- quantity: "0.01"
- triggerPrice: "50000"
- timestamp: 1712000000000

Result:
- Pending order waiting
- When BTC price reaches 50,000, market sell executes immediately
- Status changes from NEW to TRIGGERED
```

---

### Example 4: Trailing Stop on Futures
```
POST /fapi/v1/algoOrder

Parameters:
- symbol: "ETHUSDT"
- orderType: "TRAILING_STOP_MARKET"
- side: "SELL"
- positionSide: "LONG"
- quantity: "1.0"
- activatePrice: "3200"
- callbackRate: "500"        (5% trailing distance)
- timestamp: 1712000000000

Result:
- Once ETH hits 3200, starts tracking highest price
- If ETH falls 5% from highest seen price since activation, sells at market
```

---

## QUERY ENDPOINTS FOR PENDING ORDERS

### Spot
- `GET /api/v3/openOrders` - All open orders on symbol
- `GET /api/v3/allOrders` - All orders (open + closed)
- `GET /api/v3/order` - Query specific order status

### Futures
- `GET /fapi/v1/openOrders` - Regular open orders
- `GET /fapi/v1/algoOrders` - Algo orders (STOP_MARKET, TAKE_PROFIT_MARKET, etc.)
- `GET /fapi/v1/allOrders` - All orders

---

## COMMON ERROR CODES FOR PENDING ORDERS

| Code | Meaning | Solution |
|---|---|---|
| `-4120` | STOP_ORDER_SWITCH_ALGO (Futures) | Use `/fapi/v1/algoOrder` instead of `/fapi/v1/order` |
| `-2010` | ORDER_WOULD_IMMEDIATELY_MATCH | Adjust order price/trigger price |
| `-2011` | UNKNOWN_ORDER | Order ID or clientOrderId doesn't exist |
| `-1145` | INVALID_CANCEL_RESTRICTIONS | Invalid cancelRestrictions parameter |

---

## MIGRATION NOTE (December 2025)

**Effective Date:** December 9, 2025

For **USDT-M Futures**, Binance migrated conditional orders from traditional endpoints to **Algo Service**:

### Orders Affected:
- STOP_MARKET
- TAKE_PROFIT_MARKET
- STOP
- TAKE_PROFIT
- TRAILING_STOP_MARKET

### Action Required:
- **Old:** POST `/fapi/v1/order` with type="STOP_MARKET" ❌
- **New:** POST `/fapi/v1/algoOrder` with orderType="STOP_MARKET" ✅

---

## QUICK REFERENCE TABLE

| Action | Spot Endpoint | Futures Endpoint |
|---|---|---|
| Place stop loss order | POST /api/v3/order (type: STOP_LOSS) | POST /fapi/v1/algoOrder (orderType: STOP_MARKET) |
| Place take profit order | POST /api/v3/order (type: TAKE_PROFIT) | POST /fapi/v1/algoOrder (orderType: TAKE_PROFIT_MARKET) |
| Place OCO | POST /api/v3/orderList/oco | Not available in Futures |
| Query pending orders | GET /api/v3/openOrders | GET /fapi/v1/algoOrders |
| Cancel pending order | DELETE /api/v3/order | DELETE /fapi/v1/algoOrder |
| Trailing stop | POST /api/v3/order (type: TRAILING_STOP_MARKET) | POST /fapi/v1/algoOrder (orderType: TRAILING_STOP_MARKET) |

---

**End of Document**
