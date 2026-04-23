# Obtener Take Profit y Stop Loss Pendientes en Binance Futures

## RESUMEN EJECUTIVO

Cuando creas una orden en la **app nativa de Binance Futures** con las opciones **TP (Take Profit)** y **SL (Stop Loss)** marcadas, la app crea **automáticamente 3 órdenes vinculadas**:

1. **Orden Principal**: Tu orden de entrada (MARKET o LIMIT)
2. **Orden de Take Profit**: Se activa cuando el precio alcanza el nivel TP
3. **Orden de Stop Loss**: Se activa cuando el precio alcanza el nivel SL

Estas órdenes TP/SL se crean como **Algo Orders** (órdenes condicionales), y para obtenerlas vía API necesitas usar el endpoint específico para Algo Orders.

---

## ENDPOINT PARA OBTENER TP/SL PENDIENTES

### 1. **ENDPOINT PRINCIPAL (RECOMENDADO)**

```
GET /fapi/v1/openAlgoOrders
```

**Descripción**: Obtiene todas las órdenes algorítmicas (condicionales) abiertas y pendientes de ejecución.

**URL Completa**: 
```
https://fapi.binance.com/fapi/v1/openAlgoOrders
```

---

## PARÁMETROS DE LA SOLICITUD

### Parámetros Disponibles:

| Parámetro | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `symbol` | STRING | NO | Símbolo del par (ej: BTCUSDT). Si no se envía, devuelve todas |
| `algoType` | STRING | NO | Tipo de algo order: "CONDITIONAL" (para TP/SL) |
| `algoId` | LONG | NO | ID específico de una orden algo si la conoces |
| `recvWindow` | LONG | NO | Ventana de tiempo de recepción (max 60000ms) |
| `timestamp` | LONG | **SÍ** | Timestamp actual en milisegundos |
| `signature` | STRING | **SÍ** | Firma HMAC SHA256 (requerida para autenticación) |

### Peso de Solicitud:
- **1 unidad**: Si especificas un `symbol`
- **40 unidades**: Si no especificas `symbol` (cuidado: afecta rate limits)

---

## EJEMPLOS DE USO

### Ejemplo 1: Obtener TP/SL de un Par Específico

```bash
curl -X GET "https://fapi.binance.com/fapi/v1/openAlgoOrders?symbol=BTCUSDT&timestamp=1712000000000&signature=YOUR_SIGNATURE" \
  -H "X-MBX-APIKEY: YOUR_API_KEY"
```

**Python:**
```python
import requests
import time
import hmac
import hashlib

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"
base_url = "https://fapi.binance.com"

def get_signature(query_string):
    return hmac.new(
        api_secret.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()

params = {
    "symbol": "BTCUSDT",
    "timestamp": int(time.time() * 1000)
}

query_string = "&".join([f"{k}={v}" for k, v in params.items()])
signature = get_signature(query_string)

params["signature"] = signature

headers = {
    "X-MBX-APIKEY": api_key
}

response = requests.get(
    f"{base_url}/fapi/v1/openAlgoOrders",
    params=params,
    headers=headers
)

print(response.json())
```

---

### Ejemplo 2: Obtener Todos los TP/SL Pendientes (Todos los Pares)

```bash
curl -X GET "https://fapi.binance.com/fapi/v1/openAlgoOrders?timestamp=1712000000000&signature=YOUR_SIGNATURE" \
  -H "X-MBX-APIKEY: YOUR_API_KEY"
```

⚠️ **ADVERTENCIA**: Sin el parámetro `symbol`, consume **40 unidades de peso** en lugar de 1. Úsalo con cuidado si tienes rate limits limitados.

---

### Ejemplo 3: Obtener Solo por Tipo (Condicionales)

```bash
curl -X GET "https://fapi.binance.com/fapi/v1/openAlgoOrders?symbol=BTCUSDT&algoType=CONDITIONAL&timestamp=1712000000000&signature=YOUR_SIGNATURE" \
  -H "X-MBX-APIKEY: YOUR_API_KEY"
```

---

## RESPUESTA DEL ENDPOINT

