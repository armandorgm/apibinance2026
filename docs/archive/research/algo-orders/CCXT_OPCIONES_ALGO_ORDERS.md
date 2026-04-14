# CCXT - Obtener Órdenes Condicionales (Algo Orders) en Binance Futures

**Última actualización**: Abril 2, 2026
**Compatible con**: CCXT 4.5+ | Binance Futures (USDT-M)

---

## 📊 RESUMEN EJECUTIVO

Para obtener órdenes condicionales (TP/SL) en Binance Futures con CCXT, tienes **5 opciones** ordenadas de más a menos recomendada:

| # | Opción | Recomendación | Dificultad | Ventajas |
|---|---|---|---|---|
| 1 | **API Implícita: `fapiprivate_get_openalgoorders()`** | ⭐⭐⭐⭐⭐ | Baja | Soporte nativo, simple, actualizado |
| 2 | **Método CCXT: `fetch_open_orders()` con parámetro** | ⭐⭐⭐⭐ | Baja | Unificado, compatible, standard |
| 3 | **API Implícita: `fapiprivate_get_allalgoorders()`** | ⭐⭐⭐ | Baja | Acceso a historial, flexible |
| 4 | **Solicitud Raw HTTP con `exchange.request()`** | ⭐⭐ | Media | Control total, sin abstracción |
| 5 | **WebSocket + UserData Streams** | ⭐ | Alta | Tiempo real, complejo de mantener |

---

## 1️⃣ OPCIÓN 1 (MÁS RECOMENDADA) - API Implícita `fapiprivate_get_openalgoorders()`

### ⭐⭐⭐⭐⭐ Recomendación: ALTAMENTE RECOMENDADO

**Descripción**: Usa el método implícito de CCXT para acceder directamente al endpoint `/fapi/v1/openAlgoOrders`.

### Instalación
```bash
pip install ccxt
```

### Código

```python
import ccxt

# Inicializar exchange Binance Futures
exchange = ccxt.binance({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})

# OPCIÓN 1A: Obtener SOLO órdenes pendientes (RECOMENDADO)
open_algo_orders = exchange.fapiprivate_get_openalgoorders({
    'symbol': 'BTCUSDT'  # Opcional: especificar símbolo
})

print(f"Órdenes algo abiertas: {len(open_algo_orders)}")
for order in open_algo_orders:
    print(f"  - {order['symbol']}: {order['orderType']} @ {order['triggerPrice']}")

# OPCIÓN 1B: Sin símbolo específico (obtiene TODOS)
all_open_algo = exchange.fapiprivate_get_openalgoorders()
print(f"Total órdenes pending en TODOS los pares: {len(all_open_algo)}")
```

### Respuesta Típica
```python
[
    {
        'algoId': 2148627,
        'clientAlgoId': 'MRumok0dkhrP4kCm12AHaB',
        'algoType': 'CONDITIONAL',
        'orderType': 'TAKE_PROFIT',        # TP
        'symbol': 'BTCUSDT',
        'side': 'SELL',
        'quantity': '0.01',
        'triggerPrice': '50000.000',
        'algoStatus': 'NEW',               # Pendiente
        'createTime': 1750514941540
    },
    {
        'algoId': 2148628,
        'orderType': 'STOP_MARKET',        # SL
        'symbol': 'BTCUSDT',
        'triggerPrice': '45000.000',
        'algoStatus': 'NEW'
    }
]
```

### Filtrar TP y SL
```python
# Obtener solo Take Profits
take_profits = [
    o for o in open_algo_orders 
    if 'TAKE_PROFIT' in o['orderType']
]

# Obtener solo Stop Loss
stop_losses = [
    o for o in open_algo_orders 
    if 'STOP' in o['orderType']
]

# Filtrar por estado
pending = [o for o in open_algo_orders if o['algoStatus'] == 'NEW']
executed = [o for o in open_algo_orders if o['algoStatus'] == 'TRIGGERED']
```

### ✅ Ventajas
- ✅ Método implícito de CCXT (soporte completo)
- ✅ Simple y directo
- ✅ No necesita manipulación de parámetros complicada
- ✅ Documentado en GitHub CCXT
- ✅ Peso de API bajo (1 unidad por símbolo)
- ✅ Es el **método recomendado por CCXT**

### ❌ Desventajas
- ❌ Solo obtiene órdenes pendientes (NEW status)
- ❌ No obtiene historial de órdenes ejecutadas

