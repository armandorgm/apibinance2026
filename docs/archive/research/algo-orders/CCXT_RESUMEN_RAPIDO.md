# ⚡ RESUMEN RÁPIDO - CCXT para Obtener TP/SL en Binance Futures

## 🎯 LA FORMA MÁS RÁPIDA (OPCIÓN 1 - RECOMENDADA)

```python
import ccxt

# 1. Crear exchange
exchange = ccxt.binance({
    'apiKey': 'TU_API_KEY',
    'secret': 'TU_API_SECRET',
    'options': {'defaultType': 'future'}
})

# 2. Obtener órdenes algo pendientes
algo_orders = exchange.fapiprivate_get_openalgoorders({
    'symbol': 'BTCUSDT'
})

# 3. Procesar
for order in algo_orders:
    print(f"{order['symbol']}: {order['orderType']} @ {order['triggerPrice']}")
```

**¡Eso es todo!**

---

## 📊 LAS 5 OPCIONES (Ordenadas por Recomendación)

### 1️⃣ OPCIÓN 1 - `fapiprivate_get_openalgoorders()` ⭐⭐⭐⭐⭐ **MEJOR**

```python
# Solo órdenes pendientes
open_algo = exchange.fapiprivate_get_openalgoorders({'symbol': 'BTCUSDT'})

# Todos los pares
all_open = exchange.fapiprivate_get_openalgoorders()
```

**✅ Ventajas**: Simple, directo, oficial de CCXT
**❌ Desventajas**: Solo pendientes

---

### 2️⃣ OPCIÓN 2 - `fetch_open_orders()` con filtrado ⭐⭐⭐⭐

```python
# Obtener todas las órdenes abiertas
orders = exchange.fetch_open_orders('BTCUSDT')

# Filtrar solo condicionales
algo = [o for o in orders if o.get('info', {}).get('orderType') in ['TAKE_PROFIT', 'STOP_MARKET']]
```

**✅ Ventajas**: Unificado, compatible con otros exchanges
**❌ Desventajas**: Necesita filtrado manual

---

### 3️⃣ OPCIÓN 3 - `fapiprivate_get_allalgoorders()` ⭐⭐⭐

```python
# Todas las órdenes algo (pendientes + ejecutadas)
all_algo = exchange.fapiprivate_get_allalgoorders({'symbol': 'BTCUSDT'})

# Filtrar por estado
pending = [o for o in all_algo if o['algoStatus'] == 'NEW']
executed = [o for o in all_algo if o['algoStatus'] == 'TRIGGERED']
```

**✅ Ventajas**: Acceso a historial
**❌ Desventajas**: Retorna demasiados datos

---

### 4️⃣ OPCIÓN 4 - Raw HTTP `exchange.request()` ⭐⭐

```python
response = exchange.request(
    method='get',
    path='/fapi/v1/openAlgoOrders',
    params={'symbol': 'BTCUSDT'},
    authenticated=True
)
```

**✅ Ventajas**: Control total
**❌ Desventajas**: Requiere manejo manual

---

### 5️⃣ OPCIÓN 5 - WebSocket (watch_orders) ⭐

```python
# Escuchar cambios en tiempo real (async)
orders = await exchange.watch_orders('BTCUSDT')
```

**✅ Ventajas**: Tiempo real
**❌ Desventajas**: Muy complejo

---

## 🔧 CÓDIGO PRÁCTICO

### Instalar CCXT
```bash
pip install ccxt
```

### Obtener TP/SL de BTCUSDT
```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'KEY',
    'secret': 'SECRET',
    'options': {'defaultType': 'future'}
})

orders = exchange.fapiprivate_get_openalgoorders({'symbol': 'BTCUSDT'})

# Filtrar TP y SL
tp = [o for o in orders if 'TAKE_PROFIT' in o['orderType']]
sl = [o for o in orders if 'STOP' in o['orderType']]

print(f"TP: {len(tp)}, SL: {len(sl)}")
```

### Obtener Todos los TP/SL
```python
all_orders = exchange.fapiprivate_get_openalgoorders()

for order in all_orders:
    tipo = "TP" if 'TAKE_PROFIT' in order['orderType'] else "SL"
    print(f"{order['symbol']}: {tipo} @ {order['triggerPrice']}")
```

### Cancelar un TP/SL
```python
# Obtener ID de la orden
order_id = orders[0]['algoId']

# Cancelar
result = exchange.fapiprivate_delete_algoorder({'algoId': order_id})
print("Cancelado" if result else "Error")
```

---

## 📋 COMPARACIÓN DE MÉTODOS

```
┌────────────────────────────────────────────────┐
│ OPCIÓN              │ USO RECOMENDADO            │
├────────────────────────────────────────────────┤
│ fapiprivate_get_    │ Obtener TP/SL PENDIENTES  │
│ openalgoorders()    │ (MÁS COMÚN)               │
├────────────────────────────────────────────────┤
│ fetch_open_orders() │ Código portable/multi-    │
│                     │ exchange                   │
├────────────────────────────────────────────────┤
│ fapiprivate_get_    │ Ver historial completo    │
│ allalgoorders()     │ de órdenes                │
├────────────────────────────────────────────────┤
│ exchange.request()  │ Casos especiales (raros)  │
├────────────────────────────────────────────────┤
│ watch_orders()      │ Monitoring en tiempo real │
│ (WebSocket)         │ (complejo)                │
└────────────────────────────────────────────────┘
```

---

## ❌ ERRORES COMUNES

| Error | Solución |
|---|---|
| `No attribute fapiprivate_get_openalgoorders` | `pip install --upgrade ccxt` |
| `Not enough permissions` | Habilita "Futures" en API key |
| `Empty response` | No tienes TP/SL pendientes en ese pair |
| `Invalid symbol` | Usa formato: `BTCUSDT` no `BTCUSDT:USDT` |

---

## 🎯 RESUMEN DE 10 SEGUNDOS

**Para obtener TP/SL de Binance Futures con CCXT:**

```python
import ccxt
exchange = ccxt.binance({'apiKey': 'X', 'secret': 'Y', 'options': {'defaultType': 'future'}})
orders = exchange.fapiprivate_get_openalgoorders({'symbol': 'BTCUSDT'})
print(orders)  # ¡Listo!
```

**ESO ES TODO.**

---

**Más detalles**: Ver `CCXT_OPCIONES_ALGO_ORDERS.md`

