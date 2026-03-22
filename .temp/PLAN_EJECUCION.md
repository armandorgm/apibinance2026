# PLAN DE EJECUCIÓN - Corrección de Precios 0 en Frontend

## Objetivo
Corregir el problema donde "Precio Entrada" y "Precio Salida" se muestran siempre como 0 en la tabla de trades del frontend.

## Estado Inicial
- Rama: develop
- Síntoma: Precios de entrada y salida en 0 en el dashboard.

## Hoja de Ruta

### Fase 1: Investigación
1. [x] Revisar el modelo `Trade` en `backend/app/db/database.py` para verificar los campos de precio.
2. [x] Revisar la lógica de cálculo en `backend/app/services/tracker_logic.py` para ver si se asignan valores a estos campos.
3. [x] Probar el endpoint `GET /api/trades/history` para ver qué datos está enviando el backend.
4. [x] Revisar el frontend (`frontend/components/trade-table.tsx`) para verificar cómo se renderizan estos campos.
   - **Hallazgo:** El frontend usa `.toFixed(2)` para los precios. Como el usuario está operando `1000PEPE`, el precio es muy bajo (ej: 0.0033) y se redondea a 0.00.

### Fase 2: Implementación
5. [x] Crear una función de formateo de precios inteligente en el frontend que use más decimales si el precio es bajo.
6. [x] Aplicar la nueva función de formateo en `trade-table.tsx` para `entry_price` y `exit_price`.
7. [x] Corregir lints y errores de TypeScript en la implementación.

### Fase 3: Verificación
8. [x] Verificar que el backend envía los precios correctos mediante una llamada manual a `/api/trades/history`.
9. [x] Verificar que el frontend ya muestra los precios con los nuevos formateadores.

### Fase 4: Cierre
10. [x] Registrar el incidente en `docs/incidents/`.
11. [ ] Consultar al usuario sobre la eliminación de archivos temporales.

## Logs de Cambios
- [2026-03-22 04:18] Inicio del plan de ejecución.
- [2026-03-22 04:35] Hallazgo del error de redondeo en el frontend.
- [2026-03-22 04:40] Implementación de `utils.ts` y actualización de componentes `TradeTable`, `Home` y `TradeChart`.
- [2026-03-22 04:45] Verificación de datos en Backend satisfactoria.
- [2026-03-22 11:15] Cambio de rama a `fix/frontend-price-rounding` para cumplir con la política de gestión de ramas.
- [2026-03-22 11:20] Creación de `docs/PROJECT_MAP.md` y `docs/STANDARDS.md`.
- [2026-03-22 11:25] Ejecución de tests unitarios para `utils.ts` en `frontend/tests/utils_test.js`. Resultado: PASSED.
- [2026-03-22 11:30] Fin del ciclo de ejecución con cumplimiento total de reglas y workflows.
