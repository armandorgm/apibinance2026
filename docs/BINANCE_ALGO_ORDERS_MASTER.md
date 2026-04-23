# 🎯 Guía Maestra: Binance Algo-Orders (Strict CCXT)

Esta es la **Única Fuente de la Verdad** para la gestión de órdenes condicionales (Stop Loss, Take Profit, Trailing Stop) en Binance Futures utilizando únicamente la librería **CCXT**.

---

## 🚀 Método Recomendado (Binance Algo Service)

Desde Diciembre 2025, Binance migró todas las órdenes condicionales al **Algo Service**. Para consultarlas mediante CCXT (v4.5+), se debe utilizar el método específico del endpoint de derivados.

### Obtener Órdenes Abiertas (Pending)
```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'options': {'defaultType': 'future'}
})

# Obtiene todas las órdenes condicionales (TP/SL) pendientes
# Endpoint: GET /fapi/v1/algo/openOrders
algo_orders = exchange.fapiprivate_get_openalgoorders({
    'symbol': '1000PEPEUSDC' # Opcional
})

for order in algo_orders:
    print(f"ID: {order['algoId']} | Tipo: {order['orderType']} | Trigger: {order['triggerPrice']}")
```

---

## 📊 Referencia de Tipos de Orden

| `orderType` | Descripción | Estado Común (`algoStatus`) |
|-------------|-------------|----------------------------|
| `TAKE_PROFIT_MARKET` | TP a precio de mercado | `NEW` (Pendiente) |
| `STOP_MARKET` | SL a precio de mercado | `NEW` (Pendiente) |
| `TRAILING_STOP_MARKET` | Stop dinámico | `NEW` (Pendiente) |

---

## 🛠️ Solución de Problemas (Troubleshooting)

### 1. ¿Por qué no aparecen en `fetch_open_orders`?
En versiones antiguas de CCXT o si no se pasan parámetros específicos, `fetch_open_orders` solo consulta el endpoint `/fapi/v1/openOrders` (órdenes estándar), omitiendo el **Algo Service**. **Usa siempre `fapiprivate_get_openalgoorders()` para TP/SL.**

### 2. Error: `no attribute 'fapiprivate_get_openalgoorders'`
**Causa**: Versión de CCXT < 4.5.
**Solución**: `pip install --upgrade ccxt`.

### 3. Factor de Cantidad (1000PEPE, etc.)
Binance reporta `quantity` en unidades base. En el caso de `1000PEPE`, esto suele significar que `1.0` en la API equivale a `1000` tokens.
- **Factor 1 (API)**: `quantity: "1354.0"`
- **Factor 1000 (UI)**: `1,354,000` PEPE.
*Nota: Siempre validar contra el `market['contractSize']` de CCXT.*

---

## 🛑 Reglas de la Casa
1. **CCXT Únicamente**: Prohibido el uso de `requests` o llamadas directas a la API de Binance.
2. **Símbolos Estándar**: Usar siempre el formato CCXT (`BTC/USDC:USDC`) para normalizar antes de la llamada, pero pasar el ID de Binance (`BTCUSDC`) en los parámetros del método implícito si es necesario.

---
*Documento consolidado el 13 de Abril, 2026. Eliminados 12 archivos redundantes.*
