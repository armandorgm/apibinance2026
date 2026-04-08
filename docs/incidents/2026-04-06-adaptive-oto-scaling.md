# Implementación: Adaptive OTO Scaling (WebSockets)

## Fecha
2026-04-06

## Problema
El motor de reglas original evaluaba en un loop (Polling con _sleep_), lo que es ineficiente y demasiado lento para estrategias de alta frecuencia (como Chase & Scalp) que requieren responder a movimientos de un tick (milisegundos) en Binance Futures. Además, CCXT no soporta de forma nativa OTO puro para el intercambio.

## Solución
- Diseñé un modelo de suscripción WebSockets bajo demanda utilizando `ccxt.pro`.
- Implementé `StreamManager` (`stream_service.py`) para interconectar los canales `watchTicker` y `watchOrders` de manera asíncrona.
- Lideré el desarrollo de la tabla SQLite `bot_pipeline_processes` para gestión de estados resiliente a caídas.
- Implementé la acción dinámica `AdaptiveOTOScalingAction` capaz de ejecutar la persecución del precio en milisegundos (`cancel-and-replace` de Limit) y disparar el lado de Salida (TP) automáticamente tras un evento "FILLED" capturado por `watchOrders`.
- Automaticé la recolección de basura cerrando flujos inutilizados una vez logrado el "Take Profit" para optimizar la red.

## Impacto
El bot ahora escala a nivel HFT (High-Frequency) mitigando la latencia de polling y reduciendo el ancho de banda desperdiciado. Los módulos respetan los principios O/P de SOLID a través del `PipelineEngine`.
