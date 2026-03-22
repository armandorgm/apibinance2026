# Implementación LIFO (2026-03-20)

## Problema inicial
El sistema originalmente emparejaba las operaciones ("fills") de Binance usando exclusivamente el algoritmo FIFO (First-In-First-Out) en el backend para generar las estadísticas y calcular el PnL. El usuario solicitó poder contar con una lógica alternativa LIFO (Last-In-First-Out) que pudiera alternarse y visualizarse desde el dashboard del frontend.

## Solución técnica aplicada
1. **Backend (`tracker_logic.py`, `routes.py`)**:
   - Se renombró la clase `FIFOTracker` a `TradeTracker` permitiendo flexiblidad.
   - Se implementó el algoritmo correspondiente en el método `match_trades_lifo` empleando un enfoque de pilas ("stack") que empareja las ventas más recientes con las compras más recientes.
   - Se ajustó el método para calcular las posiciones abiertas usando ambas lógicas.
   - Se actualizaron los endpoints REST `/trades/history` y `/stats` para aceptar el parámetro opcional `logic`. Al usar la lógica `lifo`, el cálculo de emparejamiento se ejecuta dinámicamente en memoria desde la tabla "fills", para no interferir con los datos cacheados por FIFO.
2. **Frontend (`api.ts`, `use-trades.ts`, `page.tsx`)**:
   - Se adaptaron las llamadas a la API y los *React Query Hooks* (`useTrades`, `useStats`) insertando el nuevo parámetro `logic` en las URLs y claves de caché.
   - Se integró un selector `<select>` en la vista principal (`page.tsx`) que despacha el estado actual del método de emparejamiento, actualizando la tabla y estadísticas de forma reactiva.

## Impacto
El proyecto dispone ahora de un selector amigable en el frontend que recalcula la vista de las operaciones, métricas y PnL usando FIFO o LIFO simultáneamente sin alterar la persistencia principal en la base de datos (que se mantiene consistente bajo validaciones FIFO estándar). Todo opera fluidamente con un solo clic.
