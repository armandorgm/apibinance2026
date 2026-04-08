# Incidente: Implementación de Filas Expandibles y Transparencia en Trades

**Fecha:** 2026-04-08
**Estado:** Resuelto ✅

## Problema
El sistema agrupaba ejecuciones (Fills) correctamente, pero la interfaz de usuario no permitía ver el detalle de cada ejecución individual. Esto dificultaba la auditoría de órdenes grandes fraccionadas. Además, al intentar implementarlo inicialmente, el API devolvía listas vacías porque no "hidrataba" los datos de las ejecuciones desde la tabla `fills` al consultar el historial guardado (`atomic_fifo`).

## Solución
1. **Frontend**: Se integró `lucide-react` y se rediseñó `trade-table.tsx` para soportar filas expandibles mediante el estado `expandedRows`. Se creó un componente `FillsSubTable` para mostrar el detalle de cada trade.
2. **Backend (Core)**: Se modificó `tracker_logic.py` para preservar objetos `Fill` completos durante el proceso de agrupación y emparejamiento.
3. **Backend (API)**: Se implementó un parche de hidratación en `routes.py` que realiza un cruce eficiente (batch query) entre la tabla de `Trade` y la tabla de `Fill` por `order_id` antes de enviar la respuesta al frontend.
4. **Testing**: Se creó la suite `tests/services/test_order_fill_nesting.py` bajo metodología TDD para asegurar la integridad de la relación 1:N entre órdenes y ejecuciones.

## Impacto
- Mejora significativa en la transparencia de datos para el usuario final.
- Estructura de datos unificada para trades abiertos y cerrados.
- Base para futuras auditorías de comisiones por trade individual.

---
**Implementado por:** Antigravity AI
**Validado por:** Tester Subagent (Browser)
