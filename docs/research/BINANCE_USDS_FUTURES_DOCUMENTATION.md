# Binance USDS Futures Python Connector - Complete Documentation

**Package**: `binance-sdk-derivatives-trading-usds-futures`  
**Repository**: https://github.com/binance/binance-connector-python  
**Module Path**: `clients/derivatives_trading_usds_futures`

---

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Authentication](#authentication)
4. [Market Data Endpoints](#market-data-endpoints)
5. [Account & User Data Endpoints](#account--user-data-endpoints)
6. [Trading Endpoints](#trading-endpoints)
7. [WebSocket Streams](#websocket-streams)
8. [Error Handling](#error-handling)
9. [Rate Limits](#rate-limits)
10. [API Response Metadata](#api-response-metadata)

---

## Overview

The Binance USDS Futures (USD-M Futures) Python connector is a lightweight library that provides a simple interface to interact with Binance's USDS-Margined Perpetual Futures API.

### Key Features

- **Public API Access**: Market data endpoints accessible without authentication
- **Private API Access**: Account, position, and order management with API key authentication
- **WebSocket Support**: Real-time market streams and user data streams
- **Proxy Support**: HTTP proxy configuration for both REST and WebSocket connections
- **Rate Limiting**: Built-in rate limit information in response headers
- **Error Handling**: Comprehensive error messages for both client and server errors

### Base URLs

- **Testnet**: https://testnet.binancefuture.com
- **Mainnet**: https://fapi.binance.com (or alternative URLs provided by Binance)

---

## Installation & Setup

### Installation via pip

```bash
pip install binance-sdk-derivatives-trading-usds-futures
```

### Installation via poetry

```bash
poetry add binance-sdk-derivatives-trading-usds-futures
```

### Quick Start Example

```python
from binance.um_futures import UMFutures

# Initialize client (public endpoints)
client = UMFutures()

# Test connectivity
print(client.time())

# Initialize client with API keys (private endpoints)
client = UMFutures(
    key="your_api_key",
    secret="your_api_secret",
    show_limit_usage=True
)
```

### Configuration Options

- **key**: Your Binance API key (required for private endpoints)
- **secret**: Your Binance API secret (required for private endpoints)
- **base_url**: Custom base URL (defaults to fapi.binance.com)
- **timeout**: Request timeout in seconds
- **show_limit_usage**: Display rate limit usage in response headers (default: False)
- **proxies**: Proxy configuration dictionary

---

## Authentication

### API Key Management

All private endpoints require API key authentication. The library automatically handles request signing using HMAC-SHA256.

### Request Signing

```python
# The library automatically signs requests with your secret key
# No manual signing is required

# Example private endpoint call
response = client.account()  # Signed request
```

### Parameter Naming Convention

The library follows the exact parameter naming from the official Binance API documentation. Use camelCase as shown in the API docs:

```python
# Correct - matches API documentation
response = client.query_order('BTCUSDT', orderListId=1)

# Incorrect - will not work
response = client.query_order('BTCUSDT', order_list_id=1)
```

### recvWindow Parameter

Additional parameter available for all signed endpoints:

- **recvWindow**: Optional integer (milliseconds)
  - Default: 5000 ms
  - Maximum: 60000 ms
  - Used to prevent replay attacks by specifying timestamp tolerance

```python
client.account(recvWindow=10000)
```

---

## Market Data Endpoints

### Public Market Information

These endpoints do not require authentication.

#### 1. Test Connectivity

```python
client.ping()
```

Tests connectivity to the REST API.

#### 2. Check Server Time

```python
client.time()
```

Returns current server time in milliseconds.

#### 3. Exchange Information

```python
client.exchange_info()
```

Returns current exchange trading rules, symbol information, and parameters.

**Response includes:**
- Trading pair symbols
- Filter information (price, quantity, notional)
- Rate limit definitions

#### 4. Order Book (Depth)

```python
client.depth(symbol='BTCUSDT')
client.depth(symbol='BTCUSDT', limit=100)
```

**Parameters:**
- **symbol** (required): Trading symbol (e.g., 'BTCUSDT')
- **limit** (optional): Default 500, valid limits: [5, 10, 20, 50, 100, 500, 1000]

**Returns:** Order book with bids and asks

#### 5. Recent Trades List

```python
client.trades(symbol='BTCUSDT')
client.trades(symbol='BTCUSDT', limit=500)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **limit** (optional): Default 500, maximum 1000

#### 6. Old Trades Lookup

```python
client.historical_trades(symbol='BTCUSDT', fromId=0)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **fromId** (optional): Trade ID to begin from
- **limit** (optional): Default 500, maximum 1000

#### 7. Compressed, Aggregate Trades List

```python
client.aggregate_trades(symbol='BTCUSDT')
client.aggregate_trades(symbol='BTCUSDT', startTime=1234567890, endTime=1234567999)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **fromId** (optional): ID to begin from
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds
- **limit** (optional): Default 500, maximum 1000

#### 8. Kline/Candlestick Data

```python
client.klines(symbol='BTCUSDT', interval='1h')
client.klines(symbol='BTCUSDT', interval='1h', startTime=1234567890, limit=500)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **interval** (required): Kline interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds
- **limit** (optional): Default 500, maximum 1500

**Response Format:**
```
[
  [
    1234567890,      // Open time
    "100.00",        // Open
    "110.00",        // High
    "90.00",         // Low
    "105.00",        // Close
    "1000",          // Base asset volume
    1234567945,      // Close time
    "105000",        // Quote asset volume
    100,             // Number of trades
    "500",           // Taker buy base asset volume
    "52500",         // Taker buy quote asset volume
    "0"              // Unused field
  ]
]
```

#### 9. Continuous Contract Kline Data

```python
client.continuous_klines(pair='BTCUSDT', contractType='PERPETUAL', interval='1h')
```

**Parameters:**
- **pair** (required): Trading pair (e.g., 'BTCUSDT')
- **contractType** (required): PERPETUAL, CURRENT_MONTH, NEXT_MONTH, CURRENT_QUARTER, NEXT_QUARTER
- **interval** (required): Kline interval
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds
- **limit** (optional): Default 500, maximum 1500

#### 10. Index Price Kline Data

```python
client.index_price_klines(pair='BTCUSDT', interval='1h')
```

Index price candlesticks for the underlying asset.

#### 11. Mark Price Kline Data

```python
client.mark_price_klines(symbol='BTCUSDT', interval='1h')
```

Mark price candlesticks for the perpetual contract.

#### 12. Get Funding Rate History

```python
client.funding_rate(symbol='BTCUSDT')
client.funding_rate(symbol='BTCUSDT', startTime=1234567890, limit=100)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds
- **limit** (optional): Default 100, maximum 1000

**Important Notes:**
- Funding rates are charged/paid every 8 hours at 0, 8, and 16 UTC
- Negative funding rate means shorts pay longs
- Binance does not retain any portion of the funding rate

#### 13. Get Ticker Information (24h Price Change Statistics)

```python
client.ticker(symbol='BTCUSDT')
```

24-hour rolling window price change statistics for a symbol.

#### 14. Get All Symbols Ticker Information (24h Price Change Statistics)

```python
client.ticker_all()
```

24-hour rolling window price change statistics for all symbols.

**Note:** These are NOT UTC day statistics, but a 24-hour rolling window from requestTime to 24 hours before.

#### 15. Get Symbol Ticker Information

```python
client.symbol_ticker(symbol='BTCUSDT')
```

Latest price and bid/ask information for a symbol.

#### 16. Get All Symbol Ticker Information

```python
client.symbol_ticker_all()
```

Latest price and bid/ask information for all symbols.

#### 17. Get Book Ticker

```python
client.book_ticker(symbol='BTCUSDT')
```

Best bid and best ask information for a symbol.

#### 18. Get All Book Tickers

```python
client.book_ticker_all()
```

Best bid and best ask information for all symbols.

#### 19. Get Open Interest

```python
client.open_interest(symbol='BTCUSDT')
```

Current open interest for a symbol.

#### 20. Get Open Interest Statistics

```python
client.open_interest_stat(symbol='BTCUSDT', period='5m')
```

**Parameters:**
- **symbol** (required): Trading symbol
- **period** (required): 5m, 15m, 30m, 1h, 4h, 1d
- **limit** (optional): Default 30, maximum 500
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds

#### 21. Composite Index Symbol Information

```python
client.composite_index()
client.composite_index(symbol='DEFIUSDT')
```

Composite index information for leveraged tokens.

#### 22. Get Basis

```python
client.basis(pair='BTCUSDT', contractType='PERPETUAL', period='5m')
```

Basis information between spot and futures prices.

#### 23. Get Top Trader Long/Short Ratio

```python
client.long_short_ratio(symbol='BTCUSDT', period='5m')
client.top_long_short_position_ratio(symbol='BTCUSDT', period='5m')
client.top_long_short_account_ratio(symbol='BTCUSDT', period='5m')
```

Various long/short ratio metrics for analyzing market sentiment.

#### 24. Get Global Long/Short Ratio

```python
client.global_long_short_account_ratio(period='5m')
```

Global long/short account ratio across all traders.

#### 25. Get Taker Buy/Sell Volume

```python
client.taker_long_short_ratio(symbol='BTCUSDT', period='5m')
```

Taker buy/sell volume ratio indicator.

#### 26. Get Liquidation Orders (Public)

```python
client.liquidation_orders(symbol='BTCUSDT')
client.liquidation_orders(symbol='BTCUSDT', limit=100)
```

Recent liquidation orders for a symbol (public data).

---

## Account & User Data Endpoints

These endpoints require authentication and deal with account information, positions, and user data.

### Account Information Endpoints

#### 1. Get Account Information

```python
client.account()
```

**Returns:** Comprehensive account details including:
- Balances for all assets
- Open orders and positions
- Account settings (position mode, multi-asset mode)
- Margin information

**Key Fields:**
- **totalMarginBalance**: Total margin balance (wallet + realized + unrealized PnL)
- **totalCrossWalletBalance**: Cross-portfolio wallet balance (multi-assets mode)
- **availableBalance**: Free balance for new orders
- **maxWithdrawAmount**: Maximum transferable amount
- **totalCrossUnPnl**: Unrealized PnL (multi-assets mode)

#### 2. Get Position Mode

```python
client.get_position_mode()
```

Returns user's position mode (Hedge or One-way) across all symbols.

#### 3. Change Position Mode

```python
client.change_position_mode(dualSidePosition='true')  # Enable Hedge Mode
client.change_position_mode(dualSidePosition='false')  # Enable One-way Mode
```

**Parameters:**
- **dualSidePosition** (required): 'true' for Hedge Mode, 'false' for One-way Mode

#### 4. Get Multi-Assets Mode

```python
client.get_multi_asset_mode()
```

Returns user's Multi-Assets mode status.

#### 5. Change Multi-Assets Mode

```python
client.change_multi_asset_mode(multiAssetsMargin='true')  # Enable Multi-Assets
client.change_multi_asset_mode(multiAssetsMargin='false')  # Disable Multi-Assets
```

**Parameters:**
- **multiAssetsMargin** (required): 'true' to enable, 'false' to disable

#### 6. Get Leverage Bracket

```python
client.leverage_bracket(symbol='BTCUSDT')
```

Leverage bracket information and margin requirements for a symbol.

#### 7. Get Position Information

```python
client.position_information(symbol='BTCUSDT')
client.position_information()  # Get all open positions
```

**Returns:** Current position information including:
- Entry price
- Notional value
- Mark price
- Unrealized PnL
- Leverage setting
- Liquidation price

#### 8. Get Position Risk

```python
client.position_risk(symbol='BTCUSDT')
client.position_risk()  # Get all position risks
```

Risk metrics for open positions.

#### 9. Get Account Commission Rates

```python
client.commission_rate(symbol='BTCUSDT')
```

Trading commission rates for a specific symbol.

#### 10. Get Account Income History

```python
client.income(incomeType='TRADING_FEE')
client.income(incomeType='FUNDING_FEE', symbol='BTCUSDT')
client.income(startTime=1234567890, endTime=1234567999)
```

**Parameters:**
- **incomeType** (optional): TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, COMMISSION, INSURANCE_CLEAR, REFERRAL_KICKBACK, AFFILIATE_COMMISSION, etc.
- **symbol** (optional): Trading symbol
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds
- **limit** (optional): Default 100, maximum 1000

---

### Leverage & Margin Endpoints

#### 1. Change Leverage

```python
client.change_leverage(symbol='BTCUSDT', leverage=10)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **leverage** (required): Integer from 1 to 125

**Important:** Always verify leverage settings before placing trades to avoid unintended risk.

#### 2. Change Margin Type

```python
client.change_margin_type(symbol='BTCUSDT', marginType='ISOLATED')
client.change_margin_type(symbol='BTCUSDT', marginType='CROSSED')
```

**Parameters:**
- **symbol** (required): Trading symbol
- **marginType** (required): ISOLATED or CROSSED

**Note:** Cannot change margin type if there are open positions.

#### 3. Modify Isolated Position Margin

```python
client.modify_isolated_position_margin(
    symbol='BTCUSDT',
    amount=100,
    type=1  # 1 = add, 2 = reduce
)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **amount** (required): Margin amount to add/reduce
- **type** (required): 1 (add) or 2 (reduce)
- **positionSide** (optional): BOTH, LONG, or SHORT

#### 4. Get Isolated Margin Transfer History

```python
client.isolated_margin_transfer(symbol='BTCUSDT')
client.isolated_margin_transfer(symbol='BTCUSDT', startTime=1234567890)
```

History of margin transfers for isolated positions.

#### 5. Get Notional Leverage Bracket

```python
client.notional_leverage_bracket(notionalValue=10000)
```

Maximum leverage available for a given notional value.

---

### User Trades & Orders

#### 1. Get Account Trades

```python
client.get_account_trades(symbol='BTCUSDT')
client.get_account_trades(symbol='BTCUSDT', startTime=1234567890, limit=500)
```

**Parameters:**
- **symbol** (required): Trading symbol
- **startTime** (optional): Timestamp in milliseconds
- **endTime** (optional): Timestamp in milliseconds
- **fromId** (optional): Trade ID to start from
- **limit** (optional): Default 500, maximum 1000

**Returns:** List of recent user trades for the symbol.

#### 2. Get My Trades

```python
client.get_my_trades(symbol='BTCUSDT')
client.get_my_trades(symbol='BTCUSDT', orderId=232214776)
```

All trades for a specific symbol or order.

---

## Trading Endpoints

### Order Management

#### 1. New Order

```python
# Market Order
client.new_order(
    symbol='BTCUSDT',
    side='BUY',
    type='MARKET',
    quantity=1
)

# Limit Order
client.new_order(
    symbol='BTCUSDT',
    side='BUY',
    type='LIMIT',
    timeInForce='GTC',
    quantity=1,
    price=100000
)

# Stop Market Order
client.new_order(
    symbol='BTCUSDT',
    side='SELL',
    type='STOP_MARKET',
    quantity=1,
    stopPrice=90000,
    closePosition=True
)

# Take Profit Market Order
client.new_order(
    symbol='BTCUSDT',
    side='SELL',
    type='TAKE_PROFIT_MARKET',
    quantity=1,
    stopPrice=110000
)

# Trailing Stop Order
client.new_order(
    symbol='BTCUSDT',
    side='SELL',
    type='TRAILING_STOP_MARKET',
    quantity=1,
    callbackRate=1,  # 1%
    workingType='MARK_PRICE'
)
```

**Common Parameters:**
- **symbol** (required): Trading symbol
- **side** (required): BUY or SELL
- **type** (required): LIMIT, MARKET, STOP_MARKET, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET, LIMIT_MAKER
- **quantity** (required): Order quantity
- **price** (optional): Price for LIMIT orders
- **timeInForce** (optional): GTC, IOC, FOK (for LIMIT orders)
- **newClientOrderId** (optional): Custom order ID
- **stopPrice** (optional): For STOP/TAKE_PROFIT orders
- **closePosition** (optional): Close all position (for STOP_MARKET/TAKE_PROFIT_MARKET)
- **activationPrice** (optional): Activation price for TRAILING_STOP_MARKET
- **callbackRate** (optional): Callback rate for TRAILING_STOP_MARKET (0.1 to 5%)
- **workingType** (optional): MARK_PRICE, CONTRACT_PRICE, INDEX_PRICE
- **positionSide** (optional): BOTH (One-way), LONG or SHORT (Hedge Mode)
- **reduceOnly** (optional): true or false
- **priceProtect** (optional): true or false

**Order Types:**
- **LIMIT**: Traditional limit order
- **MARKET**: Market order (execute immediately at available price)
- **STOP_MARKET**: Market order triggered at stop price
- **TAKE_PROFIT_MARKET**: Market order triggered at take profit price
- **TRAILING_STOP_MARKET**: Stop order with trailing callback rate
- **LIMIT_MAKER**: Limit order that only adds liquidity

#### 2. Test New Order

```python
client.new_order_test(
    symbol='BTCUSDT',
    side='BUY',
    type='LIMIT',
    timeInForce='GTC',
    quantity=1,
    price=100000
)
```

Validates the order parameters without actually placing the order.

#### 3. Cancel Order

```python
client.cancel_order(symbol='BTCUSDT', orderId=12345)
client.cancel_order(symbol='BTCUSDT', origClientOrderId='custom_order_id')
```

**Parameters:**
- **symbol** (required): Trading symbol
- **orderId** (optional): Order ID
- **origClientOrderId** (optional): Original client order ID

#### 4. Get Order

```python
client.get_order(symbol='BTCUSDT', orderId=12345)
client.get_order(symbol='BTCUSDT', origClientOrderId='custom_order_id')
```

Retrieve status and details of a specific order.

#### 5. Get Open Orders

```python
client.get_open_orders(symbol='BTCUSDT')
client.get_open_orders()  # Get all open orders
```

**Parameters:**
- **symbol** (optional): Filter by symbol; if omitted, returns all open orders

#### 6. Get All Orders

```python
client.get_orders(symbol='BTCUSDT')
client.get_orders(symbol='BTCUSDT', orderId=12345)
client.get_orders(symbol='BTCUSDT', startTime=1234567890)
```

All orders for a symbol (open, cancelled, filled).

#### 7. Cancel All Open Orders

```python
client.cancel_open_orders(symbol='BTCUSDT')
```

Cancels all open orders for a specific symbol.

#### 8. Cancel Multiple Orders

```python
client.cancel_orders(symbol='BTCUSDT', orderIdList=[12345, 12346])
```

Cancel multiple orders in a single request.

#### 9. Auto Cancel All Open Orders

```python
client.auto_cancel_all_open_orders(symbol='BTCUSDT', countdownTime=60000)
```

Auto-cancel open orders after countdown time (in milliseconds).

#### 10. Query Current Open Order

```python
client.query_order(symbol='BTCUSDT', orderId=12345)
```

Get details of a specific open order.

#### 11. Get Account All Orders (With Filters)

```python
client.get_all_orders(symbol='BTCUSDT', limit=100)
```

All orders with optional filtering.

---

## WebSocket Streams

The library supports WebSocket connections for real-time data streams.

### Market Data Streams

#### Agg Trade Stream

```python
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

def message_handler(_, message):
    print(message)

ws_client = UMFuturesWebsocketClient(on_message=message_handler)
ws_client.agg_trade(symbol="btcusdt")

# Unsubscribe
ws_client.unsubscribe(stream="btcusdt@aggTrade")

# Close connection
ws_client.stop()
```

**Stream Name**: `<symbol>@aggTrade`  
**Update Speed**: Real-time

#### Mark Price Stream

```python
ws_client.mark_price(symbol="btcusdt", speed=1000)  # 1000ms updates
```

**Stream Name**: `<symbol>@markPrice` or `<symbol>@markPrice@1s`  
**Update Speed**: 1000ms (default) or 100ms

#### Kline/Candlestick Streams

```python
ws_client.kline(symbol="btcusdt", interval="1h")
```

**Stream Name**: `<symbol>@kline_<interval>`  
**Update Speed**: 250ms

#### Continuous Contract Kline Stream

```python
ws_client.continuous_kline(pair="btcusdt", contractType="PERPETUAL", interval="1h")
```

**Stream Name**: `<pair>@continuousKline_<interval>`

#### Mini Ticker Stream

```python
ws_client.mini_ticker(symbol="btcusdt")
ws_client.mini_ticker_all()  # All symbols
```

**Stream Names**: `<symbol>@miniTicker` or `!miniTicker@arr`  
**Update Speed**: 1000ms

#### Ticker Stream

```python
ws_client.ticker(symbol="btcusdt")
ws_client.ticker_all()  # All symbols
```

**Stream Names**: `<symbol>@ticker` or `!ticker@arr`  
**Update Speed**: 1000ms

#### Book Ticker Streams

```python
ws_client.book_ticker(symbol="btcusdt")
ws_client.book_ticker_all()  # All symbols
```

**Stream Names**: `<symbol>@bookTicker` or `!bookTicker@arr`  
**Update Speed**: Real-time

#### Liquidation Order Stream

```python
ws_client.liquidation_order(symbol="btcusdt")
ws_client.liquidation_order_all()  # All symbols
```

**Stream Names**: `<symbol>@forceOrder` or `!forceOrder@arr`  
**Update Speed**: Real-time

#### Partial Book Depth Stream

```python
ws_client.depth(symbol="btcusdt", speed=250)  # Levels: 5, 10, 20
```

**Stream Names**: `<symbol>@depth<levels>`, `<symbol>@depth<levels>@500ms`, `<symbol>@depth<levels>@100ms`  
**Update Speed**: 250ms, 500ms, or 100ms

#### Diff. Book Depth Stream

```python
ws_client.diff_book_depth(symbol="btcusdt", speed=250)
```

**Stream Names**: `<symbol>@depth@<speed>`  
**Update Speed**: 250ms or 100ms

#### Composite Index Symbol Information Stream

```python
ws_client.composite_index(symbol="defiusdt")
```

**Stream Name**: `<symbol>@compositeIndex`

#### Top Trader Long/Short Ratio Stream

```python
ws_client.top_long_short_position_ratio(symbol="btcusdt", period="5m")
ws_client.top_long_short_account_ratio(symbol="btcusdt", period="5m")
```

**Stream Names**: Top trader position/account ratios  
**Period**: 5m, 15m, 30m, 1h, 4h, 1d

#### Global Long/Short Ratio Stream

```python
ws_client.global_long_short_account_ratio(period="5m")
```

#### Taker Buy/Sell Volume Ratio Stream

```python
ws_client.taker_long_short_ratio(symbol="btcusdt", period="5m")
```

#### Open Interest Stream

```python
ws_client.open_interest(symbol="btcusdt", period="5m")
```

#### Open Interest Statistics Stream

```python
ws_client.open_interest_stat(symbol="btcusdt", period="5m")
```

### User Data Streams

#### Subscribe to User Data Stream

```python
from binance.websocket.um_futures.websocket_client import UMFuturesUserWebsocketClient

def message_handler(_, message):
    print(message)

ws_user = UMFuturesUserWebsocketClient(on_message=message_handler)
ws_user.user_account(listen_key="your_listen_key")
```

**Events Pushed:**
- Account position update
- Account balance update
- Order execution
- Trade execution

#### Account Update

Pushed when account balance or position changes.

#### Order Trade Update

Pushed when orders are executed or filled.

#### Listen Key Management

```python
# Create listen key
listen_key = client.stream_get_listen_key()

# Keep alive
client.stream_keepalive(listenKey=listen_key)

# Close listen key
client.stream_close_listen_key(listenKey=listen_key)
```

**Default Listen Key Validity**: 60 minutes  
**Keepalive Required Every**: 30 minutes

---

## Proxy Support

Both REST and WebSocket connections support HTTP proxy configuration:

```python
# REST Client with proxy
client = UMFutures(
    proxies={'http': 'http://1.2.3.4:8080'}
)

# WebSocket Client with proxy
ws_client = UMFuturesWebsocketClient(
    on_message=message_handler,
    proxies={'http': 'http://1.2.3.4:8080'}
)

# With authentication
proxies = {'http': 'http://username:password@host:port'}
```

---

## Error Handling

### Error Types

The library returns two types of errors:

#### ClientError (4XX Status)

Client-side error (invalid parameters, missing fields, etc.)

```python
from binance.error import ClientError

try:
    client.new_order(symbol='INVALID', ...)
except ClientError as e:
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.error_code}")
    print(f"Error Message: {e.error_message}")
```

#### ServerError (5XX Status)

Server-side error (temporary service issues)

```python
from binance.error import ServerError

try:
    response = client.time()
except ServerError as e:
    print(f"Server Error: {e}")
    # Implement retry logic
```

### Logging

Enable DEBUG logging to see full request/response details:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

client = UMFutures(
    key="your_api_key",
    secret="your_api_secret"
)

# Will now log request URLs, payloads, and response text
response = client.account()
```

---

## Rate Limits

Binance implements multiple rate limiting mechanisms:

### Rate Limit Types

1. **RAW_REQUEST**: Based on total number of requests
2. **REQUEST_WEIGHT**: Based on request weight (some endpoints cost more)
3. **ORDER**: Based on number of orders placed

### Rate Limit Headers

Every response includes rate limit information:

```python
response = client.time()
# Headers include:
# X-MBX-USED-WEIGHT-1m: Current 1-minute weight usage
# X-MBX-ORDER-COUNT-1h: Current 1-hour order count
# X-MBX-ORDER-COUNT-1d: Current 1-day order count
```

### Handling Rate Limits

When rate limit (429) is exceeded:

```python
import time
from binance.error import ClientError

for attempt in range(3):
    try:
        response = client.time()
        break
    except ClientError as e:
        if e.status_code == 429:
            wait_time = int(e.headers.get('Retry-After', 60))
            time.sleep(wait_time)
        else:
            raise
```

---

## API Response Metadata

### Show Limit Usage

Enable display of rate limit usage in response:

```python
client = UMFutures(show_limit_usage=True)
response = client.time()

# Response will include metadata about rate limit usage
```

### Response Format

All successful responses return dictionaries with actual API data. Use the library's built-in features to access response metadata when `show_limit_usage=True`.

---

## Common Parameter Definitions

### Time Formats

- **Timestamps**: Milliseconds since epoch (January 1, 1970 UTC)
- **Intervals**: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

### Position Modes

- **BOTH**: One-way mode (default)
- **LONG**: Long position in hedge mode
- **SHORT**: Short position in hedge mode

### Margin Types

- **CROSSED**: Cross margin (default)
- **ISOLATED**: Isolated margin

### Order Types

- **LIMIT**: Regular limit order
- **MARKET**: Market order
- **STOP_MARKET**: Market order triggered by stop price
- **TAKE_PROFIT_MARKET**: Market order triggered by take profit price
- **TRAILING_STOP_MARKET**: Trailing stop order
- **LIMIT_MAKER**: Limit order that only adds liquidity

### Order Status

- **NEW**: Order placed but not yet filled
- **PARTIALLY_FILLED**: Part of the order has been filled
- **FILLED**: Order completely filled
- **CANCELED**: Order cancelled by user
- **REJECTED**: Order rejected by exchange
- **EXPIRED**: Order expired (FOK or IOC)

---

## Best Practices

1. **Always set leverage carefully** before placing trades
2. **Test orders** using `new_order_test()` before live trading
3. **Use proper error handling** with try-catch blocks
4. **Monitor rate limits** to avoid hitting thresholds
5. **Keep listen keys alive** every 30 minutes for user data streams
6. **Use appropriate timeouts** for WebSocket connections
7. **Implement reconnection logic** for WebSocket streams
8. **Use recvWindow parameter** to handle time synchronization issues
9. **Verify API key permissions** for the operations you plan
10. **Use ISOLATED margin** for risk management if unsure

---

## Additional Resources

- **Official API Documentation**: https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
- **GitHub Repository**: https://github.com/binance/binance-connector-python
- **PyPI Package**: https://pypi.org/project/binance-sdk-derivatives-trading-usds-futures/
- **Binance API Status**: https://status.binance.com

---

**Last Updated**: April 2026  
**API Version**: FAPI v1  
**Library**: binance-sdk-derivatives-trading-usds-futures
