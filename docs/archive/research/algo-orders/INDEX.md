# 📚 ÍNDICE DE ARCHIVOS - Obtener TP/SL de Binance Futures

Aquí tienes una guía completa sobre qué archivo consultar según tus necesidades.

---

## 🎯 ¿QUÉ ARCHIVO NECESITO?

### 1️⃣ **"Solo quiero saber rápidamente cómo hacerlo"**
📄 **Lee**: `REFERENCIA_RAPIDA.md`
- ⏱️ Tiempo: 2-3 minutos
- 📍 Contiene: Endpoint, parámetros, ejemplos rápidos
- ✨ Ideal para: Desarrolladores experimentados

---

### 2️⃣ **"Quiero usar un script Python listo para usar"**
🐍 **Usa**: `get_tp_sl.py`
- 📖 Guía: `GUIA_USO_GET_TP_SL.md`
- ⏱️ Tiempo: 5 minutos para instalar, después 1 comando
- ✨ Ideal para: Quienes prefieren no escribir código

**Comando más rápido**:
```bash
python3 get_tp_sl.py --api-key "TU_KEY" --api-secret "TU_SECRET"
```

---

### 3️⃣ **"Quiero entender en profundidad cómo funciona"**
📄 **Lee**: `obtener_tp_sl_pendientes_futuros.md`
- ⏱️ Tiempo: 15-20 minutos
- 📍 Contiene: Explicación completa, API details, troubleshooting
- ✨ Ideal para: Quienes integran en sus sistemas

---

### 4️⃣ **"Necesito lista completa de TODOS los endpoints"**
📄 **Lee**: `binance_pending_orders_api_endpoints.md`
- ⏱️ Tiempo: 30 minutos
- 📍 Contiene: Todos los endpoints de Binance para TP/SL (Spot + Futures)
- ✨ Ideal para: Quienes quieren referencia exhaustiva

---

## 📂 ESTRUCTURA DE ARCHIVOS

```
📦 Tu carpeta de Binance Futures
├── 📄 REFERENCIA_RAPIDA.md
│   └─ Resumen de 1 página, comandos rápidos
│
├── 🐍 get_tp_sl.py
│   └─ Script Python ejecutable
│
├── 📄 GUIA_USO_GET_TP_SL.md
│   └─ Cómo usar el script (instalación, ejemplos)
│
├── 📄 obtener_tp_sl_pendientes_futuros.md
│   └─ Guía técnica detallada (API, código, solución problemas)
│
├── 📄 binance_pending_orders_api_endpoints.md
│   └─ Referencia completa de todos endpoints Binance
│
└── 📄 INDEX.md (este archivo)
    └─ Qué archivo leer en cada caso
```

---

## 🚀 INICIO RÁPIDO (3 PASOS)

### Opción A: Usar el Script (RECOMENDADO)

```bash
# Paso 1: Instalar dependencias
pip install requests tabulate

# Paso 2: Ejecutar script
python3 get_tp_sl.py --api-key "TU_API_KEY" --api-secret "TU_API_SECRET"

# Paso 3: ¡Listo! Verás todos tus TP/SL pendientes
```

Consulta `GUIA_USO_GET_TP_SL.md` para más opciones.

---

### Opción B: Usar cURL directo

```bash
# Paso 1: Obtener timestamp
timestamp=$(date +%s)000

# Paso 2: Crear firma
signature=$(echo -n "symbol=BTCUSDT&timestamp=$timestamp" | \
  openssl dgst -sha256 -hmac "TU_API_SECRET" | cut -d' ' -f2)

# Paso 3: Hacer solicitud
curl -X GET "https://fapi.binance.com/fapi/v1/openAlgoOrders?symbol=BTCUSDT&timestamp=$timestamp&signature=$signature" \
  -H "X-MBX-APIKEY: TU_API_KEY"
```

---

### Opción C: Implementar en Python

Consulta `obtener_tp_sl_pendientes_futuros.md` sección "CÓDIGO COMPLETO EN PYTHON".

---

## 📋 MATRIZ DE DECISIÓN

| Necesidad | Archivo | Tiempo |
|---|---|---|
| Entiender rápido | REFERENCIA_RAPIDA.md | 3 min |
| Usar script | get_tp_sl.py + GUIA_USO | 5 min |
| Implementar en mi código | obtener_tp_sl_pendientes_futuros.md | 20 min |
| Referencia completa | binance_pending_orders_api_endpoints.md | 30 min |

---

## 🎓 LEARNING PATH (Recomendado)

