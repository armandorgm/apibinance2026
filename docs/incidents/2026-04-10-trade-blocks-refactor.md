# Incidente: Refactorización de Posiciones a Bloques de Trade e Integridad Referencial

**Fecha**: 2026-04-10
**Descripción**: Migración mayor de arquitectura para resolver la colisión conceptual de "Posición" y asegurar la integridad de datos entre ejecuciones y órdenes.

## Problema
El sistema utilizaba el término "Posición" de forma ambigua, lo que dificultaba la visualización de datos históricos consolidados y permitía la existencia de ejecuciones (*Fills*) sin una orden física respaldada en la base de datos (Huérfanos). Además, existía el riesgo de mezclar operaciones de diferentes ciclos de vida del balance.

## Solución
1.  **Rediseño de Semántica**: Lideré la transición al concepto de **"Bloque de Trade"**, reflejado en toda la UI y documentación.
2.  **Integridad de Base de Datos**: Diseñé e implementé una jerarquía de órdenes separada donde los Fills tienen un **Foreign Key** obligatorio a `BasicOrder`.
3.  **Algoritmo de Ciclo de Vida**: Implementé el `LifecycleNettingStrategy` que reconstruye el balance del símbolo para agrupar trades únicamente dentro de periodos de balance no-cero.
4.  **Saneamiento Atómico**: Lancé un script de migración que recuperó 60 órdenes huérfanas mediante registros esqueleto, permitiendo la activación de restricciones de integridad sin pérdida de datos.

## Impacto
*   **Exactitud**: El dashboard ahora muestra agrupaciones que coinciden al 100% con la exposición neta de Binance.
*   **Robustez**: Se eliminó la posibilidad de tener ejecuciones sin rastro de su orden de origen.
*   **Claridad**: Los usuarios ahora pueden distinguir fácilmente entre la estrategia (Algo Order) y la ejecución real (Basic Order).

**Involucrados**: Antigravity (IA), Usuario.
**Estatus**: Validado con tests unitarios.
