# PROJECT MAP - Binance Futures Tracker

## Visión General
Rastreador de operaciones para Binance Futures con soporte para emparejamiento FIFO/LIFO, cálculo de PnL neto y visualización en tiempo real.

## Stack Tecnológico
- **Backend**: Python 3.10+, FastAPI, SQLModel (SQLite), CCXT.
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, TanStack Query, Recharts.

## Diccionario de Directorios
- `backend/app/api/`: Endpoints REST.
- `backend/app/core/`: Configuración y gestor de exchange.
- `backend/app/db/`: Modelos de base de datos (`Fill`, `Trade`).
- `backend/app/services/`: Lógica de negocio (`TrackerLogic`).
- `frontend/app/`: Páginas y layouts de Next.js.
- `frontend/components/`: Componentes UI reutilizables.
- `frontend/lib/`: Utilidades, cliente API y motor de trading.
  - `tradingStrategy.ts`: Definición de reglas funcionales (Array de evaluadores).
  - `ruleEngine.ts`: Motor funcional de evaluación de estrategias.
- `docs/incidents/`: Registro de incidentes y resoluciones.
- `docs/MATCHING_SYSTEM.md`: Arquitectura detallada del sistema de emparejamiento (Strategy pattern, FIFO/LIFO/Atomic).

## Flujos Críticos de Datos
1. **Sincronización**: Binance API -> `exchange.py` -> `fills` table -> `tracker_logic.py` -> `trades` table.
2. **Visualización**: `routes.py` -> `api.ts` -> React Query -> `trade-table.tsx` / `trade-chart.tsx`.
3. **Formateo**: Precios brutos -> `lib/utils.ts` (`formatPrice`) -> UI.
## Responsabilidades de Módulos (Actualizado 2026-03-24)
- `frontend/lib/utils.ts`: Gestiona el formateo dinámico de precios, cantidades y porcentajes para activos de cualquier valor nominal.
- `backend/app/services/tracker_logic.py`: Implementa el Patrón Strategy (FIFO, LIFO, ATOMIC). `compute_open_positions` delega ahora en `match_trades()` con la estrategia seleccionada, garantizando consistencia entre posiciones cerradas y flotantes.
- `backend/app/api/routes.py`: FIFO/LIFO/Atomic se calculan siempre en vivo desde fills; solo `atomic_fifo` lee la DB pre-procesada. `sync/historical` respeta la estrategia seleccionada.
- `frontend/app/page.tsx`: Orquesta la carga de datos históricos manteniendo el estado de búsqueda para evitar solapamientos y periodos vacíos.
- `backend/tests/test_matching_strategies.py`: Suite pytest parametrizada con 16 casos cubriendo exact/partial/inverted match, orden FIFO vs LIFO, y posiciones abiertas por estrategia.
- `frontend/lib/ruleEngine.ts`: Motor de reglas desacoplado que evalúa el contexto de trading contra un array de funciones evaluadoras distribuidas en `tradingStrategy.ts`.
