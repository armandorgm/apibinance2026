# REFERENCIA RÁPIDA - Obtener TP/SL Pendientes en Binance Futures

## 📌 ENDPOINT PRINCIPAL

```
GET /fapi/v1/openAlgoOrders
```

**URL Completa**:
```
https://fapi.binance.com/fapi/v1/openAlgoOrders?symbol=BTCUSDT&timestamp=1712000000000&signature=SIGNATURE
```

---

## 🚀 COMANDO MÁS RÁPIDO (con el script)

```bash
python3 get_tp_sl.py --api-key "YOUR_KEY" --api-secret "YOUR_SECRET"
```

---

## 📋 PARÁMETROS CLAVE

| Parámetro | Valor | Obligatorio | Ejemplo |
|---|---|---|---|
| `symbol` | Par trading | NO | BTCUSDT |
| `algoType` | CONDITIONAL | NO | CONDITIONAL |
| `algoId` | ID de la orden | NO | 2148627 |
| `timestamp` | Milisegundos | **SÍ** | 1712000000000 |
| `signature` | HMAC SHA256 | **SÍ** | abc123... |

---

## 📊 RESPUESTA ESPERADA

```json
[
  {
    "algoId": 2148627,
    "orderType": "TAKE_PROFIT",      // ← Tipo de orden
    "symbol": "BTCUSDT",
    "side": "SELL",
    "triggerPrice": "50000.000",      // ← Precio de activación
    "quantity": "0.01",
    "algoStatus": "NEW",              // ← Estado (NEW = pendiente)
    "createTime": 1750514941540
  }
]
```

---

## 🎯 IDENTIFIYING TP vs SL

| Campo | Valor | Significa |
|---|---|---|
| `orderType` | `TAKE_PROFIT` | 📈 Take Profit |
| `orderType` | `TAKE_PROFIT_MARKET` | 📈 Take Profit (Market) |
| `orderType` | `STOP_MARKET` | 🛑 Stop Loss (Market) |
| `orderType` | `STOP` | 🛑 Stop Loss (Limit) |
| `algoStatus` | `NEW` | ⏳ Pendiente |
| `algoStatus` | `TRIGGERED` | ✅ Ejecutado |
| `algoStatus` | `CANCELED` | ❌ Cancelado |

---

## 💻 CÓDIGO PYTHON MÍNIMO

```python
import requests
import time
import hmac
import hashlib

api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

params = {
    "symbol": "BTCUSDT",
    "timestamp": int(time.time() * 1000)
}

query_string = "&".join([f"{k}={v}" for k, v in params.items()])
signature = hmac.new(
    api_secret.encode(),
    query_string.encode(),
    hashlib.sha256
).hexdigest()

params["signature"] = signature

response = requests.get(
    "https://fapi.binance.com/fapi/v1/openAlgoOrders",
    params=params,
    headers={"X-MBX-APIKEY": api_key}
)

# Extraer solo Take Profits
tp_orders = [o for o in response.json() 
             if 'TAKE_PROFIT' in o['orderType']]

# Extraer solo Stop Loss
sl_orders = [o for o in response.json() 
             if 'STOP' in o['orderType']]

print(f"TP pendientes: {len(tp_orders)}")
print(f"SL pendientes: {len(sl_orders)}")
```

---

## 🔄 FLUJO COMPLETO

```
1. Crear orden en app nativa con TP/SL marcados
                    ↓
2. Binance crea 3 órdenes:
   - Orden principal (entrada)
   - Orden TP (condicional)
   - Orden SL (condicional)
                    ↓
3. Consultar API: GET /fapi/v1/openAlgoOrders
                    ↓
4. Filtrar por orderType:
   - TAKE_PROFIT* = Los TP
   - STOP* = Los SL
                    ↓
5. Monitorear estado:
   - NEW = Esperando
   - TRIGGERED = Ejecutado
   - CANCELED = Cancelado
```

---

## ⚡ CASOS DE USO COMUNES

### Ver todos los TP/SL
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET
```

### Ver solo TP/SL de BTCUSDT
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --symbol BTCUSDT
```

