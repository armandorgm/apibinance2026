# ⚡ RESUMEN EJECUTIVO - Obtener TP/SL Pendientes de Binance Futures

## 🎯 LA RESPUESTA EN 30 SEGUNDOS

Cuando creas una orden con **TP/SL en la app nativa**, Binance crea **3 órdenes**:
1. Tu orden principal
2. Un **Take Profit** (condicional)
3. Un **Stop Loss** (condicional)

Para obtenerlas vía API:

```bash
# OPCIÓN 1: Script Python (MÁS FÁCIL)
python3 get_tp_sl.py --api-key "TU_KEY" --api-secret "TU_SECRET"
```

```bash
# OPCIÓN 2: cURL directo (MÁS RÁPIDO)
curl -X GET "https://fapi.binance.com/fapi/v1/openAlgoOrders?symbol=BTCUSDT&timestamp=1712000000000&signature=FIRMA"
```

---

## 📌 ENDPOINT

```
GET /fapi/v1/openAlgoOrders
```

| Parámetro | Valor | Obligatorio |
|---|---|---|
| `symbol` | BTCUSDT | NO (pero recomendado) |
| `timestamp` | Milisegundos | **SÍ** |
| `signature` | HMAC SHA256 | **SÍ** |

---

## 🔍 INTERPRETAR LA RESPUESTA

```json
{
  "orderType": "TAKE_PROFIT",      // 📈 Es un Take Profit
  "triggerPrice": "50000.000",     // Precio que activa la orden
  "quantity": "0.01",               // Cantidad
  "algoStatus": "NEW",              // Estado (NEW = pendiente)
  "algoId": 2148627                 // ID para cancelar
}
```

### Identificar Tipo:
- **`TAKE_PROFIT`** o **`TAKE_PROFIT_MARKET`** = Es un TP 📈
- **`STOP`** o **`STOP_MARKET`** = Es un SL 🛑
- **`algoStatus: NEW`** = Está pendiente de ejecutarse

---

## 🚀 OPCIÓN 1: USAR SCRIPT (RECOMENDADO)

### Instalación (1 minuto)
```bash
pip install requests tabulate
```

### Uso
```bash
# Ver todos los TP/SL
python3 get_tp_sl.py --api-key KEY --api-secret SECRET

# Ver solo de BTCUSDT
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --symbol BTCUSDT

# Ver solo Take Profits
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action tp

# Ver solo Stop Loss
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action sl

# Cancelar un TP/SL (algoId: 2148627)
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --cancel 2148627
```

---

## 💻 OPCIÓN 2: CÓDIGO PYTHON MÍNIMO (3 minutos)

```python
import requests, time, hmac, hashlib

api_key = "TU_API_KEY"
api_secret = "TU_API_SECRET"

params = {
    "symbol": "BTCUSDT",
    "timestamp": int(time.time() * 1000)
}

query = "&".join([f"{k}={v}" for k, v in params.items()])
sig = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
params["signature"] = sig

resp = requests.get(
    "https://fapi.binance.com/fapi/v1/openAlgoOrders",
    params=params,
    headers={"X-MBX-APIKEY": api_key}
)

# Filtrar TP y SL
tp = [o for o in resp.json() if 'TAKE_PROFIT' in o['orderType']]
sl = [o for o in resp.json() if 'STOP' in o['orderType']]

print(f"TP pendientes: {len(tp)}")
print(f"SL pendientes: {len(sl)}")
```

---

## ☑️ REQUISITOS PREVIOS

- ✅ API Key de Binance
- ✅ API Secret de Binance
- ✅ Permisos de **Futures** habilitados en la API key
- ✅ Python 3.7+ (si usas script)
- ✅ Reloj del sistema sincronizado

---

## ❌ ERRORES TÍPICOS Y SOLUCIONES

