# PLAN DE EJECUCIÓN - Ordenamiento de Historial de Operaciones

## Objetivos
1.  **Orden Cronológico Absoluto**: Mezclar el registro de operaciones cerradas y posiciones abiertas en una sola lista ordenada.
2.  **Principios SOLID (Strategy Pattern)**: Desacoplar la lógica de ordenamiento (`HistoryFormatter`).
3.  **Criterio Arquitecto (Dynamic Sorting)**: Implementar ordenamientos múltiples (`recent`, `oldest`, `pnl_desc`) usando Query Params, aprovechando la infraestructura Strategy montada.

## Hoja de Ruta (Ejecutada)
- [x] **Fase 1: Capa de Servicios (Backend)**
    - [x] Módulo `services/history_formatter.py`.
    - [x] Clase `TradeSorterStrategy` base (OCP).
    - [x] Estrategias `SortByEntryDateDesc`, `SortByEntryDateAsc`, `SortByPnLDesc`.
    - [x] Contexto `HistoryFormatter` (SRP).
- [x] **Fase 2: Motor de Routing (Backend)**
    - [x] Importado `HistoryFormatter` al endpoint `/trades/history`.
    - [x] Añadido parámetro `sort_by` al router mapeando subclases concretas.
- [x] **Fase 3: Integración Frontend (API & Hook)**
    - [x] Adaptado el parámetro opcional `sortBy` en el fetch de `api.ts`.
    - [x] Añadida validación de Query Key en `use-trades.ts`.
- [x] **Fase 4: Modificación Dashboard (Frontend UI)**
    - [x] `<select>` creado para habilitar el state `sortBy` ("Más Recientes", "Más Antiguas", "Mayor PnL").

## Log de Cambios
- **2026-04-01 02:13**: Generación del plan arquitectónico.
- **2026-04-01 02:17**: Usuario aprueba el plan delegando Open Question. Se implementa ordenamiento total dinámico full stack.
- **2026-04-01 02:20**: Culminación con éxito de la arquitectura Strategy tanto en Python como React.

## ESTADO: FINALIZADO
- Feature completada. Archivo listo para ser commiteado al repositorio.