### Ver solo Take Profits
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action tp
```

### Ver solo Stop Loss
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action sl
```

### Cancelar un TP/SL (por algoId 2148627)
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --cancel 2148627
```

### Ver en formato JSON
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action json
```

---

## 🔗 OTROS ENDPOINTS ÚTILES

| Endpoint | Método | Uso |
|---|---|---|
| `/fapi/v1/openAlgoOrders` | GET | **TP/SL PENDIENTES** (ideal) |
| `/fapi/v1/algoOrders` | GET | Historial TP/SL (todos) |
| `/fapi/v1/algoOrder` | DELETE | Cancelar TP/SL |
| `/fapi/v1/algoOrdersAll` | DELETE | Cancelar todos TP/SL de un par |

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

| Error | Causa | Solución |
|---|---|---|
| `-2015 Invalid API-key` | API key incorrecta o sin permisos | Habilita "Futures" en API key |
| `-4120 Order type not supported` | Intentaste crear TP/SL en endpoint antiguo | Usa `/fapi/v1/algoOrder` |
| `Signature for this request was invalid` | Timestamp desincronizado | Sincroniza tu reloj |
| `No module named 'requests'` | Falta instalar requests | `pip install requests` |

---

## 🔐 SEGURIDAD RECOMENDADA

```bash
# Guardar API keys en variables de entorno
export BINANCE_API_KEY="tu_api_key"
export BINANCE_API_SECRET="tu_api_secret"

# Usar en Python
import os
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
```

---

## 📱 INTEGRACIÓN CON HERRAMIENTAS

### Google Sheets
```
=IMPORTDATA("https://api.tu-servidor.com/get_tp_sl?symbol=BTCUSDT")
```

### IFTTT / Automatizaciones
```bash
# Webhook que devuelve TP/SL en JSON
curl -X GET "https://tu-servidor/get_tp_sl?symbol=BTCUSDT&format=json"
```

### Discord Bot
```python
import discord
client = discord.Client()

@client.event
async def on_message(message):
    if message.content == "!tp_sl":
        tp_sl = api.get_pending_tp_sl()
        await message.channel.send(f"TP/SL pendientes: {len(tp_sl)}")
```

---

## 📚 DOCUMENTACIÓN OFICIAL

- **Current All Algo Open Orders**: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Current-All-Algo-Open-Orders
- **Binance Futures API**: https://binance-docs.github.io/apidocs/futures/en/
- **Test Binance Futures**: https://testnet.binancefuture.com/

---

## 💡 TIPS & TRICKS

### Usar jq para parsear JSON (Linux)
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action json \
  | jq '.[] | select(.orderType == "TAKE_PROFIT") | {symbol, triggerPrice}'
```

### Guardar en CSV
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action json \
  | python3 -c "import json, csv, sys; data = json.load(sys.stdin); writer = csv.DictWriter(sys.stdout, fieldnames=data[0].keys()); writer.writeheader(); writer.writerows(data)"
```

### Monitoreo en tiempo real (cada 5 segundos)
```bash
while true; do
    clear
    python3 get_tp_sl.py --api-key KEY --api-secret SECRET
    sleep 5
done
```

---

## 📞 SOPORTE

**Si tienes problemas:**
1. ✅ Verifica que tu API key tenga permisos para Futures
2. ✅ Sincroniza tu reloj (timestamp)
3. ✅ Verifica que tengas TP/SL activos (no ejecutados/cancelados)
4. ✅ Intenta en testnet primero: `--testnet`

---

**Script y documentación actualizados**: Abril 2, 2026

---

## RESUMEN DE 10 SEGUNDOS

```
1. Endpoint: GET /fapi/v1/openAlgoOrders
2. Parámetro clave: ?symbol=BTCUSDT
3. Busca: orderType = "TAKE_PROFIT" o "STOP_MARKET"
4. Estado: algoStatus = "NEW" (pendiente)
5. O usa: python3 get_tp_sl.py --api-key KEY --api-secret SECRET
```
