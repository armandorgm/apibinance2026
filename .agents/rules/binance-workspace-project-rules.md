---
trigger: always_on
---

# Estructura del Proyecto

## 📁 Estructura Completa

```
apibinance2026/
│
├── backend/                          # API Backend (Python/FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # ⚙️ Configuración FastAPI, CORS, rutas principales
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # 🔌 Endpoints REST (GET /trades/history, POST /sync)
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # ⚙️ Configuración y variables de entorno
│   │   │   └── exchange.py          # 🔗 Gestión CCXT/Binance, rate limits
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py          # 💾 Modelos SQLModel (Fill, Trade), gestión DB
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       └── tracker_logic.py     # 🧮 LÓGICA FIFO/LIFO/Qnty.match - Empareja buys/sells, calcula PnL
│   │
│   ├── requirements.txt              # 📦 Dependencias Python
│   ├── .env.example                  # 🔐 Ejemplo de variables de entorno
│   ├── .gitignore
│   ├── run.py                        # 🚀 Script de inicio
│   └── README.md
│
├── frontend/                         # Dashboard Frontend (Next.js)
│   ├── app/
│   │   ├── layout.tsx                # 📐 Layout principal con QueryProvider
│   │   ├── page.tsx                  # 🏠 Página principal (dashboard)
│   │   ├── globals.css               # 🎨 Estilos globales Tailwind
│   │   └── providers/
│   │       └── query-provider.tsx   # 🔄 React Query provider
│   │
│   ├── components/
│   │   ├── trade-table.tsx           # 📊 Tabla de operaciones (verde/rojo PnL)
│   │   ├── trade-chart.tsx           # 📈 Gráfico Recharts con puntos entrada/salida
│   │   ├── sync-button.tsx           # 🔄 Botón sincronización Binance
│   │   └── stats-card.tsx            # 📈 Tarjetas de estadísticas
│   │
│   ├── hooks/
│   │   └── use-trades.ts            # 🎣 React Query hooks (useTrades, useStats, useSyncTrades)
│   │
│   ├── lib/
│   │   └── api.ts                   # 🌐 Cliente API (fetchTrades, syncTrades, fetchStats)
│   │
│   ├── package.json                 # 📦 Dependencias Node.js
│   ├── tsconfig.json                # ⚙️ Configuración TypeScript
│   ├── tailwind.config.ts           # 🎨 Configuración Tailwind CSS
│   ├── next.config.js               # ⚙️ Configuración Next.js
│   ├── .env.local.example           # 🔐 Ejemplo variables de entorno
│   ├── .gitignore
│   └── README.md
│
├── docs/                             # Documentación y Estándares
│   ├── incidents/                    # Bitácoras de resolución de problemas
│   └── STANDARDS.md                  # Guías de estilo y convenciones
│
├── README.md                         # 📖 Documentación principal
├── QUICKSTART.md                    # 🚀 Guía de inicio rápido
├── PROJECT_STRUCTURE.md             # 📁 Este archivo
└── .gitignore                       # 🚫 Archivos ignorados por Git
```

## 🎯 Componentes Clave

### Backend

1. **`tracker_logic.py`** - El corazón del sistema
   - Algoritmo FIFO para emparejar compras/ventas
   - Cálculo de PnL neto (descontando comisiones)
   - Manejo de fills parciales

2. **`exchange.py`** - Gestión de Binance
   - Conexión CCXT con rate limiting
   - Fetch de trades desde Binance Futures
   - Manejo de errores y reintentos

3. **`database.py`** - Persistencia
   - Modelo `Fill`: ejecuciones crudas de Binance
   - Modelo `Trade`: operaciones emparejadas con PnL
   - SQLModel para ORM ligero

4. **`routes.py`** - API REST
   - `GET /api/trades/history` - Lista de trades procesados
   - `POST /api/sync` - Sincronizar con Binance
   - `GET /api/stats` - Estadísticas agregadas

### Frontend

1. **`page.tsx`** - Dashboard principal
   - Orquesta todos los componentes
   - Maneja estado del símbolo seleccionado
   - Integra tabla, gráfico y estadísticas

2. **`trade-table.tsx`** - Visualización de datos
   - Tabla responsive con colores PnL
   - Formateo de fechas y duraciones
   - Indicadores visuales de entrada/salida

3. **`trade-chart.tsx`** - Gráfico interactivo
   - Recharts para visualización
   - Marcadores de entrada/salida
   - Tooltips con información detallada

4. **`use-trades.ts`** - Gestión de estado
   - React Query para caché y sincronización
   - Hooks reutilizables para datos
   - Invalidación automática después de sync

## 🔐 Seguridad

- Credenciales API en `.env` (no en código)
- CORS configurado para frontend específico
- Rate limiting en requests a Binance
- Validación de datos con Pydantic

## 📊 Base de Datos

- **SQLite** por defecto (fácil desarrollo)
- Tabla `fills`: ejecuciones crudas
- Tabla `trades`: operaciones emparejadas
- Migraciones automáticas con SQLModel

## 🚀 Despliegue

### Backend
- FastAPI compatible con cualquier servidor ASGI
- Variables de entorno para configuración
- Base de datos puede cambiarse a PostgreSQL

### Frontend
- Next.js optimizado para producción
- Build estático posible
- Variables de entorno para API URL
