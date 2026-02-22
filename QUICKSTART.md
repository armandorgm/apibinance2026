# Guía de Inicio Rápido

## Prerrequisitos

- Python 3.10 o superior
- Node.js 18 o superior
- npm, yarn o pnpm
- Credenciales de API de Binance Futures

## Configuración Paso a Paso

### 1. Backend (Python/FastAPI)

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Copiar el archivo de ejemplo y editar con tus credenciales
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env con tus credenciales de Binance:
# BINANCE_API_KEY=tu_api_key_aqui
# BINANCE_API_SECRET=tu_api_secret_aqui

# Ejecutar servidor
python run.py
```

El backend estará disponible en `http://localhost:8000`
Documentación API: `http://localhost:8000/docs`

### 2. Frontend (Next.js)

Abre una nueva terminal:

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install
# o
yarn install
# o
pnpm install

# Configurar variables de entorno (opcional, por defecto usa localhost:8000)
# copy .env.local.example .env.local  # Windows
# cp .env.local.example .env.local  # Linux/Mac

# Ejecutar aplicación
npm run dev
# o
yarn dev
# o
pnpm dev
```

El frontend estará disponible en `http://localhost:3000`

## Primer Uso

1. **Sincronizar datos**: En el frontend, haz clic en el botón "Sincronizar con Binance" para traer tus operaciones desde Binance Futures.

2. **Visualizar trades**: Una vez sincronizado, verás tus operaciones en la tabla con:
   - Entrada y salida de cada trade
   - PnL neto (descontando comisiones)
   - Porcentaje de ganancia/pérdida
   - Duración de cada operación

3. **Ver estadísticas**: Las tarjetas superiores muestran:
   - Total de trades
   - PnL neto acumulado
   - Win rate
   - PnL promedio

## Solución de Problemas

### Error de conexión con Binance
- Verifica que tus credenciales API estén correctas en `.env`
- Asegúrate de que tu API key tenga permisos de lectura en Binance Futures
- Si usas Testnet, configura `TESTNET=true` en `.env`

### Error de CORS
- Verifica que `CORS_ORIGINS` en `.env` incluya `http://localhost:3000`
- Reinicia el servidor backend después de cambiar `.env`

### No aparecen trades
- Asegúrate de haber ejecutado operaciones en Binance Futures
- Verifica que el símbolo seleccionado coincida con tus operaciones
- Revisa la consola del navegador para errores

## Estructura de Archivos Importantes

### Backend
- `backend/app/main.py` - Configuración FastAPI
- `backend/app/api/routes.py` - Endpoints de la API
- `backend/app/services/tracker_logic.py` - Lógica FIFO (núcleo del sistema)
- `backend/app/core/exchange.py` - Conexión con Binance

### Frontend
- `frontend/app/page.tsx` - Página principal
- `frontend/components/trade-table.tsx` - Tabla de operaciones
- `frontend/components/trade-chart.tsx` - Gráfico de precios
- `frontend/lib/api.ts` - Cliente API para comunicarse con backend

## Próximos Pasos

- Personaliza los símbolos disponibles en el selector
- Agrega más métricas y análisis
- Implementa filtros y búsqueda en la tabla
- Exporta datos a CSV/Excel
- Agrega notificaciones para trades importantes