### Disponible Desde
CCXT 4.0+ con soporte para Binance

---

## 2️⃣ OPCIÓN 2 - Método Unificado `fetch_open_orders()` con Parámetros

### ⭐⭐⭐⭐ Recomendación: MUY RECOMENDADO

**Descripción**: Usa el método unificado de CCXT (`fetch_open_orders`) que soporta órdenes condicionales.

### Código

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': True
    }
})

# OPCIÓN 2A: Obtener órdenes abiertas (incluye TP/SL condicionales)
open_orders = exchange.fetch_open_orders('BTCUSDT')

# Filtrar SOLO órdenes condicionales
algo_orders = [
    o for o in open_orders 
    if o.get('info', {}).get('orderType') in ['TAKE_PROFIT', 'STOP_MARKET', 'STOP', 'TAKE_PROFIT_MARKET']
]

print(f"Órdenes condicionales abiertas: {len(algo_orders)}")
for order in algo_orders:
    print(f"  {order['symbol']}: {order.get('type')} - Status: {order['status']}")

# OPCIÓN 2B: Con parámetros adicionales
params = {
    'algoType': 'CONDITIONAL'  # Parámetro específico de Binance
}
conditional_orders = exchange.fetch_open_orders(
    'BTCUSDT',
    params=params
)

print(f"Encontradas {len(conditional_orders)} órdenes condicionales")
```

### Estructura de Respuesta
```python
[
    {
        'id': '2148627',                   # algoId
        'clientOrderId': 'abc123',
        'timestamp': 1750514941540,
        'datetime': '2025-12-20T10:30:00Z',
        'lastTradeTimestamp': None,
        'symbol': 'BTC/USDT',              # Con formato CCXT
        'type': 'TAKE_PROFIT',             # Tipo de orden
        'side': 'SELL',
        'price': 50000.0,                  # Trigger price
        'amount': 0.01,                    # Cantidad
        'cost': None,
        'average': None,
        'filled': 0,
        'remaining': 0.01,
        'status': 'open',                  # NEW = open
        'fee': None,
        'trades': [],
        'info': {                          # Datos crudos de Binance
            'orderType': 'TAKE_PROFIT',
            'triggerPrice': '50000.000',
            'algoStatus': 'NEW'
        }
    }
]
```

### ✅ Ventajas
- ✅ Método unificado de CCXT
- ✅ Compatible con múltiples exchanges
- ✅ Datos normalizados
- ✅ Fácil integración con código multi-exchange
- ✅ Soporte completo en documentación CCXT

### ❌ Desventajas
- ❌ Necesita filtrado manual para obtener solo condicionales
- ❌ Los datos están parcialmente normalizados (datos crudos en `info`)
- ❌ Puede ser más lento que la opción 1

### Disponible Desde
CCXT 2.0+ (soporte estable en 4.0+)

---

## 3️⃣ OPCIÓN 3 - API Implícita `fapiprivate_get_allalgoorders()`

### ⭐⭐⭐ Recomendación: RECOMENDADO (para historial)

**Descripción**: Accede a TODAS las órdenes algo (pendientes, ejecutadas, canceladas).

### Código

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'options': {'defaultType': 'future'}
})

# Obtener TODAS las órdenes algo (con filtros opcionales)
all_algo_orders = exchange.fapiprivate_get_allalgoorders({
    'symbol': 'BTCUSDT',
    'limit': 100  # Máximo 100 (default)
})

# Filtrar por estado
pending_algo = [o for o in all_algo_orders if o['algoStatus'] == 'NEW']
executed_algo = [o for o in all_algo_orders if o['algoStatus'] == 'TRIGGERED']
canceled_algo = [o for o in all_algo_orders if o['algoStatus'] == 'CANCELED']

print(f"Pendientes: {len(pending_algo)}")
print(f"Ejecutadas: {len(executed_algo)}")
print(f"Canceladas: {len(canceled_algo)}")

# Filtrar por tipo
take_profits = [o for o in all_algo_orders if 'TAKE_PROFIT' in o['orderType']]
stop_losses = [o for o in all_algo_orders if 'STOP' in o['orderType']]
trailing_stops = [o for o in all_algo_orders if 'TRAILING' in o['orderType']]

print(f"TP: {len(take_profits)}, SL: {len(stop_losses)}, TRAILING: {len(trailing_stops)}")
```

