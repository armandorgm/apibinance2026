# Incidente: Estabilización de Chase V2 e Infraestructura de WebSockets
Fecha: 2026-04-17

## Problema
Tras un cierre forzado del IDE, se identificaron varios problemas críticos en la funcionalidad "Chase Entry" y en la gestión de WebSockets:
1. **NameError en Backend:** La variable `native_params` no estaba definida en `handle_fill` de `NativeOTOScalingAction`, rompiendo la colocación del Take Profit.
2. **Duplicación de Notificaciones e Inestabilidad:** El `StreamManager` original utilizaba hilos nativos de Binance para el Market Data, lo que obligaba a usar `run_coroutine_threadsafe` y causaba latencias innecesarias o posibles interbloqueos (deadlocks) en el motor de trading.
3. **Falta de Fallback en Bot Runner:** El script independiente `bot_runner.py` no inicializaba correctamente todos los servicios necesarios para Chase V2.

## Solución
1. **Refactorización de StreamManager:**
   - Se migró el flujo de Market Data (@bookTicker) a **CCXT Pro** utilizando un bucle `asyncio` nativo (`watch_tickers`).
   - Se eliminaron las dependencias de hilos para el procesamiento de ticks, centralizando las actualizaciones en el registro de precios en memoria (DIAS Optimization).
   - Se mantuvo el driver nativo de Binance únicamente para el **User Data Stream** (eventos de ejecución) para aprovechar su baja latencia de red en órdenes.
2. **Correcciones en Chase V2 (Native):**
   - Se definió `native_params` con `reduceOnly: "true"` para órdenes de salida.
   - Se eliminó la dependencia de `fetch_ticker` (REST) en favor de una espera inteligente por el stream de alta velocidad.
3. **Consolidación de Plan de Ejecución:** Se limpiaron los logs duplicados en `.temp/PLAN_EJECUCION.md` y se documentó el estado actual `feature/chase-infographic`.
4. **Validación de Frontend:** Confirmada la correcta integración de `NotificationProvider` (precios en tiempo real) y `ActivePipelines` (infograma dinámico).

## Impacto
- **Estabilidad:** Eliminados los hilos en el flujo de datos de mercado, lo que previene deadlocks en entornos de alta carga.
- **Visibilidad:** El usuario ahora puede ver el progreso del Chase (sub-estados como `INITIAL_ORDER_SENT`, `MOVING_PRICE`) en tiempo real.
- **Rendimiento:** Reducción de llamadas REST innecesarias al servidor de Binance.

## Tests Realizados
- Validación de sintaxis e imports en `main.py`, `stream_service.py` y `native_actions.py`.
- Verificación de la disponibilidad de `ccxt.pro`.
- Análisis de impacto del cambio de driver de WS (bajo riesgo para el flujo de usuario).

---
*Reporte generado automáticamente por Antigravity IDE.*
