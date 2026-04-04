# AGENTS.md

> **Single source of truth** for all AI agents, IDEs, and coding assistants working in this repository.
> Compatible with: Antigravity, RooCode, Continue, Cursor, GitHub Copilot, Claude Dev, and any AGENTS.md-aware tool.

---

## Project Overview

**apibinance2026** is a full-stack automated trading dashboard for Binance Futures (USDⓈ-M). It provides:
- Real-time trade history with FIFO/LIFO PnL matching
- Automated trading bot with rules engine executing orders on Binance Futures
- Bot monitoring dashboard with signal history and rule trigger tracking
- Full visibility of all order types: standard orders + Algo conditional orders (Stop Loss, Take Profit, Trailing Stop)

**Stack:** Python 3.11 / FastAPI · Next.js 14 / TypeScript · SQLite (SQLModel) · CCXT + Direct Binance REST API · React Query

---

## Project Structure

```
apibinance2026/
│
├── backend/                          # API Backend (Python/FastAPI)
│   └── app/
│       ├── main.py                   # FastAPI setup, CORS, main routes
│       ├── api/
│       │   └── routes.py             # REST endpoints (GET /trades/history, POST /sync, etc.)
│       ├── core/
│       │   ├── config.py             # Configuration and environment variables
│       │   └── exchange.py           # CCXT/Binance management, rate limits
│       ├── db/
│       │   └── database.py           # SQLModel models (Fill, Trade), DB management
│       └── services/
│           └── tracker_logic.py      # FIFO/LIFO/Qty-match logic — pairs buys/sells, calculates PnL
│
├── frontend/                         # Dashboard Frontend (Next.js)
│   └── app/
│       ├── layout.tsx                # Main layout with QueryProvider
│       ├── page.tsx                  # Main dashboard page
│       └── globals.css               # Global Tailwind styles
│   └── components/
│       ├── trade-table.tsx           # Operations table (green/red PnL)
│       ├── trade-chart.tsx           # Recharts chart with entry/exit points
│       ├── bot-monitor.tsx           # Bot monitoring dashboard
│       ├── sync-button.tsx           # Binance sync button
│       └── stats-card.tsx            # Statistics cards
│   └── hooks/
│       └── use-trades.ts             # React Query hooks (useTrades, useStats, useSyncTrades)
│   └── lib/
│       └── api.ts                    # API client (fetchTrades, syncTrades, fetchStats)
│
├── docs/                             # Documentation and standards
│   ├── PROJECT_MAP.md                # Collective brain — always keep updated
│   ├── STANDARDS.md                  # Style and convention guides
│   ├── incidents/                    # Problem resolution logs (YYYY-MM-DD-description.md)
│   └── logs/                         # Feature execution plans archive
│
├── AGENTS.md                         # ← YOU ARE HERE — Universal AI agent config
├── .agents/                          # Antigravity-specific agents/workflows/skills
│   └── workflows/                    # Slash command workflows
│       ├── gitflow-process.md        # /gitflow-process
│       └── orquestador.md            # /orquestador
├── .cursorrules                      # Cursor compat redirect → see AGENTS.md
├── .gemini/gemini.md                 # Antigravity compat redirect → see AGENTS.md
├── README.md
├── QUICKSTART.md
└── .gitignore
```

---

## Key Components

### Backend

| Component | File | Responsibility |
|-----------|------|----------------|
| **tracker_logic.py** | `backend/app/services/` | FIFO algorithm for buy/sell matching, net PnL calculation (discounting commissions), partial fill handling |
| **exchange.py** | `backend/app/core/` | CCXT + direct Binance REST calls, rate limiting, retries |
| **database.py** | `backend/app/db/` | `Fill` model (raw Binance executions), `Trade` model (matched ops with PnL), SQLModel ORM |
| **routes.py** | `backend/app/api/` | `GET /api/trades/history`, `POST /api/sync`, `GET /api/stats`, `GET /api/open-orders` |

### Frontend

