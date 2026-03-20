# Carga diferida ("Lazy Loading") de operaciones históricas (2026-03-20)

## Problema inicial
Binance restringe la recuperación de trades a ventanas de tiempo que no superen los 7 días. Previamente, si la base de datos estaba vacía o no tenía datos antiguos, el sistema solo traía los últimos 7 días. El usuario necesitaba obtener trades de hasta 3 meses (y potencialmente más en el futuro) sin bloquear el flujo de la aplicación ni ejecutar grandes descargas síncronas masivas de una sola vez.

## Solución técnica aplicada
1. **Backend (`core/exchange.py`, `api/routes.py`)**:
   - Modificación en el método `fetch_my_trades` encapsulador de CCXT para que soporte parámetros directos adicionales (`params`), insertando de ser necesario el `endTime`.
   - Modificación en `routes.py` para añadir el endpoint `POST /api/sync/historical`. 
   - La lógica del nuevo endpoint ubica en la base de datos el trade más antiguo del par seleccionado, establece su fecha como límite superior (`endTime`) y desplaza la ventana a exactamente 7 días antes (`startTime = endTime - 7_days`).
2. **Frontend (`lib/api.ts`, `hooks/use-trades.ts`, `app/page.tsx`)**:
   - Se construyó el hook mutante de React Query `useSyncHistoricalTrades` referenciando el nuevo endpoint.
   - En el panel principal del frontend, se incluyó un botón con animación de carga diseñado como "Cargar previos (7 días)" (Load older trades), que interconecta el llamado a dicho hook y reactivamente regenera PnL y caché mediante desvalidación de QueryKey.

## Impacto
El sistema ahora soporta de manera eficiente "lazy loading" del historial. Mantiene inactividad mínima sin afectar la sincronización hacia adelante (datos recientes), permite recargar el historial bajo demanda sin duplicados, limitando adecuadamente la carga en la API de Binance de forma orgánica por parte del usuario.
