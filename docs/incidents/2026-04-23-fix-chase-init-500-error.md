# Incidente: Error 500 en /api/chase/init por Desincronización de Tiempo

**Fecha**: 2026-04-23
**Estado**: Resuelto

## Problema
Al intentar inicializar un proceso de Chase V2 a través del endpoint `/api/chase/init`, el servidor devolvía un `500 Internal Server Error`. 

Tras investigar los logs, se identificaron dos causas:
1. **Causa Raíz**: El reloj local de Windows estaba adelantado ~165ms respecto a los servidores de Binance, provocando el error `-1021 INVALID_TIMESTAMP` en la API de Binance Futures.
2. **Causa Técnica (Backend)**: El manejador de excepciones en `chase_routes.py` capturaba cualquier error (incluyendo `HTTPException` de 400 por fallos de Binance) y lo re-lanzaba como un Error 500 genérico, ocultando el problema real.

## Solución
1. **Sincronización Automática de Tiempo**: Se modificó `BinanceNativeEngine` (`binance_native.py`) para calcular el *offset* de tiempo contra la API de Binance al inicializarse y aplicar un *monkey-patch* al generador de timestamps de la librería `binance-futures-connector`.
2. **Resiliencia de Red**: Se añadió `recvWindow=10000` por defecto en todas las órdenes nativas para tolerar pequeñas latencias.
3. **Refactorización de Rutas**: Se corrigió `chase_routes.py` para que no capture `HTTPException`, permitiendo que los errores 400 (Bad Request) de Binance lleguen correctamente al cliente con su mensaje descriptivo.

## Impacto
El sistema ahora es inmune a desajustes de reloj en Windows de hasta varios segundos y proporciona mensajes de error claros en lugar de errores 500 genéricos. Las pruebas de integración confirmaron el inicio exitoso del proceso Chase V2.

---
**Implementado por**: AI Agent (Antigravity)
