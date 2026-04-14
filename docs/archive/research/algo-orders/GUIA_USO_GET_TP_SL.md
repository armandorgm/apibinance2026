# Guía de Uso - Script get_tp_sl.py

## INSTALACIÓN

### 1. Descargar el script
```bash
wget https://tu-servidor/get_tp_sl.py
# o cópialo manualmente
```

### 2. Instalar dependencias
```bash
pip install requests tabulate
```

Si no quieres usar tabulate (sin tabla bonita):
```bash
pip install requests
# Y luego usa el flag --no-table al ejecutar
```

---

## CONFIGURACIÓN DE API KEY

### Paso 1: Crear una API Key en Binance
1. Dirígete a: https://www.binance.com/en/usercenter/settings/api-management
2. Click en "Create API"
3. Asigna un nombre (ej: "TP-SL-Monitor")
4. **MUY IMPORTANTE**: Habilita los permisos para:
   - ✅ Futures (USDT-M Futures)
   - ✅ Enable Reading (lectura de órdenes)
5. Guarda tu **API Key** y **Secret Key**

### Paso 2: Configurar en tu máquina
```bash
# Opción 1: Variables de entorno (MÁS SEGURO)
export BINANCE_API_KEY="tu_api_key_aqui"
export BINANCE_API_SECRET="tu_api_secret_aqui"

# Opción 2: Crear archivo .env (para desarrollo)
echo "BINANCE_API_KEY=tu_api_key_aqui" > .env
echo "BINANCE_API_SECRET=tu_api_secret_aqui" >> .env
```

---

## EJEMPLOS DE USO

### 1. Ver RESUMEN de todos los TP/SL (RECOMENDADO)
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret"
```

**Resultado esperado**:
```
================================================================================
RESUMEN DE TP/SL PENDIENTES - TODOS LOS PARES
================================================================================

📊 BTCUSDT
----
  🎯 TAKE PROFITS (1)
    • Trigger: 50000.00 | Cantidad: 0.01 | Lado: SELL | Estado: NEW | ID: 2148627
  🛑 STOP LOSS (1)
    • Trigger: 45000.00 | Cantidad: 0.01 | Lado: SELL | Estado: NEW | ID: 2148628

📊 ETHUSDT
----
  🎯 TAKE PROFITS (1)
    • Trigger: 3500.00 | Cantidad: 1.0 | Lado: SELL | Estado: NEW | ID: 2148629
  🛑 STOP LOSS (1)
    • Trigger: 3000.00 | Cantidad: 1.0 | Lado: SELL | Estado: NEW | ID: 2148630
```

---

### 2. Ver solo TP/SL de UN par específico
```bash
# Ver todos los TP/SL de BTCUSDT
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --symbol BTCUSDT
```

---

### 3. Ver solo TAKE PROFITS
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action tp
```

---

### 4. Ver solo STOP LOSS
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action sl
```

---

### 5. Ver en TABLA bonita
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action list
```

**Resultado**:
```
+─────────────+─────+─────+──────────+───────────────+─────────+─────────+─────────+─────────────────────────┐
│ Símbolo     │ Tipo│ Lado│ Cantidad │ Trigger Price │ Precio  │ Estado  │ Algo ID │ Creado                  │
├─────────────┼─────┼─────┼──────────┼───────────────┼─────────┼─────────┼─────────┼─────────────────────────┤
│ BTCUSDT     │ TP  │ SELL│    0.01  │ 50000.000     │ 50000.0 │ NEW     │ 2148627 │ 2026-04-02 10:30:15     │
│ BTCUSDT     │ SL  │ SELL│    0.01  │ 45000.000     │ 45000.0 │ NEW     │ 2148628 │ 2026-04-02 10:30:16     │
│ ETHUSDT     │ TP  │ SELL│     1.0  │ 3500.000      │ 3500.0  │ NEW     │ 2148629 │ 2026-04-02 10:31:10     │
└─────────────┴─────┴─────┴──────────┴───────────────┴─────────┴─────────┴─────────┴─────────────────────────┘
```

---

### 6. Ver en formato JSON (para procesar)
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action json
```

---

### 7. CANCELAR un TP o SL específico
```bash
# Cancelar el algo order con ID 2148627
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --cancel 2148627
```

⚠️ **ADVERTENCIA**: Esto cancelará INMEDIATAMENTE el TP/SL. No hay confirmación.

---

### 8. Ver TODOS los TP/SL (de todos los pares)
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action all
```

---

### 9. Usar TESTNET de Binance
```bash
python3 get_tp_sl.py \
  --api-key "tu_testnet_api_key" \
  --api-secret "tu_testnet_api_secret" \
  --testnet
```

---

### 10. Sin tabla (si tabulate falla)
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action list \
  --no-table
