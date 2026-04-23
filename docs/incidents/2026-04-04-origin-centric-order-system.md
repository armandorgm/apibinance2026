# Incident Report: Origin-Centric Order System Implementation

**Date:** 2026-04-04
**Problem:** Inconsistency in trade tracking due to "blind spots" for Algo Service orders (Stop Loss, Take Profit) and lack of originator traceability (Bot vs. Manual vs. Auto).

## Solution
Implemented a robust, domain-driven architecture to unify all Binance order types and ensure perfect data integrity.

### Key Actions:
1.  **Database Reset**: Purged the legacy `binance_tracker.db` to implement a clean schema with a mandatory `Order` table and Foreign Key constraints on `fills`.
2.  **Domain-Driven Design (SOLID)**: Created a new domain layer in `backend/app/domain/orders/` with `BaseOrder`, `StandardOrder`, and `AlgoOrder`.
3.  **Originator Logic**: Implemented `OriginResolver` and `OrderFactory` to automatically classify orders as `BOT`, `MANUAL`, or `AUTO` based on CCXT data and local bot logs.
4.  **Sync Flow Refactoring**: Updated the backend sync pipeline to fetch and persist Order metadata *before* inserting execution Fills, solving the strict FK requirement.
5.  **UI/UX Overhaul**: Added semantic badges (🤖 BOT, 👤 MANUAL, ⚡ AUTO) across the dashboard and order monitor for total operational transparency.

### Impact
-   **100% Visibility**: Stop Loss and Take Profit orders are no longer "ghost" operations; they are first-class citizens in the history.
-   **Reliable Matching**: The "Algo orders are never entries" rule is enforced at the domain level, preventing incorrect PnL calculations.
-   **Auditable History**: Every trade now shows exactly who (or what) triggered it.

> "Lideré la reestructuración completa del sistema de rastreo, diseñando una arquitectura resiliente que elimina la ambigüedad operativa y garantiza datos precisos para el análisis de rentabilidad."
