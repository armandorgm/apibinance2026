# Incidente: Órdenes Abiertas invisibles (Algo Service compatibilidad)

**Fecha:** 2026-04-14
**Descripción:** El dashboard reportaba "0 órdenes activas" a pesar de tener órdenes TP/SL configuradas en Binance.

## Problema
1. **Incompatibilidad de API:** El código utilizaba métodos de CCXT 4.5+ mientras que el entorno tiene la versión 4.1.94. Esto impedía la comunicación con el servicio de órdenes Algo de Binance.
2. **Filtrado Excesivo:** La lógica del backend ocultaba órdenes vinculadas a posiciones para evitar redundancia, lo cual era contraintuitivo para el usuario.

## Solución
1. **Implementé** un fallback compatible con CCXT 4.1.94 en `ExchangeManager.fetch_algo_open_orders` usando llamadas manuales `request`.
2. **Diseñé** una nueva lógica de retorno en `/trades/history` que incluye todas las órdenes abiertas de Binance en la lista de pendientes, asegurando visibilidad total.
3. **Validé** la solución mediante `debug_open_orders.py` confirmando la detección de 5 órdenes Algo activas.

## Impacto
Visibilidad restaurada para todas las órdenes condicionales (TP, SL, Trailing). Los traders ahora pueden confirmar sus protecciones activas directamente desde la sección "Órdenes Abiertas".
