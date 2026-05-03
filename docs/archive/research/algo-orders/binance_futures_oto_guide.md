# Binance Futures API: Market Order con TakeProfit (OTO)

## Realidad Importante ⚠️

**Binance Futures API NO soporta nativa mente la creación de un OTO (One Triggers the Other) completo en una sola llamada API**, tal como lo hace la app nativa. 

Sin embargo, Binance ofrece dos soluciones principales:

---

## **Solución 1: `batchOrders` - Múltiples órdenes simultáneamente** ✅ RECOMENDADO

Este es el enfoque más cercano a lo que buscas. Permite enviar múltiples órdenes en **una sola llamada HTTP**, aunque técnicamente son órdenes separadas.

### Ventaja Clave
- Si la orden principal se cancela manualmente, deberás cancelar manualmente el TP/SL
- Si se ejecuta la orden principal, el TP permanece activo (podrías usar webhooks/listeners para cancelarlo automáticamente)

### Ejemplo de Solicitud

```bash
POST /fapi/v1/batchOrders

batchOrders=[
  {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": "0.1",
    "positionSide": "BOTH"
  },
  {
    "symbol": "BTCUSDT",
    "side": "SELL",
    "type": "TAKE_PROFIT_MARKET",
    "quantity": "0.1",
    "stopPrice": "50000",
    "positionSide": "BOTH",
    "timeInForce": "GTC",
    "workingType": "MARK_PRICE"
  }
]
```

### JavaScript (Node.js) con Binance API

```javascript
const axios = require('axios');
const crypto = require('crypto');

const apiKey = 'tu_api_key';
const apiSecret = 'tu_api_secret';
const baseUrl = 'https://fapi.binance.com';

async function createMarketOrderWithTP(symbol, quantity, takeProfitPrice) {
  const timestamp = Date.now();
  const recvWindow = 5000;

  // Crear las dos órdenes
  const batchOrders = [
    {
      symbol: symbol,
      side: 'BUY',
      type: 'MARKET',
      quantity: quantity.toString(),
      positionSide: 'BOTH'
    },
    {
      symbol: symbol,
      side: 'SELL',
      type: 'TAKE_PROFIT_MARKET',
      quantity: quantity.toString(),
      stopPrice: takeProfitPrice.toString(),
      positionSide: 'BOTH',
      timeInForce: 'GTC',
      workingType: 'MARK_PRICE', // O 'CONTRACT_PRICE'
      priceProtect: true
    }
  ];

  // Query string
  const params = new URLSearchParams({
    batchOrders: JSON.stringify(batchOrders),
    timestamp: timestamp,
    recvWindow: recvWindow
  });

  // Generar firma
  const signature = crypto
    .createHmac('sha256', apiSecret)
    .update(params.toString())
    .digest('hex');

  try {
    const response = await axios.post(
      `${baseUrl}/fapi/v1/batchOrders`,
      null,
      {
        params: {
          ...params,
          signature: signature
        },
        headers: {
          'X-MBX-APIKEY': apiKey
        }
      }
    );

    console.log('Órdenes creadas:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Uso
createMarketOrderWithTP('BTCUSDT', 0.1, 50000);
```

### Python (con python-binance)

```python
from binance.um_futures import UMFutures

client = UMFutures(key='tu_api_key', secret='tu_api_secret')

def place_market_order_with_tp(symbol, quantity, tp_price):
    """
    Coloca una orden MARKET con su correspondiente TAKE_PROFIT_MARKET
    en una sola llamada batchOrders
    """
    
    orders = [
        {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quantity": str(quantity),
            "positionSide": "BOTH"
        },
        {
            "symbol": symbol,
            "side": "SELL",
            "type": "TAKE_PROFIT_MARKET",
            "quantity": str(quantity),
            "stopPrice": str(tp_price),
            "positionSide": "BOTH",
            "timeInForce": "GTC",
            "workingType": "MARK_PRICE",
            "priceProtect": True
        }
    ]
    
    try:
        response = client.place_multiple_orders(batchOrders=orders)
        print("Órdenes colocadas exitosamente:", response)
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise

# Uso
place_market_order_with_tp('BTCUSDT', 0.1, 50000)
```

---

## **Solución 2: Órdenes Secuenciales** (Alternativa menos ideal)

Si necesitas control más fino o mejor sincronización:

```javascript
async function createMarketOrderWithTPSequential(symbol, quantity, tpPrice, slPrice = null) {
  try {
    // 1. Crear la orden MARKET
    const marketOrder = await client.futures_create_order({
      symbol: symbol,
      side: 'BUY',
      type: 'MARKET',
      quantity: quantity
    });

    console.log('Orden Market creada:', marketOrder.orderId);

    // 2. Crear orden TAKE_PROFIT_MARKET (vinculada a la posición)
    const tpOrder = await client.futures_create_order({
      symbol: symbol,
      side: 'SELL',
      type: 'TAKE_PROFIT_MARKET',
      quantity: quantity,
      stopPrice: tpPrice,
      timeInForce: 'GTC',
      workingType: 'MARK_PRICE',
      priceProtect: true,
      reduceOnly: true,
      positionSide: 'BOTH'
    });

    console.log('Orden TP creada:', tpOrder.orderId);

    // 3. (Opcional) Crear orden STOP_LOSS_MARKET
    if (slPrice) {
      const slOrder = await client.futures_create_order({
        symbol: symbol,
        side: 'SELL',
        type: 'STOP_MARKET',
        quantity: quantity,
        stopPrice: slPrice,
        timeInForce: 'GTC',
        workingType: 'MARK_PRICE',
        priceProtect: true,
        reduceOnly: true,
        positionSide: 'BOTH'
      });

      console.log('Orden SL creada:', slOrder.orderId);
      return { marketOrder, tpOrder, slOrder };
    }

    return { marketOrder, tpOrder };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

---

## Parámetros Importantes

### `type` (Tipo de Orden)
- `MARKET` - Ejecución inmediata
- `TAKE_PROFIT_MARKET` - Se ejecuta como MARKET cuando alcanza el stopPrice
- `STOP_MARKET` - Se ejecuta como MARKET cuando cae el stopPrice

### `stopPrice` (para TP/SL)
El precio en el que se dispara la orden condicional

### `workingType` 
- `MARK_PRICE` - Usa el precio de marca (más estable, recomendado)
- `CONTRACT_PRICE` - Usa el precio del último contrato (default, más volátil)

### `timeInForce`
- `GTC` - Good Till Cancel (hasta que se ejecute o cancele manualmente)
- `GTE_GTC` - Good Till Execute, Good Till Cancel (para órdenes condicionales)

### `reduceOnly`
- `true` - Solo reduce posición (seguridad extra para TP/SL)
- `false` - Puede abrir nueva posición

### `priceProtect`
- `true` - Protege contra precios extremos (recomendado)
- `false` - Sin protección

---

## Ejemplo Completo con Gestión Automática

```javascript
async function managedMarketOrderWithTP(symbol, quantity, tpPrice, slPrice) {
  try {
    // 1. Colocar todas las órdenes
    const orders = await createMarketOrderWithTP(symbol, quantity, tpPrice, slPrice);
    
    const mainOrderId = orders[0].orderId;
    const tpOrderId = orders[1].orderId;
    const slOrderId = slPrice ? orders[2].orderId : null;

    // 2. Escuchar cambios en la posición
    const positionMonitor = setInterval(async () => {
      const position = await client.get_position(symbol);

      // Si no hay posición, ambas órdenes fueron ejecutadas o canceladas
      if (position.quantity === 0) {
        console.log('Posición cerrada');
        clearInterval(positionMonitor);
        
        // Cancelar cualquier orden pendiente
        if (tpOrderId) await client.cancel_order(symbol, tpOrderId);
        if (slOrderId) await client.cancel_order(symbol, slOrderId);
      }
    }, 1000);

    return { mainOrderId, tpOrderId, slOrderId };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

---

## Limitaciones vs App Nativa

| Característica | App Nativa | API batchOrders |
|---|---|---|
| Una sola llamada | ✅ Sí | ✅ Sí (HTTP) |
| Cancelación automática TP/SL | ✅ Sí | ❌ Manual |
| Sincronización perfecta | ✅ Sí | ⚠️ Casi perfecta |
| Tipo OTO verdadero | ✅ Sí | ❌ Simulado |

---

## Recomendación Final

**Usa `batchOrders`** para colocar la orden MARKET + TAKE_PROFIT_MARKET en una sola llamada HTTP. Para mejorar la experiencia:

1. **Coloca ambas órdenes con `batchOrders`**
2. **Implementa un listener** que cancele el TP cuando la posición se cierre
3. **Usa webhooks o polling** para monitorear cambios
4. **Considera usar Algo Orders** (New Algo Order endpoint) para órdenes condicionales más avanzadas

---

## Nota Importante sobre Algo Orders

Binance recientemente migró órdenes condicionales (STOP_MARKET, TAKE_PROFIT_MARKET) a **Algo Service**. Para máxima compatibilidad, verifica si necesitas usar:

```
POST /fapi/v1/algoOrders  (en lugar de /fapi/v1/order)
```

para órdenes condicionales avanzadas.
