# Incidente: Fuga de Conexiones WebSocket y Desajuste de Precios Bid/Ask

**Fecha**: 2026-04-18
**Estado**: ✅ RESUELTO
**ID de Conversación**: 974b1c2d-a731-4da3-9af5-2e4e91f1ddb8

## Problema
Se identificaron tres fallos críticos en la infraestructura de tiempo real de Chase V2:
1. **Fuga de Recursos**: El `NotificationManager` no estaba limpiando las conexiones WebSocket cerradas, acumulando hasta 39 conexiones "zombie" que saturaban el backend.
2. **Invisible Bid/Ask**: Los precios en el panel de Chase Entry se mostraban como `---` debido a una discrepancia de normalización de símbolos entre el backend (CCXT) y el frontend (Raw Binance ID).
3. **Advertencias de Sesión**: Terminal inundada con errores de `Unclosed client session` y `ccxt requires an explicit .close()` al reiniciar el servidor.

## Solución Liderada
1. **Refactorización de WebSocket**: Implementé un sistema de rastreo por IDs únicos (UUID) en el backend y un bucle de limpieza proactivo en el método `broadcast`.
2. **Estrategia "Dual-Key"**: Diseñé e implementé una simplificación arquitectónica donde el backend emite tickers con ambos formatos de símbolo (Raw y CCXT). Esto permite al frontend realizar búsquedas directas $O(1)$ sin fallos de mapeo.
3. **Blindaje y Cierre**: Lancé hooks de apagado (`@app.on_event("shutdown")`) que cierran explícitamente las sesiones de CCXT y aiohttp, eliminando las advertencias en la terminal.
4. **Resiliencia de Endpoint**: Blindé el endpoint de `/balances` para evitar errores 500 ante glitches temporales de conectividad con Binance.

## Impacto
- **Limpieza**: La terminal ahora está libre de "ruido" y advertencias de sesiones no cerradas.
- **Visibilidad**: Precios Bid/Ask 100% operativos y sincronizados en tiempo real para todos los símbolos.
- **Estabilidad**: El sistema mantiene un conteo de conexiones preciso (0 al cerrar pestañas, 1-3 en uso nominal), eliminando el riesgo de leaks de memoria.

---
*Reporte generado automáticamente por Antigravity IDE.*