### Estructura de Respuesta:

```json
[
  {
    "algoId": 2148627,
    "clientAlgoId": "MRumok0dkhrP4kCm12AHaB",
    "algoType": "CONDITIONAL",
    "orderType": "TAKE_PROFIT",
    "symbol": "BNBUSDT",
    "side": "SELL",
    "positionSide": "BOTH",
    "timeInForce": "GTC",
    "quantity": "0.01",
    "algoStatus": "NEW",
    "actualOrderId": "",
    "actualPrice": "0.00000",
    "triggerPrice": "750.000",
    "price": "750.000",
    "icebergQuantity": null,
    "tpTriggerPrice": "0.000",
    "tpPrice": "0.000",
    "slTriggerPrice": "0.000",
    "slPrice": "0.000",
    "tpOrderType": "",
    "selfTradePreventionMode": "EXPIRE_MAKER",
    "workingType": "CONTRACT_PRICE",
    "priceMatch": "NONE",
    "closePosition": false,
    "priceProtect": false,
    "reduceOnly": false,
    "createTime": 1750514941540,
    "updateTime": 1750514941540,
    "triggerTime": 0,
    "goodTillDate": 0
  }
]
```

---

## EXPLICACIÓN DE CAMPOS IMPORTANTES

### Para Identificar TP/SL:

| Campo | Valor | Significado |
|---|---|---|
| `orderType` | `TAKE_PROFIT` | Es una orden de Take Profit |
| `orderType` | `TAKE_PROFIT_MARKET` | Es una orden de Take Profit (ejecución a MARKET) |
| `orderType` | `STOP_MARKET` | Es una orden de Stop Loss (ejecución a MARKET) |
| `orderType` | `STOP` | Es una orden de Stop Loss (ejecución a LIMIT) |
| `algoStatus` | `NEW` | Orden pendiente, esperando ser activada |
| `algoStatus` | `TRIGGERED` | La orden fue activada y se ejecutó |
| `algoStatus` | `CANCELED` | La orden fue cancelada |

### Campos Clave:

```
triggerPrice    → Precio que activa la orden (TP/SL)
price          → Precio límite (si aplica)
quantity       → Cantidad a ejecutar
side           → SELL (para posición LONG) o BUY (para posición SHORT)
positionSide   → LONG, SHORT, o BOTH (en modo one-way)
createTime     → Cuándo se creó la orden
algoId         → ID único de la orden algo
actualOrderId  → ID de la orden real (si ya se ejecutó)
```

---

## CASOS DE USO PRÁCTICOS

### Caso 1: Verificar si Tienes TP/SL Activos en BTC

**Situación**: Compraste 0.01 BTC en la app nativa con TP en 55,000 y SL en 45,000. Quieres verificar que están activos.

**Solicitud**:
```bash
GET /fapi/v1/openAlgoOrders?symbol=BTCUSDT
```

**Respuesta Esperada**: Array con 2 órdenes:
1. Una con `orderType: "TAKE_PROFIT"`, `triggerPrice: "55000"`
2. Una con `orderType: "STOP_MARKET"` (o `STOP`), `triggerPrice: "45000"`

---

### Caso 2: Obtener Todos los TP/SL Pendientes

**Situación**: Tienes posiciones abiertas en múltiples pares (BTC, ETH, SOL) y quieres saber todos tus TP/SL.

**Solicitud**:
```bash
GET /fapi/v1/openAlgoOrders
```

**Respuesta Esperada**: Array con TODOS los TP/SL de todos tus pares.

---

### Caso 3: Filtrar Solo los TP y SL de una Posición

**Situación**: Tienes TP y SL en ETHUSDT y necesitas obtener el `algoId` de cada uno para modificarlos o cancelarlos.

**Solicitud 1 - Obtener el TP**:
```bash
GET /fapi/v1/openAlgoOrders?symbol=ETHUSDT&orderType=TAKE_PROFIT
```

**Solicitud 2 - Obtener el SL**:
```bash
GET /fapi/v1/openAlgoOrders?symbol=ETHUSDT&orderType=STOP_MARKET
```

