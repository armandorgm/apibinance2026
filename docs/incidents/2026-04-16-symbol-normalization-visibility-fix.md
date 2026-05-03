# Reporte de Incidente: Reparación de Normalización y Visibilidad

**Fecha**: 2026-04-16
**Falla**: Operaciones no visibles en la UI a pesar de existir en la DB.

## Problema
Se identificó que el sistema fallaba al traducir los símbolos enviados desde la UI (ej. `1000PEPEUSDC`) al formato estándar guardado en SQLite (`1000PEPE/USDC:USDC`). Esta falla ocurría principalmente cuando la API de Binance tardaba en responder o fallaba la sincronización de mercado, dejando la consulta a la base de datos con un símbolo incorrecto que retornaba 0 resultados.

## Solución
1.  **Heurística de Respaldo DIAS**: Implementé una lógica de "inteligencia local" en `backend/app/core/exchange.py` que permite al sistema deducir el formato CCXT a partir del ID de Binance si la normalización oficial falla.
2.  **Sincronización de Estrategias**: Se actualizó `backend/app/api/routes.py` para incluir `intent_fifo` en la lista blanca de procesamiento en tiempo real, garantizando la visibilidad inmediata de los cambios en el motor de emparejamiento.
3.  **Seguridad DIAS**: Se utilizó el `impact_analyzer.py` para confirmar que el cambio en el núcleo de normalización no afectó otros módulos críticos como el motor de órdenes del Bot.

## Impacto
*   **Visibilidad Restaurada**: Las operaciones previas en `binance_tracker_v3.db` ahora se visualizan correctamente al seleccionar el símbolo en el Dashboard.
*   **Resiliencia**: El sistema ahora es capaz de operar y mostrar datos históricos incluso bajo condiciones de latencia o fallos temporales de comunicación con Binance.

**Responsable**: Antigravity AI
**Estatus**: Solucionado y Verificado.