Si eres **principiante**:
```
1. Lee REFERENCIA_RAPIDA.md (10 min)
   ↓
2. Usa get_tp_sl.py (5 min)
   ↓
3. Lee GUIA_USO_GET_TP_SL.md (10 min)
   ↓
4. Experimenta con diferentes comandos (10 min)
```

Si eres **desarrollador**:
```
1. Lee REFERENCIA_RAPIDA.md (3 min)
   ↓
2. Lee obtener_tp_sl_pendientes_futuros.md (15 min)
   ↓
3. Implementa en tu código (30 min)
```

Si necesitas **referencia exhaustiva**:
```
Lee binance_pending_orders_api_endpoints.md
(tiene TODO sobre Binance API)
```

---

## 📌 LO MÁS IMPORTANTE

### Endpoint Principal:
```
GET /fapi/v1/openAlgoOrders
```

### Script Más Rápido:
```bash
python3 get_tp_sl.py --api-key "KEY" --api-secret "SECRET"
```

### Para Identificar TP/SL en Respuesta:
```
orderType = "TAKE_PROFIT" o "STOP_MARKET" o "STOP"
```

---

## ✅ CHECKLIST DE CONFIGURACIÓN

Antes de usar cualquier método:

- [ ] Tengo una API Key de Binance
- [ ] Mi API Key tiene permisos para **Futures**
- [ ] Tengo mi API Secret guardado de forma segura
- [ ] Mi reloj está sincronizado (para timestamp)
- [ ] Tengo Python 3.7+ instalado (si uso script)
- [ ] Tengo `requests` instalado (`pip install requests`)

---

## 🔗 FLUJO DE INFORMACIÓN

```
┌─────────────────────────────────────────┐
│  App Nativa Binance                      │
│  (Creo orden con TP/SL marcados)         │
└────────────────┬──────────────────────────┘
                 │
                 ↓ (3 órdenes creadas)
┌─────────────────────────────────────────┐
│  Binance Servers                         │
│  - Orden Principal                       │
│  - Orden TP (CONDITIONAL)                │
│  - Orden SL (CONDITIONAL)                │
└────────────────┬──────────────────────────┘
                 │
                 ↓
         GET /fapi/v1/openAlgoOrders
                 │
        ┌────────┴────────┐
        ↓                 ↓
   Script Python    cURL/Postman
   get_tp_sl.py
        │                 │
        └────────┬────────┘
                 ↓
     JSON Response con TP/SL
```

---

## 🎁 EJEMPLOS RÁPIDOS

### Obtener TP/SL de BTCUSDT
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --symbol BTCUSDT
```

### Obtener solo Take Profits
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action tp
```

### Obtener solo Stop Loss
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action sl
```

### Ver en tabla bonita
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action list
```

### Ver en JSON (para procesar)
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action json
```

### Cancelar un TP/SL (ID: 2148627)
```bash
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --cancel 2148627
```

---

## 🆘 AYUDA

### Si tienes error "-2015: Invalid API-key"
👉 Lee: `obtener_tp_sl_pendientes_futuros.md` → Sección "PROBLEMAS COMUNES"

### Si no ves tus TP/SL
👉 Lee: `obtener_tp_sl_pendientes_futuros.md` → Sección "PROBLEMA 1"

### Si no sabes usar el script
👉 Lee: `GUIA_USO_GET_TP_SL.md` → Sección "EJEMPLOS DE USO"

### Si necesitas más opciones del script
👉 Ejecuta: `python3 get_tp_sl.py --help`

---

## 📞 REFERENCIAS OFICIALES

- **Documentación Binance**: https://developers.binance.com/docs/derivatives/
- **API Reference**: https://binance-docs.github.io/apidocs/futures/en/
- **Test Environment**: https://testnet.binancefuture.com/

---

## 🎯 RESUMEN FINAL

| Quiero | Archivo | Comando |
|---|---|---|
| Saber rápido | REFERENCIA_RAPIDA.md | `cat REFERENCIA_RAPIDA.md` |
| Usar script | get_tp_sl.py | `python3 get_tp_sl.py --help` |
| Entender bien | obtener_tp_sl_pendientes_futuros.md | Leer en editor |
| Todo sobre Binance | binance_pending_orders_api_endpoints.md | Referencia |

---

**Última actualización**: Abril 2, 2026
**Creado para**: Traders de Binance Futures
**Facilidad de uso**: ⭐⭐⭐⭐⭐

¡Ahora tienes TODO lo que necesitas para obtener tus TP/SL pendientes! 🚀