---

## FILTRAR RESULTADOS (POST-PROCESAMIENTO)

### En Python - Obtener Solo TP o SL:

```python
response = requests.get(
    f"{base_url}/fapi/v1/openAlgoOrders",
    params={"symbol": "BTCUSDT", "timestamp": timestamp, "signature": signature},
    headers={"X-MBX-APIKEY": api_key}
)

orders = response.json()

# Filtrar solo Take Profits
take_profits = [o for o in orders if o['orderType'] in ['TAKE_PROFIT', 'TAKE_PROFIT_MARKET']]

# Filtrar solo Stop Loss
stop_losses = [o for o in orders if o['orderType'] in ['STOP_MARKET', 'STOP']]

# Filtrar solo órdenes activas (no ejecutadas ni canceladas)
active_orders = [o for o in orders if o['algoStatus'] == 'NEW']
```

---

## ACCIONES QUE PUEDES HACER CON TP/SL

Una vez obtengas los TP/SL, puedes:

### 1. **Modificar el Trigger Price (Precio de Activación)**

```
PUT /fapi/v1/algoOrder
```

Parámetros:
- `algoId`: ID de la orden algo
- `triggerPrice`: Nuevo precio de activación

---

### 2. **Cancelar un TP o SL**

```
DELETE /fapi/v1/algoOrder
```

Parámetros:
- `algoId`: ID de la orden algo a cancelar

---

### 3. **Cancelar Todos los TP/SL de un Símbolo**

```
DELETE /fapi/v1/algoOrdersAll
```

Parámetros:
- `symbol`: Símbolo del par

---

## COMPARACIÓN DE ENDPOINTS

| Endpoint | Uso | Respuesta | Peso |
|---|---|---|---|
| **GET /fapi/v1/openAlgoOrders** | Obtener TP/SL PENDIENTES | Array de órdenes activas | 1-40 |
| GET /fapi/v1/algoOrders | Obtener historial TP/SL | Todas (activas + cerradas) | 20 |
| GET /fapi/v1/algoOrder | Obtener UN TP/SL específico | Detalles de una orden | 1 |

### Recomendación:
- **Para verificar TP/SL activos**: Usa `GET /fapi/v1/openAlgoOrders`
- **Para historial completo**: Usa `GET /fapi/v1/algoOrders`

---

## PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: No Veo Mis TP/SL

**Posibles Causas**:
1. Los TP/SL ya se ejecutaron (`algoStatus` = `TRIGGERED`)
2. Fueron cancelados (`algoStatus` = `CANCELED`)
3. La firma (signature) es incorrecta
4. El timestamp está desincronizado

**Solución**:
```python
# Verificar el timestamp actual vs Binance
server_time = requests.get("https://fapi.binance.com/fapi/v1/time").json()['serverTime']
client_time = int(time.time() * 1000)
print(f"Diferencia: {client_time - server_time}ms")
# Debe ser < 5000ms
```

---

### Problema 2: Error -2015 "Invalid API-key"

**Causa**: API key no tiene permisos para Futures Trading

**Solución**:
1. Ve a https://www.binance.com/en/usercenter/settings/api-management
2. Habilita "Futures" en los permisos de tu API key
3. Guarda y espera a que se actualice (puede tomar 1-2 minutos)

---

### Problema 3: Error -4120 "Order type not supported"

**Causa**: Intentaste crear TP/SL usando el endpoint antiguo

**Solución**: Usa `POST /fapi/v1/algoOrder` para crear nuevas órdenes TP/SL, no `POST /fapi/v1/order`

---

## CÓDIGO COMPLETO EN PYTHON

