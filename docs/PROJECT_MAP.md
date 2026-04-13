# PROJECT MAP - Binance Futures Tracker

## Visión General
Rastreador de operaciones para Binance Futures con soporte para emparejamiento FIFO/LIFO, cálculo de PnL neto y visualización en tiempo real.

## Stack Tecnológico
- **Backend**: Python 3.10+, FastAPI, SQLModel (SQLite), CCXT.
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, TanStack Query, Recharts.

## Diccionario de Directorios
- `backend/app/api/`: Endpoints REST.
- `backend/app/core/`: Configuración y gestor de exchange.
- `backend/app/db/`: Modelos de base de datos (`Fill`, `Trade`, `Order`, `BotConfig`).
- `backend/app/domain/orders/`: Núcleo de la arquitectura de órdenes (SOLID). `BaseOrder`, `OrderFactory`, `OriginResolver`.
- `backend/app/services/`: Lógica de negocio (`TradeTracker`, `BotService`, `HistoryFormatter`).
- `frontend/app/`: Páginas y layouts de Next.js.
- `frontend/components/`: Componentes UI reutilizables.
- `frontend/lib/`: Utilidades, cliente API y motor de trading.
  - `tradingStrategy.ts`: Definición de reglas funcionales (Array de evaluadores).
  - `ruleEngine.ts`: Motor funcional de evaluación de estrategias.
- `docs/incidents/`: Registro de incidentes y resoluciones.
- `docs/MATCHING_SYSTEM.md`: Arquitectura detallada del sistema de emparejamiento (Strategy pattern, FIFO/LIFO/Atomic).
- `docs/GLOSSARY.md`: Glosario oficial de términos y nomenclatura del proyecto (Posición, Orden B/C, Fill).
- `frontend/app/exchange-logs/`: Monitor interactivo central para reportes y respuestas CCXT.

## Flujos Críticos de Datos
1. **Sincronización**: Binance API -> `exchange.py` (Unified native CCXT fetch for Standard + Algo CONDITIONAL) -> `ensure_orders_exist` -> `basic_orders` / `conditional_orders` / `fills` -> `tracker_logic.py` -> `trades` table.
2. **Visualización**: `routes.py` (Unión virtual de órdenes normalizadas por CCXT + hidratación de fills) -> `api.ts` -> React Query -> `trade-table.tsx` (expandible) / `trade-chart.tsx`.
3. **Relación de Datos**: 1 Orden (Virtual normalizada) -> N Fills (Executions). Agrupación en `tracker_logic.py` e hidratación dinámica en `routes.py`.
4. **Formateo**: Precios brutos -> `lib/utils.ts` (`formatPrice`) -> UI.
5. **Ejecución Autónoma**: `BotConfig` (DB) -> `BotService` (Background Task) -> CCXT -> Binance API -> `BotSignal` (DB).

## Responsabilidades de Módulos (Actualizado 2026-04-01)
- `backend/app/services/history_formatter.py`: Abstrae el formateo y acomodo de resultados (Patrón Strategy) bajo los principios Open-Closed y SRP para ordenar la visualización combinada de trades cerradas y flotantes.
- `frontend/lib/utils.ts`: Gestiona el formateo dinámico de precios, cantidades y porcentajes para activos de cualquier valor nominal.
- `backend/app/services/tracker_logic.py`: Implementa el Patrón Strategy (FIFO, LIFO, ATOMIC) referenciado al cruce de trades puros.
- `backend/app/api/routes.py`: Endpoints para sync de trades y gestión de balances. Implementa la **Hidratación Dinámica de Fills** para el historial (atomic_fifo) asegurando transparencia total al expandir filas en el frontend.
- `frontend/components/trade-table.tsx`: Tabla interactiva con soporte para **filas expandibles** y sub-tablas de ejecuciones detalladas (lucide-react).
- `frontend/components/open-trades-table.tsx`: Visualizador premium de **órdenes pendientes** (Limit, Conditional, Algo) filtradas del historial activo para mayor visibilidad estratégica.
- `frontend/app/page.tsx`: Orquesta del dashboard incluyendo `BalanceWidget`, `BotMonitor` y filtros dinámicos (como Query Params inyectados hacia useTrades).
- `backend/app/services/bot_service.py`: Ejecuta órdenes transformando el monto inversión configuado (USD Notional) a cantidad exacta de contratos vía matemática (`Notional / Live Market Price`), pasando por el filtro de CCXT `amount_to_precision` para lograr compatibilidad estricta con Binance eliminando errores `-4164 MIN_NOTIONAL` y `-4111 PRECISION`.
- `frontend/app/settings/page.tsx`: Vista de control paramétrico estricto para el Bot Autónomo. La UI aclara la lógica de apalancamiento vs input en notional.
- `frontend/components/balance-widget.tsx`: Dashboard Balance View con pestañas e interfaz unificada.
- `backend/app/services/unified_counter_order_service.py`: Motor estratégico bi-direccional (UCOE) que genera contrapartidas (Long/Short) basadas en el historial real de 7 días de Binance, gestionando automáticamente el flag `reduceOnly` y utilizando unidades estándar de contratos (Factor 1).
- `frontend/components/ucoe-activity-panel.tsx` & `ucoe-preview-modal.tsx`: Interfaz de usuario para la ejecución estratégica de órdenes espejo/contrapartida con ajuste de profit dinámico (0.05% - 30%).
- `backend/app/api/routes.py`: Incorpora los endpoints descriptivos `/api/unified-counter-order-engine/*` para la orquestación del UCOE.

## AI Agent Configuration (Updated 2026-04-04)

- **`AGENTS.md` (project root):** Single source of truth for ALL AI agents (Antigravity, RooCode, Continue, Cursor, GitHub Copilot, Claude Dev). Contains project overview, tech stack, key components, Binance API notes, agent roles, execution standards, GitFlow, documentation protocol, and code style. **This file supersedes all other agent configuration files.**
- `.agents/workflows/`: Slash commands for Antigravity (`/gitflow-process`, `/orquestador`). Still active and referenced from `AGENTS.md`.
- `.agents/skills/`: Antigravity skill definitions. Still active.
- `.cursorrules`: Redirect → points to `AGENTS.md` (Cursor backward compatibility).
- `.gemini/gemini.md`: Redirect → points to `AGENTS.md` (Antigravity backward compatibility).
