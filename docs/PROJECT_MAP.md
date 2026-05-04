# PROJECT MAP - Binance Futures Tracker

## Visión General
Rastreador de operaciones para Binance Futures con soporte para emparejamiento FIFO/LIFO, cálculo de PnL neto y visualización en tiempo real. 
> [!IMPORTANT]
> Ver [PRODUCT_OWNER_VISION.md](file:///f:/apibinance2026/docs/PRODUCT_OWNER_VISION.md) para el manifiesto estratégico oficial.

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
- `scripts/impact_analyzer.py`: Motor central de DIAS (Dependency & Impact Analysis System) para prevenir regresiones.
- **Intent Matcher**: Algoritmo de emparejamiento 1:1 basado en intención (descartando SL).
- `frontend/app/intent-timeline/`: Vista cinemática independiente con estética Neón.
- `docs/MATCHING_SYSTEM.md`: Arquitectura detallada del sistema de emparejamiento (Strategy pattern, FIFO/LIFO/Atomic).
- `docs/GLOSSARY.md`: Glosario oficial de términos y nomenclatura del proyecto (Posición, Orden B/C, Fill).
- `docs/BINANCE_CHANGELOG.md`: Registro histórico de la API de Binance optimizado para agentes de IA.
- `frontend/app/exchange-logs/`: Monitor interactivo central para reportes y respuestas CCXT.

## Flujos Críticos de Datos
1. **Sincronización**: Binance API -> `exchange.py` (Unified native CCXT fetch for Standard + Algo CONDITIONAL via manual request) -> `ensure_orders_exist` -> `basic_orders` / `conditional_orders` / `fills` -> `tracker_logic.py` -> `OrderFactory` (Normalización V5.9) -> `trades` table.
2. **Visualización**: `routes.py` (Unión virtual de órdenes normalizadas por CCXT + hidratación de fills) -> `api.ts` -> React Query -> `trade-table.tsx` (expandible) / `trade-chart.tsx`.
3. **Relación de Datos**: 1 Orden (Virtual normalizada) -> N Fills (Executions). Agrupación en `tracker_logic.py` e hidratación dinámica en `routes.py`.
4. **Formateo**: Precios brutos -> `lib/utils.ts` (`formatPrice`) -> UI.
5. **Ejecución Autónoma**: `BotConfig` (DB) -> `BotService` (Background Task) -> CCXT -> Binance API -> `BotSignal` (DB).

## Responsabilidades de Módulos (Actualizado 2026-04-01)
- `backend/app/core/exchange.py`: Registro para data de mercado y manipulación de precios. Incluye `get_tick_size` para obtener precisión dinámica de Binance/CCXT.
- `backend/app/services/pipeline_engine/native_actions.py`: Contiene la lógica de ejecución en modo NATIVE. Implementa el algoritmo Front-Running Maker (Bid+1/Ask-1) y gestión de errores Post-Only (-5022).
- `backend/app/services/tracker_logic.py`: Implementa el Patrón Strategy (FIFO, LIFO, ATOMIC, INTENT, NETTING) referenciado al cruce de trades puros.
- `backend/app/api/routes.py`: Endpoints para sync de trades y gestión de balances. Implementa la **Hidratación Dinámica de Fills** para el historial (atomic_fifo) asegurando transparencia total al expandir filas en el frontend.
- `frontend/components/trade-table.tsx`: Tabla interactiva con soporte para **filas expandibles** y sub-tablas de ejecuciones detalladas (lucide-react).
- `frontend/components/open-trades-table.tsx`: Visualizador premium de **órdenes pendientes** (Limit, Conditional, Algo) filtradas del historial activo para mayor visibilidad estratégica.
- `frontend/app/page.tsx`: Orquesta del dashboard incluyendo `BalanceWidget`, `BotMonitor` y filtros dinámicos (como Query Params inyectados hacia useTrades).
- `backend/app/services/bot_service.py`: Ejecuta órdenes transformando el monto inversión configuado (USD Notional) a cantidad exacta de contratos vía matemática (`Notional / Live Market Price`), pasando por el filtro de CCXT `amount_to_precision` para lograr compatibilidad estricta con Binance eliminando errores `-4164 MIN_NOTIONAL` y `-4111 PRECISION`.
- `frontend/app/settings/page.tsx`: Vista de control paramétrico estricto para el Bot Autónomo. La UI aclara la lógica de apalancamiento vs input en notional.
- `frontend/components/balance-widget.tsx`: Dashboard Balance View con pestañas e interfaz unificada.
- `backend/app/services/unified_counter_order_service.py`: Motor estratégico bi-direccional (UCOE V5.9) que genera contrapartidas (Long/Short) basadas en el historial de Binance, integrando visibilidad de **Algo Orders (TP/SL/Trailing)** y gestionando automáticamente el flag `reduceOnly` utilizando unidades estándar de contratos (Factor 1).
- `backend/app/api/routes.py`: Incorpora los endpoints descriptivos `/api/unified-counter-order-engine/*` para la orquestación del UCOE.
- `scripts/impact_analyzer.py`: Herramienta de seguridad implementada en 2026-04-16. Escanea el proyecto, construye grafos de dependencia y mapea impactos entre backend y frontend para asegurar cambios libres de errores.
- `backend/app/services/scheduled_scaler_bot.py`: Orquestador de escalado (Bot C). Implementa lógica de validación de margen consciente del apalancamiento (leverage-aware) y ejecución dinámica de Chase V2 (Adaptive OTO Scaling). Incluye trazabilidad detallada de idempotencia para validación de ciclos (ID/Originator).

## AI Agent Configuration (Updated 2026-04-04)

- **`AGENTS.md` (project root):** Single source of truth for ALL AI agents (Antigravity, RooCode, Continue, Cursor, GitHub Copilot, Claude Dev). Contains project overview, tech stack, key components, Binance API notes, agent roles, execution standards, GitFlow, documentation protocol, and code style. **This file supersedes all other agent configuration files.**
- `.agents/workflows/`: Slash commands for Antigravity (`/gitflow-process`, `/orquestador`). Still active and referenced from `AGENTS.md`.
- `.agents/skills/`: Antigravity skill definitions. Still active.
- `.cursorrules`: Redirect → points to `AGENTS.md` (Cursor backward compatibility).
- `.gemini/gemini.md`: Redirect → points to `AGENTS.md` (Antigravity backward compatibility).