```

---

## INTERPRETACIÓN DE RESULTADOS

### Estados (algoStatus):
| Estado | Significado | Acción |
|---|---|---|
| `NEW` | Orden pendiente, esperando | Normal |
| `TRIGGERED` | Orden fue activada y ejecutada | Completada |
| `CANCELED` | Orden fue cancelada | Finalizada |

### Tipo (orderType):
| Valor | Significado |
|---|---|
| `TAKE_PROFIT` | TP que ejecuta a precio LÍMITE |
| `TAKE_PROFIT_MARKET` | TP que ejecuta a precio MERCADO |
| `STOP_MARKET` | SL que ejecuta a precio MERCADO |
| `STOP` | SL que ejecuta a precio LÍMITE |

### Lado (side):
| Si tienes... | SELL | BUY |
|---|---|---|
| Posición LONG | ✅ TP/SL para cerrar | ❌ No aplica |
| Posición SHORT | ❌ No aplica | ✅ TP/SL para cerrar |

---

## CASOS DE USO PRÁCTICOS

### Caso 1: Monitorear mis TP/SL cada mañana
```bash
# Crear un script monitor_diario.sh
#!/bin/bash
echo "🔍 Verificando TP/SL pendientes..."
python3 get_tp_sl.py \
  --api-key "$BINANCE_API_KEY" \
  --api-secret "$BINANCE_API_SECRET"
```

Luego ejecutar:
```bash
chmod +x monitor_diario.sh
./monitor_diario.sh
```

---

### Caso 2: Revisar solo BTCUSDT
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --symbol BTCUSDT \
  --action summary
```

---

### Caso 3: Programar revisiones automáticas (Cron)
```bash
# Editar crontab
crontab -e

# Agregar (revisar cada hora)
0 * * * * cd /ruta/al/script && python3 get_tp_sl.py --api-key "KEY" --api-secret "SECRET" >> logs.txt 2>&1
```

---

### Caso 4: Integrar en un bot Python
```python
from get_tp_sl import BinanceFuturesTPSL

# Crear instancia
api = BinanceFuturesTPSL(
    api_key="tu_api_key",
    api_secret="tu_api_secret"
)

# Obtener TP/SL
tp_orders = api.get_take_profits("BTCUSDT")
sl_orders = api.get_stop_losses("BTCUSDT")

# Procesar
for tp in tp_orders:
    print(f"TP en {tp['triggerPrice']} para {tp['quantity']} BTC")

# Cancelar si necesario
api.cancel_tp_sl(2148627)
```

---

## TROUBLESHOOTING

### Error: "Invalid API-key"
**Solución**:
1. Verifica que tu API Key sea correcta (sin espacios)
2. Habilita "Futures" en los permisos de la API key
3. Espera 1-2 minutos a que se propague

---

### Error: "API key format invalid"
**Solución**:
- Copia la API Key directamente desde Binance
- No agregues espacios antes/después
- Usa comillas: `--api-key "tu_key_aqui"`

---

### Error: "Signature for this request was invalid"
**Solución**:
1. Verifica que el API Secret sea correcto
2. Tu reloj del sistema puede estar desincronizado
3. Sincroniza tu hora: `ntpdate -s time.nist.gov` (Linux)

---

### Error: "No module named 'tabulate'"
**Solución**:
```bash
pip install tabulate
# O usa el flag --no-table
python3 get_tp_sl.py --no-table ...
```

---

### No veo mis TP/SL
**Causas posibles**:
1. ✅ Ya fueron ejecutados (`algoStatus: TRIGGERED`)
2. ✅ Ya fueron cancelados (`algoStatus: CANCELED`)
3. ❌ No tiene permisos para Futures en la API key
4. ❌ El símbolo no tiene TP/SL activos

---

## EJEMPLOS AVANZADOS

### Obtener TP/SL y guardar en JSON
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action json > tp_sl_backup.json
```

---

### Obtener y procesar con jq (Linux)
```bash
python3 get_tp_sl.py \
  --api-key "tu_api_key" \
  --api-secret "tu_api_secret" \
  --action json | jq '.[] | select(.orderType == "TAKE_PROFIT")'
```

---

### Crear un reporte diario
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
python3 get_tp_sl.py \
  --api-key "$BINANCE_API_KEY" \
  --api-secret "$BINANCE_API_SECRET" \
  --action json > "reporte_tp_sl_$DATE.json"
echo "Reporte guardado: reporte_tp_sl_$DATE.json"
```

---

## SEGURIDAD

### ⚠️ NUNCA:
- ❌ Compartas tu API Secret
- ❌ Subas el script con API keys hardcodeadas
- ❌ Uses API keys en repositorios públicos
- ❌ Habilites más permisos de lo necesario

### ✅ SÍ:
- ✅ Usa variables de entorno
- ✅ Limita permisos a solo "Futures Reading"
- ✅ Usa una IP whitelist en Binance
- ✅ Desactiva la API key cuando no la uses

---

## REFERENCIA RÁPIDA

```bash
# Ver resumen
python3 get_tp_sl.py --api-key KEY --api-secret SECRET

# Ver solo TP
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action tp

# Ver solo SL
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --action sl

# Ver de un par
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --symbol BTCUSDT

# Cancelar TP/SL (ID: 2148627)
python3 get_tp_sl.py --api-key KEY --api-secret SECRET --cancel 2148627
```

---

## CONTACTO & SOPORTE

- 📖 Documentación oficial: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Current-All-Algo-Open-Orders
- 🐛 Reporte de bugs: Abre un issue en GitHub
- 💬 Preguntas: Consulta el FAQ de Binance

---

**Última actualización**: Abril 2, 2026