### ✅ Ventajas
- ✅ Acceso a historial completo de órdenes
- ✅ Ver órdenes ejecutadas y canceladas
- ✅ Análisis histórico de TP/SL
- ✅ Peso de API bajo

### ❌ Desventajas
- ❌ Retorna TODAS (necesita filtrado)
- ❌ Si quieres solo pendientes, mejor usar opción 1
- ❌ Puede ser más pesado si hay muchas órdenes

---

## 4️⃣ OPCIÓN 4 - HTTP Raw Request con `exchange.request()`

### ⭐⭐ Recomendación: NO RECOMENDADO (para expertos)

**Descripción**: Llamada HTTP directa al endpoint de Binance.

### Código

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'options': {'defaultType': 'future'}
})

# Opción 4A: Usando request() de CCXT
try:
    response = exchange.request(
        method='get',
        path='/fapi/v1/openAlgoOrders',
        params={'symbol': 'BTCUSDT'},
        authenticated=True  # Usa firma automáticamente
    )
    print(f"Órdenes algo abiertas: {len(response)}")
except Exception as e:
    print(f"Error: {e}")

# Opción 4B: Acceso directo via fapiPrivateGet (más bajo nivel)
open_algo = exchange.fapiPrivateGetOpenalgoorders({'symbol': 'BTCUSDT'})
print(open_algo)
```

### ✅ Ventajas
- ✅ Control total sobre la solicitud
- ✅ Sin abstracción CCXT
- ✅ Acceso directo a respuesta de Binance

### ❌ Desventajas
- ❌ Requiere manejo manual de firma
- ❌ Más error-prone
- ❌ Requiere conocimiento de API Binance
- ❌ CCXT maneja esto mejor en las opciones 1-2

---

## 5️⃣ OPCIÓN 5 - WebSocket UserData Streams

### ⭐ Recomendación: NO RECOMENDADO (para tiempo real)

**Descripción**: Escuchar cambios en órdenes en tiempo real via WebSocket.

### Código

```python
import ccxt.async_support as ccxt_async
import asyncio

async def watch_orders():
    exchange = ccxt_async.binance({
        'apiKey': 'TU_API_KEY',
        'secret': 'TU_API_SECRET',
        'options': {'defaultType': 'future'}
    })
    
    try:
        while True:
            # Escuchar actualizaciones de órdenes en tiempo real
            orders = await exchange.watch_orders('BTCUSDT')
            
            # Filtrar solo condicionales
            algo_orders = [
                o for o in orders 
                if o.get('info', {}).get('orderType') in [
                    'TAKE_PROFIT', 'STOP_MARKET', 'STOP', 'TAKE_PROFIT_MARKET'
                ]
            ]
            
            for order in algo_orders:
                if order['status'] == 'open':
                    print(f"Orden abierta: {order['symbol']} {order['type']}")
                elif order['status'] == 'closed':
                    print(f"Orden cerrada: {order['symbol']}")
    
    except Exception as e:
        print(f"Error WebSocket: {e}")
    
    finally:
        await exchange.close()

# Ejecutar
asyncio.run(watch_orders())
```

### ✅ Ventajas
- ✅ Tiempo real
- ✅ Actualizaciones instantáneas
- ✅ Eficiente en recursos

### ❌ Desventajas
- ❌ Complejidad muy alta
- ❌ Manejo de conexiones WebSocket
- ❌ Reconexión y manejo de errores
- ❌ **NO es para obtener TP/SL actuales**, solo cambios
- ❌ Para monitoring, mejor usar REST API

---

## 🎯 COMPARACIÓN RÁPIDA

| Característica | Opción 1 | Opción 2 | Opción 3 | Opción 4 | Opción 5 |
|---|---|---|---|---|---|
| **Solo pendientes** | ✅ | ⚠️ | ❌ | ✅ | ⚠️ |
| **Con historial** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Tiempo real** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Facilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Performance** | Rápido | Normal | Normal | Rápido | Excelente |
| **Documentación** | Buena | Excelente | Buena | Media | Media |

---

## 📋 TABLA DE DECISIÓN

```
¿Cuál opción usar?

┌─────────────────────────────────────────┐
│ ¿Necesitas obtener TP/SL PENDIENTES?    │
│         SÍ → OPCIÓN 1 ⭐⭐⭐⭐⭐        │
└─────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ¿Quieres         ¿Necesitas
    código           historial
    portable?        completo?
    │                │
    SÍ               SÍ
    │                │
    ↓                ↓
   OPCIÓN 2      OPCIÓN 3 ⭐⭐⭐
   ⭐⭐⭐⭐
    
