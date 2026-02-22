# Binance Futures Tracker - Frontend

Frontend desarrollado con Next.js 14 (App Router) y TypeScript para visualizar operaciones de Binance Futures.

## Estructura del Proyecto

```
frontend/
├── app/
│   ├── layout.tsx           # Layout principal
│   ├── page.tsx             # Página principal
│   ├── globals.css          # Estilos globales
│   └── providers/
│       └── query-provider.tsx  # React Query provider
├── components/
│   ├── trade-table.tsx      # Tabla de operaciones
│   ├── trade-chart.tsx      # Gráfico de operaciones
│   ├── sync-button.tsx      # Botón de sincronización
│   └── stats-card.tsx       # Tarjeta de estadísticas
├── hooks/
│   └── use-trades.ts       # Hooks de React Query
├── lib/
│   └── api.ts              # Cliente API
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## Instalación

1. Instalar dependencias:
```bash
npm install
# o
yarn install
# o
pnpm install
```

2. Configurar variables de entorno:
```bash
cp .env.local.example .env.local
# Editar .env.local con la URL del backend (por defecto http://localhost:8000)
```

## Ejecución

```bash
npm run dev
# o
yarn dev
# o
pnpm dev
```

La aplicación estará disponible en `http://localhost:3000`

## Tecnologías Utilizadas

- **Next.js 14** - Framework React con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos utilitarios
- **React Query (TanStack Query)** - Gestión de estado y caché de datos
- **Recharts** - Gráficos interactivos
- **date-fns** - Manipulación de fechas

## Características

- 📊 Tabla interactiva de operaciones con colores para PnL positivo/negativo
- 📈 Gráfico de precios con marcadores de entrada y salida
- 🔄 Sincronización con Binance Futures
- 📈 Estadísticas en tiempo real (total trades, win rate, PnL promedio)
- 🌙 Soporte para modo oscuro (basado en preferencias del sistema)
