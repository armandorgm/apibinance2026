# Binance Futures Tracker

Aplicación full stack moderna para rastrear y analizar operaciones en Binance Futures. El backend (Python/FastAPI) maneja la lógica de negocio y el cálculo FIFO, mientras que el frontend (Next.js) proporciona una interfaz visual moderna.

## 🏗️ Arquitectura

```
├── backend/          # API Python con FastAPI
│   ├── app/
│   │   ├── main.py              # Configuración FastAPI
│   │   ├── api/routes.py        # Endpoints REST
│   │   ├── core/
│   │   │   ├── config.py        # Configuración
│   │   │   └── exchange.py      # Gestión CCXT/Binance
│   │   ├── db/
│   │   │   └── database.py      # Modelos SQLModel
│   │   └── services/
│   │       └── tracker_logic.py # Lógica FIFO
│   └── requirements.txt
│
└── frontend/         # Dashboard Next.js
    ├── app/          # App Router
    ├── components/   # Componentes React
    ├── hooks/        # React Query hooks
    └── lib/          # Utilidades y API client
```

## 🚀 Inicio Rápido

### Backend

1. Navegar al directorio backend:
```bash
cd backend
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales de Binance
```

5. Ejecutar servidor:
```bash
python run.py
# o
uvicorn app.main:app --reload --port 8000
```

El backend estará disponible en `http://localhost:8000`

### Frontend

1. Navegar al directorio frontend:
```bash
cd frontend
```

2. Instalar dependencias:
```bash
npm install
```

3. Configurar variables de entorno:
```bash
cp .env.local.example .env.local
# Ajustar NEXT_PUBLIC_API_URL si es necesario
```

4. Ejecutar aplicación:
```bash
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## 📋 Características

### Backend
- ✅ API REST con FastAPI
- ✅ Conexión con Binance Futures usando CCXT
- ✅ Base de datos SQLite con SQLModel
- ✅ Algoritmo FIFO para emparejar compras/ventas
- ✅ Cálculo de PnL neto (descontando comisiones)
- ✅ Rate limiting para proteger contra límites de API
- ✅ Documentación automática (Swagger UI)

### Frontend
- ✅ Dashboard moderno con Next.js 14
- ✅ Tabla interactiva de operaciones
- ✅ Gráfico de precios con Recharts
- ✅ Estadísticas en tiempo real
- ✅ Sincronización con Binance
- ✅ Gestión de estado con React Query
- ✅ Diseño responsive con Tailwind CSS

## 🔑 Endpoints API

- `GET /api/trades/history?symbol=BTC/USDT` - Obtener historial de trades
- `POST /api/sync?symbol=BTC/USDT` - Sincronizar con Binance
- `GET /api/stats?symbol=BTC/USDT` - Obtener estadísticas
- `GET /api/symbols` - Listar símbolos disponibles

Documentación interactiva: `http://localhost:8000/docs`

## 🔐 Seguridad

- Las credenciales de Binance se almacenan en variables de entorno (`.env`)
- CORS configurado para permitir solo el frontend autorizado
- Rate limiting para proteger contra límites de API de Binance

## 📝 Notas

- La lógica de negocio (FIFO y cálculo de PnL) está 100% en el backend Python
- El frontend solo consume la API y visualiza los datos procesados
- La base de datos SQLite se crea automáticamente en el primer uso
- Se recomienda usar Binance Testnet para desarrollo (`TESTNET=true` en `.env`)

## 🛠️ Tecnologías

**Backend:**
- Python 3.10+
- FastAPI
- SQLModel (SQLAlchemy)
- CCXT
- SQLite

**Frontend:**
- Next.js 14
- TypeScript
- React Query
- Tailwind CSS
- Recharts

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