¿Necesitas tiempo real? → OPCIÓN 5 (WebSocket)
¿Eres experto? → OPCIÓN 4 (Raw HTTP)
```

---

## 🚀 CÓDIGO COMPLETO - OPCIÓN 1 (RECOMENDADO)

```python
import ccxt
from datetime import datetime

class BinanceFuturesAlgoOrders:
    def __init__(self, api_key, api_secret):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
    
    def get_pending_algo_orders(self, symbol=None):
        """Obtiene órdenes algo pendientes (TP/SL)"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self.exchange.fapiprivate_get_openalgoorders(params)
    
    def get_take_profits(self, symbol=None):
        """Obtiene solo Take Profits pendientes"""
        orders = self.get_pending_algo_orders(symbol)
        return [
            o for o in orders 
            if 'TAKE_PROFIT' in o['orderType']
        ]
    
    def get_stop_losses(self, symbol=None):
        """Obtiene solo Stop Loss pendientes"""
        orders = self.get_pending_algo_orders(symbol)
        return [
            o for o in orders 
            if 'STOP' in o['orderType']
        ]
    
    def cancel_algo_order(self, algo_id):
        """Cancela una orden algo por ID"""
        return self.exchange.fapiprivate_delete_algoorder({
            'algoId': algo_id
        })
    
    def print_summary(self, symbol=None):
        """Imprime resumen de TP/SL"""
        orders = self.get_pending_algo_orders(symbol)
        
        if not orders:
            print(f"✅ No hay órdenes algo pendientes")
            return
        
        print(f"\n📊 ÓRDENES ALGO PENDIENTES - {symbol or 'TODOS'}")
        print("=" * 80)
        
        for order in orders:
            order_type = "TP" if 'TAKE_PROFIT' in order['orderType'] else "SL"
            print(f"\n{order['symbol']} - {order_type}")
            print(f"  Trigger: {order['triggerPrice']}")
            print(f"  Cantidad: {order['quantity']}")
            print(f"  Lado: {order['side']}")
            print(f"  Estado: {order['algoStatus']}")
            print(f"  ID: {order['algoId']}")

# USO
if __name__ == "__main__":
    api_key = "TU_API_KEY"
    api_secret = "TU_API_SECRET"
    
    algo = BinanceFuturesAlgoOrders(api_key, api_secret)
    
    # Ver resumen
    algo.print_summary('BTCUSDT')
    
    # Obtener TP/SL
    tp = algo.get_take_profits('BTCUSDT')
    sl = algo.get_stop_losses('BTCUSDT')
    
    print(f"\nTP pendientes: {len(tp)}")
    print(f"SL pendientes: {len(sl)}")
```

---

## ⚠️ PROBLEMAS COMUNES Y SOLUCIONES

### Error: "binance object has no attribute 'fapiprivate_get_openalgoorders'"
```
Causa: CCXT versión antigua
Solución: pip install --upgrade ccxt
```

### Error: "Order does not exist" (-2013)
```
Causa: CCXT intenta fetch_order de algo order con fetch_order regular
Solución: Usa fapiprivate_get_openalgoorders() en su lugar
```

### Error: "Not enough permissions"
```
Causa: API key sin permisos para Futures
Solución: Habilita "Futures" en https://www.binance.com/en/usercenter/settings/api-management
```

---

## 📚 DOCUMENTACIÓN OFICIAL

- **CCXT GitHub**: https://github.com/ccxt/ccxt
- **CCXT Docs**: https://docs.ccxt.com/
- **Binance API**: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Current-All-Algo-Open-Orders

---

## 🎓 RESUMEN DE 30 SEGUNDOS

```python
# La forma más recomendada:
import ccxt

exchange = ccxt.binance({
    'apiKey': 'TU_KEY',
    'secret': 'TU_SECRET',
    'options': {'defaultType': 'future'}
})

# ESTO ES TODO LO QUE NECESITAS:
algo_orders = exchange.fapiprivate_get_openalgoorders({
    'symbol': 'BTCUSDT'
})

for order in algo_orders:
    print(f"{order['symbol']}: {order['orderType']} @ {order['triggerPrice']}")
```

---

**¡Listo! Ahora sabes cómo obtener TP/SL con CCXT.** 🚀