```python
import requests
import time
import hmac
import hashlib
import json

class BinanceFuturesAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://fapi.binance.com"
    
    def _get_signature(self, query_string):
        return hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def get_pending_tp_sl(self, symbol=None):
        """
        Obtiene todos los TP/SL pendientes
        
        Args:
            symbol: (str) Símbolo opcional (ej: BTCUSDT)
            Si no se especifica, obtiene de TODOS los pares
        
        Returns:
            list: Array de órdenes algo pendientes
        """
        params = {
            "timestamp": int(time.time() * 1000)
        }
        
        if symbol:
            params["symbol"] = symbol
        
        # Crear query string y firmar
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self._get_signature(query_string)
        
        params["signature"] = signature
        
        headers = {
            "X-MBX-APIKEY": self.api_key
        }
        
        response = requests.get(
            f"{self.base_url}/fapi/v1/openAlgoOrders",
            params=params,
            headers=headers
        )
        
        return response.json()
    
    def get_take_profits(self, symbol=None):
        """Obtiene solo los Take Profits pendientes"""
        all_orders = self.get_pending_tp_sl(symbol)
        return [o for o in all_orders 
                if o['orderType'] in ['TAKE_PROFIT', 'TAKE_PROFIT_MARKET']]
    
    def get_stop_losses(self, symbol=None):
        """Obtiene solo los Stop Loss pendientes"""
        all_orders = self.get_pending_tp_sl(symbol)
        return [o for o in all_orders 
                if o['orderType'] in ['STOP_MARKET', 'STOP']]
    
    def print_tp_sl_summary(self, symbol=None):
        """Imprime un resumen de TP/SL pendientes"""
        orders = self.get_pending_tp_sl(symbol)
        
        if not orders:
            print("No hay TP/SL pendientes")
            return
        
        print(f"\n{'='*80}")
        print(f"RESUMEN DE TP/SL PENDIENTES - {symbol or 'TODOS LOS PARES'}")
        print(f"{'='*80}\n")
        
        for order in orders:
            order_type = "TAKE PROFIT" if 'TAKE_PROFIT' in order['orderType'] else "STOP LOSS"
            print(f"Símbolo: {order['symbol']}")
            print(f"Tipo: {order_type}")
            print(f"Lado: {order['side']} | Cantidad: {order['quantity']}")
            print(f"Precio de Trigger: {order['triggerPrice']}")
            print(f"Precio Límite: {order['price']}")
            print(f"Estado: {order['algoStatus']}")
            print(f"Algo ID: {order['algoId']}")
            print(f"Creado: {order['createTime']}")
            print("-" * 80 + "\n")

# USO:
if __name__ == "__main__":
    api_key = "tu_api_key"
    api_secret = "tu_api_secret"
    
    api = BinanceFuturesAPI(api_key, api_secret)
    
    # Obtener TP/SL de BTCUSDT
    btc_orders = api.get_pending_tp_sl("BTCUSDT")
    print("TP/SL de BTCUSDT:", json.dumps(btc_orders, indent=2))
    
    # Obtener solo Take Profits de ETHUSDT
    eth_tp = api.get_take_profits("ETHUSDT")
    print("\nTake Profits de ETHUSDT:", json.dumps(eth_tp, indent=2))
    
    # Obtener solo Stop Loss de SOLUSDT
    sol_sl = api.get_stop_losses("SOLUSDT")
    print("\nStop Loss de SOLUSDT:", json.dumps(sol_sl, indent=2))
    
    # Resumen visual
    api.print_tp_sl_summary("BTCUSDT")
```

---

## DOCUMENTACIÓN OFICIAL

- **Current All Algo Open Orders**: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Current-All-Algo-Open-Orders
- **Query All Algo Orders**: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Query-All-Algo-Orders
- **New Algo Order**: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/New-Algo-Order

---

## RESUMEN RÁPIDO

**Endpoint**: `GET /fapi/v1/openAlgoOrders`

**Para obtener TP/SL de BTCUSDT**:
```
GET /fapi/v1/openAlgoOrders?symbol=BTCUSDT&timestamp=XXX&signature=XXX
```

**Para obtener TODOS los TP/SL**:
```
GET /fapi/v1/openAlgoOrders?timestamp=XXX&signature=XXX
```

**Diferencia con otros endpoints**:
- `openAlgoOrders` = TP/SL PENDIENTES (activos)
- `algoOrders` = HISTORIAL COMPLETO (todos + cerrados)

---

**Última actualización**: Abril 2, 2026
