# Binance Futures Tracker - Backend API

Backend API desarrollado con FastAPI para rastrear y calcular PnL de operaciones en Binance Futures.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # Endpoints de la API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuración y variables de entorno
│   │   └── exchange.py      # Gestión de conexión CCXT con Binance
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py      # Modelos SQLModel y gestión de base de datos
│   └── services/
│       ├── __init__.py
│       └── tracker_logic.py # Lógica FIFO para emparejar trades
├── requirements.txt
├── .env.example
└── README.md
```

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales de Binance
```

## Ejecución

```bash
uvicorn app.main:app --reload --port 8000
```

La API estará disponible en `http://localhost:8000`

## Endpoints

- `GET /api/trades/history?symbol=BTC/USDT` - Obtener historial de trades procesados
- `POST /api/sync?symbol=BTC/USDT` - Sincronizar trades desde Binance
- `GET /api/symbols` - Obtener lista de símbolos disponibles
- `GET /api/stats?symbol=BTC/USDT` - Obtener estadísticas de trading

## Documentación API

Una vez ejecutando el servidor, visita:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
