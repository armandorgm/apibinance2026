# Plan de Ejecución - Fix Visibilidad Órdenes Abiertas

## Estado: COMPLETADO

## Problema Identificado
La sección "Órdenes Abiertas" mostraba 0 órdenes pendientes debido a dos causas:
1. **Error de Compatibilidad CCXT:** Se estaba llamando a un método (`fapiprivate_get_openalgoorders`) que no existe en la versión de CCXT instalada (`4.1.94`). Esto causaba que todas las órdenes Algo (TP/SL) fallaran silenciosamente.
2. **Filtrado de Lógica:** Las órdenes que estaban vinculadas a una posición abierta (como TP o SL) eran filtradas de la lista de órdenes "standalone" para evitar duplicidad técnica, pero esto provocaba que el usuario no visualizara sus órdenes activas en la sección correspondiente.

## Acciones Realizadas
1. **Corrección en `exchange.py`:** Se cambió la llamada dinámica por una llamada manual compatible con CCXT 4.1.94 utilizando `exchange.request('openAlgoOrders', ...)`.
2. **Corrección en `routes.py`:** Se eliminó el filtro que excluía las órdenes vinculadas de la lista de visualización. Ahora todas las órdenes abiertas en Binance aparecen en la sección "Órdenes Abiertas", independientemente de si están vinculadas a una posición o no.
3. **Verificación:** Se ejecutó un script de depuración (`debug_open_orders.py`) que confirmó que ahora se detectan y devuelven correctamente las 5 órdenes pendientes encontradas en la cuenta.

## Estado Final
- Backend operativo con soporte para órdenes Algo en CCXT 4.1.94.
- Frontend ahora muestra correctamente las órdenes TP/SL activas.
- Logs confirman "Total: 5 (Std: 0, Algo: 5)" y "Pending orders in API response: 5".

¿Deseas eliminar los temporales o aplicar un plan reparador/modificador/restaurador?
