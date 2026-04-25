# Incidente 2026-04-25: Estabilización del Scaler Bot y API Native

## Problema
El Scaler Bot (Bot C) presentaba fallos intermitentes y críticos que impedían su ejecución:
1. **Error -1021 (Timestamp)**: Los relojes del servidor local y de Binance estaban desincronizados por ~1.5s, lo que provocaba el aborto de las peticiones.
2. **Error `orderId is mandatory`**: Llamada incorrecta a `get_open_orders` (singular) en lugar de `get_orders` (plural) en la librería nativa.
3. **Inconsistencia de Parcheo**: El offset de tiempo no se aplicaba a todas las clases de la librería de Binance.

## Solución
- **Diseñé** e **Implementé** un sistema de re-sincronización dinámica en `BinanceNativeEngine`. Ahora, ante un error `-1021`, el motor sincroniza el tiempo, actualiza el `time_offset` global y reintenta la petición automáticamente.
- **Corregí** la integración con `binance-futures-connector` para usar el endpoint plural de órdenes abiertas.
- **Lancé** una versión mejorada de monkey-patching que cubre `binance.api`, `binance.um_futures` y `binance.websocket`.
- **Agregué** validaciones de margen más robustas y logging preventivo en el Scaler Bot.

## Impacto
El Scaler Bot ahora es capaz de completar su ciclo de análisis (inferencia de lado, búsqueda de TP, cálculo de profit) y lanzar ejecuciones de `Chase V2` incluso si existe drift en el reloj del sistema. La infraestructura de comunicación con Binance es ahora resiliente a errores de sincronización temporales.

**Estado Final**: Estable y Verificado.
