# PLAN_EJECUCION.md - Restablecimiento de Vinculación de Órdenes Condicionales (OTO/TP)

**Estado actual:** FASE DE CIERRE (FINALIZADO)

## Objetivo
Restaurar los badges Algo/TP en el historial de operaciones, diagnosticando por qué las 8 órdenes de `1000PEPEUSDC` pendientes no se estaban vinculando con sus respectivos Trades a pesar de ser procesadas desde el backend.

## Hoja de Ruta
1. `[x]` Escribir un script de validación local (`verify_algo_orders.py`) para confirmar la persistencia de los payloads `TAKE_PROFIT_MARKET` en el endpoint de Binance 2025.
2. `[x]` Diagnosticar la desaparición de los campos `create_time_ms` y `conditional_kind` debido al refactor de `OrderFactory`.
3. `[x]` Inyectar nuevamente la extracción algorítmica de atributos condicionales explícitos con `create_time` y `conditional_kind` en `OrderFactory`.
4. `[x]` Modificar el mapeo persistente hacia la base de datos `Order` en `routes.py`.
5. `[x]` Restaurar el constructor en la instancia devuelta a FastAPI (`OrderResponse`), devolviendo el `is_algo` y los valores a la UI para reactivar `conditional_exit_link.py`.
6. `[x]` Ejecución de Test Suite Completa. Re-verificación. (100% Passed).

## Logs de Cambios
- 16:00: FASE INICIAL. Detección de órdenes desaparecidas de PEPE en interfaz. Se procede a crear el `verify_algo_orders.py`.
- 16:15: FASE DE PROGRESO. Aprobación del Usuario. Se modificó el factory de Dominio (`base_order.py`, `order_factory.py`) y las colecciones pydantic en rutas (`routes.py`) adaptándolos.
- 16:20: FASE DE CIERRE. Se ejecutan los test (`pytest backend/tests/ -v`) con un status total de éxito. El frontend ahora debe mostrar correctamente las etiquetas.
