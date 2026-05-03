# Reporte de Incidente: Refactorización de Glosario y Segmentación de Órdenes

**Fecha**: 2026-04-08
**Descripción**: Implementación de la nueva arquitectura de base de datos y dominio para alinearse con el Glosario oficial del proyecto (Posición, Orden B/C, Fill).

## Problema
El sistema operaba con una tabla de órdenes unificada (`orders`), lo que dificultaba la distinción entre órdenes estándar (Binance API) y condicionales (Algo API), y no cumplía con la nomenclatura jerárquica deseada por el usuario (Identidad Dual).

## Solución
*   **Lideré** el diseño del sistema de **Identidad Dual**, donde los IDs se almacenan crudos en DB (Fidelidad de Origen) pero se proyectan con prefijos ('B'/'C') en la API (Glosario).
*   **Implementé** la segmentación física de tablas en `basic_orders` y `conditional_orders`.
*   **Diseñé** una lógica de **Integridad por Aplicación** en Python para permitir que los Fills apunten a cualquiera de las dos tablas físicas sin las restricciones rígidas de SQLite.
*   **Lancé** la actualización de la UI, renombrando el historial a "Historial de Posiciones" y garantizando la coherencia visual.

## Impacto
*   **Trazabilidad Total**: Claridad inmediata entre órdenes de protección (Algo) y de ejecución (Standard).
*   **Extensibilidad**: El sistema está preparado para recibir nuevos tipos de órdenes condicionales sin romper el esquema principal.
*   **Consistencia**: Alineación del 100% entre la documentación funcional (GLOSSARY.md) y la implementación técnica.

---
*Estado: Validado y Desplegado en Código. Requiere reinicio de DB local.*