| Component | File | Responsibility |
|-----------|------|----------------|
| **page.tsx** | `frontend/app/` | Orchestrates all components, manages selected symbol state |
| **bot-monitor.tsx** | `frontend/components/` | Real-time bot status, signal history, rule trigger monitoring (5s auto-refresh) |
| **trade-table.tsx** | `frontend/components/` | Responsive table with PnL colors, date/duration formatting |
| **use-trades.ts** | `frontend/hooks/` | React Query cache/sync, hooks, auto-invalidation after sync |

---

## Binance API Critical Notes

### Futures USDⓈ-M Orders

**Main endpoint:** `POST /fapi/v1/order` — requires HMAC-SHA256 signature and API key in header.

**Invalid combinations to avoid:**
- `reduceOnly` cannot be used in Hedge Mode or with `closePosition`
- `price` and `priceMatch` are mutually exclusive
- `selfTradePreventionMode` only takes effect when `timeInForce` is `IOC`, `GTC`, or `GTD`

**CRITICAL — 2025 Breaking Change:**  
As of **2025-12-09**, conditional orders (`STOP_MARKET`, `TAKE_PROFIT_MARKET`, `STOP`, `TAKE_PROFIT`, `TRAILING_STOP_MARKET`) migrated to the **Algo Service**. Using them on `/fapi/v1/order` after that date returns error `-4120 STOP_ORDER_SWITCH_ALGO`.  
**New endpoint: `/fapi/v1/algo/newOrder`**

**Testnet base URL:** `https://demo-fapi.binance.com` — use for all testing without risk.

### Open Orders Aggregation

The system must aggregate from **two sources** to get full order visibility:
1. `/fapi/v1/openOrders` — standard open orders
2. `/fapi/v1/algo/openOrders` — conditional Algo orders (SL, TP, Trailing)

---

## Agent Roles

This project uses three specialized agent personas:

| Role | Mandate | Primary Tools |
|------|---------|---------------|
| **Architect** | Analyze requirements, design technical strategy, delegate tasks. Primary tool: Planning Mode. | Planning Mode, documentation |
| **Developer** | Code implementation, refactoring, terminal operations. Receives only the technical context needed for the specific task. | Code editor, terminal |
| **Tester** | Validation specialist. Uses Browser Subagent for UI testing, DOM state capture, and verification session recording. | Browser Subagent |

**Orchestrator (`/orquestador`):** Low-consumption router. Mandate: Delegate, never process. Prohibits greetings or explanations. Always demands Unified Diff format. Output: `[Specialized Agent] → [Direct technical instruction]`.

---

## Execution Standards

Every AI agent working in this repository MUST follow this lifecycle:

### 1. Execution Plan Lifecycle (`.temp/` folder)

All complex procedures require mandatory real-time traceability inside `.temp/`:

- **Before (Initial Phase):** Generate `PLAN_EJECUCION.md` with roadmap and objectives.
- **During (Progress Phase):** Update the file with change logs, intercepted errors, and strategy adjustments.
- **After (Closing Phase):** Record the final system state.

**User Sovereignty:** On completion, the agent MUST NOT delete records. It will ask the user:
  - a) Delete temporaries.
  - b) Execute Repair Plan (fix failures).
  - c) Execute Modification Plan (adjust solution).
  - d) Execute Restoration Plan (revert to last stable step).

### 2. Context Switching & Branch Management

If a new plan or requirement does not correspond to the current Git branch:

- **Postponement Record:** Before switching context, update the current `PLAN_EJECUCION.md` with status `"POSTPONED"`, detailing what remains to be done.
- **Safety Stash:** Run `git stash` on current changes and record the stash pointer/name in the postponed plan document.
- **Branch Management:** Find an existing branch for the new plan; if none exists, create one with clear naming.

### 3. Latency Management (Local API)

Changes to the code are not instantaneous in the runtime:

- **Prudential Wait:** After modifying a local API, wait 5–10 seconds before attempting to execute or test the endpoint.
- **False Error Handling:** If a connection error or 500 is received immediately after a change, retry after an additional brief pause before reporting a failure.

### 4. Implementation & Testing Standards

Every new feature or fix must meet:

