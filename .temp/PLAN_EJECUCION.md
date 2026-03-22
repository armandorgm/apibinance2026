# PLAN DE EJECUCIÓN (Antigravity IDE)

## 🎯 OBJETIVOS
1. **Integración de Reglas**: Implementar trazabilidad en `.temp/` y registrar incidentes en `docs/incidents/`.
2. **Corrección de Orphan Sells (Long-Only)**: Asegurar que el tracker solo maneje compras antes que ventas y agrupe fills por `order_id`.
3. **Exact Match & Unrealized PnL**: Implementar emparejamiento exacto y toggle de PnL no realizado.

## 🛣️ HOJA DE RUTA
- [x] Fase 1: Inicialización de Estructura (Carpeta `.temp/` y tracking de `.gemini/`).
- [x] Fase 2: Refactorización de `tracker_logic.py` (Orden temporal `buy < sell`, Agrupación `order_id`).
- [x] Fase 3: Refactorización de `routes.py` (Parámetros de Stats).
- [x] Fase 4: Actualización de Frontend (Toggle de PnL).
- [x] Fase 5: Verificación con Tests y Reporte de Incidentes.

## 📝 LOG DE CAMBIOS (Tiempo Real)
- [2026-03-22] Iniciado análisis de la rama `fix/orphan-sells-long-only`.
- [2026-03-22] Generación inicial de `PLAN_EJECUCION.md`.
- [2026-03-22] Incorporada restricción temporal: No se puede emparejar un Sell con un Buy futuro.
- [2026-03-22] Refactorización completa de `TradeTracker` para manejar agrupaciones por `order_id`.
- [2026-03-22] Implementada visualización diferenciada entre posiciones Abiertas y Huérfanas.
- [2026-03-22] Verificación técnica exitosa mediante `test_verification.py`.
