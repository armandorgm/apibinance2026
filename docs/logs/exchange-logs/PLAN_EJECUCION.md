# Plan de Ejecución Temporal: Corrección de UI para Historial de Trades

## Fase Inicial
**Objetivo:** Identificar y corregir el error por el cual no se muestran las filas en la tabla del historial de operaciones en Next.js.
**Hipótesis:** El endpoint FastAPI `GET /api/trades/history` devolvía un error HTTP 500 por mala manipulación de strings o diccionarios al procesar `open_orders`.

## Fase de Progreso
1. **Intento de Sub-agente (Tester):** Se intentó delegar usando el `browser_subagent`, sin embargo su cuota de uso en el modelo ha sido agotada.
2. **Depuración Manual:** Análisis del flujo en `backend/app/api/routes.py` y el frontend (`frontend/components/trade-table.tsx`).
3. **Identificación del Bug:** 
    - Las órdenes devueltas por CCXT en Python son diccionarios (`dict`).
    - El código intentaba llamar a la propiedad mediante notación de punto: `order.info.get(...)`. Esto arroja un `AttributeError: 'dict' object has no attribute 'info'` causando una excepción en todo el endpoint y apagón completo de la tabla en el frontend.
    - Llamar a `.lower()` sobre valores nulos de `side`.
4. **Resolución:** Se usó `order.get('info', {}).get(...)` para acceder a la clave de forma segura y se agregaron validaciones condicionales `(raw.get('side') or '').lower()`.

## Fase de Cierre
- Parche completado y empujado al endpoint. El dashboard debería reaccionar automáticamente recuperando las operaciones tan pronto como se recargue.
- Estado: Exitoso.
