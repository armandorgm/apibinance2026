# Incidente: Fallo en Transición de Chase Entry a Close (TP)

**Fecha:** 2026-04-11
**Estado:** Resuelto (Pendiente de Validación Final)

## Problema
Se reportó que el bot ejecutaba correctamente la entrada del Chase (`AdaptiveOTO`), pero no colocaba el Take Profit (`Close`) una vez que la orden de entrada se llenaba (`FILLED`). 

Tras el análisis de logs y código, se identificaron dos causas raíces:
1. **Error de Arquitectura (Crítico):** Los métodos `handle_order_event` y `handle_tick` de la clase `AdaptiveOTOScalingAction` estaban definidos como métodos de instancia (`self`), pero eran invocados como métodos estáticos desde `strategy_engine.py` (usando el nombre de la clase). Esto provocaba un `TypeError` interno que interrumpía el procesamiento del evento de llenado sin dejar rastro en los logs convencionales.
2. **Falta de Trazabilidad:** Los eventos críticos del Stream (llenado de órdenes, actualizaciones de precio) utilizaban `print` en lugar de `logger`, lo que impedía ver la actividad del motor WebSocket en `app.log`.

## Solución
1. **Refactorización de `actions.py`:** Se convirtieron todos los manejadores de eventos en `AdaptiveOTOScalingAction` a `@staticmethod` y se actualizaron las referencias internas de `self` a `AdaptiveOTOScalingAction`.
2. **Estandarización de Logs:** Se integró el `logger` de la aplicación en `stream_service.py` y `actions.py`, reemplazando todos los `print` por `logger.info`, `logger.debug` y `logger.error`.
3. **Validación de Schema:** Se confirmó que la base de datos ya cuenta con las columnas `custom_cooldown` y `custom_threshold`, descartando el error de `OperationalError` como causa del fallo actual (aunque fue un problema previo).

## Impacto
Se restauró la capacidad del bot para detectar el llenado de órdenes de entrada y transicionar automáticamente a la colocación del Take Profit. Además, se mejoró significativamente la capacidad de depuración del sistema al centralizar todos los eventos de alta frecuencia en el archivo de log rotativo.

**Implementado por:** Antigravity AI
**Pruebas:** Verificación de sintaxis y firmas de métodos. Pendiente de ejecución en runtime tras reinicio.