| Error | Solución |
|---|---|
| `-2015: Invalid API-key` | Habilita "Futures" en tu API key en Binance |
| `-4120: Order not supported` | No intentes crear TP/SL con `/fapi/v1/order`, usa `/fapi/v1/algoOrder` |
| `Signature invalid` | Sincroniza tu reloj del sistema |
| `No module named requests` | Ejecuta: `pip install requests` |

---

## 📂 ARCHIVOS QUE TIENES

| Archivo | Usa cuando... |
|---|---|
| **REFERENCIA_RAPIDA.md** | Necesitas recordar comandos/parámetros |
| **get_tp_sl.py** | Quieres ejecutar directamente (script Python) |
| **GUIA_USO_GET_TP_SL.md** | Necesitas guía de cómo usar el script |
| **obtener_tp_sl_pendientes_futuros.md** | Necesitas entender en profundidad |
| **binance_pending_orders_api_endpoints.md** | Necesitas referencia COMPLETA de todos endpoints |
| **INDEX.md** | No sabes qué archivo leer |

---

## 🔑 CONCEPTOS CLAVE

### ¿Qué es un Algo Order?
Son órdenes condicionales que se activan cuando se cumple una condición (precio de trigger alcanzado).

### Tipos de TP/SL:
- **TAKE_PROFIT_MARKET**: Se ejecuta a precio MERCADO cuando se alcanza el trigger
- **STOP_MARKET**: Stop Loss que se ejecuta a precio MERCADO
- **TAKE_PROFIT** (LIMIT): Se ejecuta a precio LÍMITE
- **STOP** (LIMIT): Stop Loss que se ejecuta a precio LÍMITE

### Estados:
- **NEW**: Orden pendiente, esperando ser activada
- **TRIGGERED**: Fue activada y ejecutada
- **CANCELED**: Fue cancelada

---

## 💡 CASO DE USO PRÁCTICO

```
Escenario:
- Compré 0.01 BTC en BTCUSDT en la app
- Marqué TP en 50,000 y SL en 45,000
- Quiero verificar que están activos

Solución:
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --symbol BTCUSDT

Resultado esperado:
- 1 orden con orderType: TAKE_PROFIT, triggerPrice: 50000
- 1 orden con orderType: STOP_MARKET, triggerPrice: 45000
- Ambas con algoStatus: NEW
```

---

## 🎯 PRÓXIMOS PASOS

### 1. Configurar API Key (5 min)
→ Ve a https://www.binance.com/en/usercenter/settings/api-management
→ Habilita permisos para "Futures"

### 2. Obtener TP/SL (1 min)
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET
```

### 3. Automatizar (10 min)
→ Lee GUIA_USO_GET_TP_SL.md sección "CASOS DE USO PRÁCTICOS"

---

## 📊 MATRIZ RÁPIDA

```
┌─────────────────────────────────────────────────────┐
│ ¿QUÉ NECESITO?                                       │
├─────────────────────────────────────────────────────┤
│ 📈 TP pendientes      → orderType = "TAKE_PROFIT*"   │
│ 🛑 SL pendientes      → orderType = "STOP*"          │
│ ⏳ Pendientes         → algoStatus = "NEW"           │
│ ✅ Ejecutados        → algoStatus = "TRIGGERED"      │
│ ❌ Cancelados        → algoStatus = "CANCELED"       │
└─────────────────────────────────────────────────────┘
```

---

## 🔗 REFERENCIAS

- Documentación oficial: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Current-All-Algo-Open-Orders
- Binance Testnet: https://testnet.binancefuture.com/

---

## ⭐ QUICK START (COPY-PASTE)

```bash
# 1. Instalar
pip install requests tabulate

# 2. Ejecutar
python3 get_tp_sl.py --api-key "tu_api_key_aqui" --api-secret "tu_api_secret_aqui"

# 3. Ver resultado
# [Tabla con todos tus TP/SL pendientes]
```

---

**¡Listo! Ahora sabes cómo obtener tus TP/SL pendientes de Binance Futures.** 🚀

Para más detalles, consulta los otros archivos (INDEX.md te ayuda a elegir).
