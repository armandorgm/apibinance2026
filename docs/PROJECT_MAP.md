# PROJECT MAP - Binance Futures Tracker

## Visión General
Rastreador de operaciones para Binance Futures con soporte para emparejamiento FIFO/LIFO, cálculo de PnL neto y visualización en tiempo real.

## Stack Tecnológico
- **Backend**: Python 3.10+, FastAPI, SQLModel (SQLite), CCXT.
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, TanStack Query, Recharts.

## Diccionario de Directorios
- `backend/app/api/`: Endpoints REST.
- `backend/app/core/`: Configuración y gestor de exchange.
- `backend/app/db/`: Modelos de base de datos (`Fill`, `Trade`, `BotConfig`).
- `backend/app/services/`: Lógica de negocio (`TrackerLogic`, `TradingBot`).
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
4. **Ejecución Autónoma**: `BotConfig` (DB) -> `BotService` (Background Task) -> CCXT -> Binance API -> `BotSignal` (DB).

## Responsabilidades de Módulos (Actualizado 2026-04-01)
- `frontend/lib/utils.ts`: Gestiona el formateo dinámico de precios, cantidades y porcentajes para activos de cualquier valor nominal.
- `backend/app/services/tracker_logic.py`: Implementa el Patrón Strategy (FIFO, LIFO, ATOMIC).
- `backend/app/api/routes.py`: Endpoints para sync de trades y gestión de balances. Incluye protección activa para asegurar configuraciones válidas (`trade_amount > 0`).
- `frontend/app/page.tsx`: Orquesta del dashboard incluyendo `BalanceWidget` y `BotMonitor`.
- `backend/app/services/bot_service.py`: Ahora consume el `trade_amount` explícito de la base de datos para ejecutar el volumen configurado por el usuario, sustituyendo montos hardcodeados por parametrización viva, evadiendo el error "min notional".
- `frontend/app/settings/page.tsx`: Vista de control paramétrico estricto para el Bot Autónomo (símbolo, intervalo, monto, activación).
- `frontend/components/balance-widget.tsx`: Dashboard Balance View con pestañas e interfaz unificada. 
