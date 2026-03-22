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
- `frontend/lib/`: Utilidades y cliente API.
- `docs/incidents/`: Registro de incidentes y resoluciones.

## Flujos Críticos de Datos
1. **Sincronización**: Binance API -> `exchange.py` -> `fills` table -> `tracker_logic.py` -> `trades` table.
2. **Visualización**: `routes.py` -> `api.ts` -> React Query -> `trade-table.tsx` / `trade-chart.tsx`.
3. **Formateo**: Precios brutos -> `lib/utils.ts` (`formatPrice`) -> UI.

## Responsabilidades de Módulos (Actualizado 2026-03-22)
- `frontend/lib/utils.ts`: Gestiona el formateo dinámico de precios, cantidades y porcentajes para activos de cualquier valor nominal.
- `backend/app/services/tracker_logic.py`: Implementa el algoritmo de matching exacto por cantidad y orden temporal.