- **Mandatory Testing:** A task is NOT considered "finished" without corresponding tests (unit or integration). Organize in mirror folders (e.g., `src/auth` → `tests/auth`).
- **SOLID Principles:**
  - **S** (Single Responsibility): Separate business logic from persistence/UI.
  - **O/P** (Open/Closed): Prioritize extension via interfaces.
  - **D** (Dependency Inversion): Inject dependencies to facilitate Mocks/Stubs.
- **Simplicity Criterion:** If SOLID generates unnecessary over-engineering, prioritize clean, maintainable code (YAGNI).

### 5. Permanent Incident Log

Once the solution is validated and temporaries are closed, generate a report in `docs/incidents/`:

- **Naming:** `YYYY-MM-DD-short-description.md`
- **Structure:** Problem, Solution (including mention of tests), Impact.
- **Language:** Use ownership verbs (Led, Designed, Implemented, Launched).

### 6. Exit Protocol

On completion, the agent MUST emit:
> *"The execution cycle has concluded. Logs in `.temp/` and report in `docs/incidents/`. Branch/stash state has been managed as needed. Do you want to delete temporaries or apply a repair/modification/restoration plan?"*

---

## Branching & GitFlow

Full workflow defined in `.agents/workflows/gitflow-process.md` (slash command: `/gitflow-process`).

**Quick reference:**

1. Always start from `develop`.
2. Create feature branch: `git checkout -b feature/name develop`.
3. Work on your feature.
4. Commit changes: `git add . && git commit -m "feat: description"`.
5. Update `docs/PROJECT_MAP.md` incrementally.
6. Merge back with non-fast-forward: `git checkout develop && git merge --no-ff feature/name`.
7. Archive `.temp/` artifacts to `docs/logs/feature-name/` before closing.
8. Delete the feature branch: `git branch -d feature/name`.
9. For hotfixes, branch from `main` using `hotfix/name`.

**Important:** Always consult `docs/STANDARDS.md` before closing a task.

---

## Documentation Protocol

To avoid massive scans and facilitate onboarding of new agents or conversations:

- **Master File:** Keep `docs/PROJECT_MAP.md` updated at all times.
- **Discovery Protocol:** When reading a new file or modifying it, the agent must update the file's responsibility, flow, and relationship with other modules in this map.
- **Content:** General overview, stack, folder/file dictionary, and critical data flows.
- **Preservation Rule:** NEVER delete sections that have not been touched by the current task. Stored knowledge must persist for future agents and sessions.

---

## Code Style

### Developer Profile

- **Specialty:** Backend Developer (Node.js/TypeScript, Python, C++).
- **Hard Restriction:** Do NOT use Java under any circumstance.
- **Frontend Technologies:** React, Next.js (use `useState` and standard hooks).

### Development Principles (Must-Follow)

1. **Safe Hands:** Always prioritize solving real problems and stability over accumulating unnecessary complexity.
2. **Quantifiable Impact:** Every new function or service must include clear error handling and, where possible, metrics or logs to measure success. Describe results, not tasks.
3. **Ownership Verbs:** In comments and documentation, use leadership language: "Designed", "Implemented", "Launched".
4. **Skill Translation:** Adapt technical terminology to business priorities. Code must be clean but results-oriented.
5. **Risk Mitigation:** If a solution involves a drastic change or potential performance issue, mention it before implementing.

### TypeScript / Next.js

- Strong typing — avoid `any`.
- Use `formatPrice`, `formatAmount`, `formatPercentage` from `@/lib/utils`. Never use `.toFixed()` ad-hoc.
- Modular, clean components.

### Python / FastAPI

- Follow PEP 8 standards.
- Respect "Buy before Sell" principle and exact quantity matching in trade logic.
- PnL calculation must always subtract all commissions.
- After modifying the local API, wait 5–10 seconds before running tests (allow runtime reload).

---

## Security

- API credentials in `.env` files (never in source code).
- CORS configured for the specific frontend origin.
- Rate limiting on all Binance API requests.
- Data validation with Pydantic models.

---

## Database

- **SQLite** by default (easy development); PostgreSQL-ready for production.
- `fills` table: raw Binance executions.
- `trades` table: matched operations with PnL.
- Automatic migrations via SQLModel.

---

*Last updated: 2026-04-04 | Maintained by AI agents — update incrementally, never overwrite whole sections.*
