# Refactorización Long-Only y Exact Amount Matching (2026-03-20)

## Problema inicial
1. **Falsos trades Short:** El sistema registraba ventas como aperturas de posiciones cortas (Short) si el timestamp de la venta era anterior al de la compra, ya que la lógica predeterminada manejaba un sistema bidireccional. Esto confundía al usuario, cuya operativa es estrictamente Long.
2. **Partición de trades:** Las compras y ventas se emparejaban usando una lógica de llenado fraccional (`min(buy, sell)`). El usuario prefirió que las transacciones sólo se emparejen si las cantidades (`amount`) son exactamente iguales.
3. **Visibilidad del Floating PnL:** El usuario requería una manera de visualizar el resumen de ganancias sumando o excluyendo el PnL no realizado (Unrealized PnL) de los trades abiertos o sin emparejar.

## Solución técnica aplicada
1. **Agrupación por Órdenes (Backend):** 
   - Se añadió un paso previo en `TradeTracker` (`_group_fills`) que agrupa todos los *fills* fragmentados provenientes de Binance por su `order_id` o `trade_id`, fusionando sus cantidades y obteniendo un precio de entrada/salida ponderado. Esto soluciona la partición de la API.
2. **Emparejamiento Estricto Long-Only (Backend):**
   - Se reescribieron los algoritmos de `match_trades_fifo` y `lifo` suprimiendo las colas direccionales bidireccionales. 
   - Ahora, **sólo las compras abren posición**. Cuando llega una venta (`sell`), el algoritmo busca en la cola de compras un trade con *exactamente la misma cantidad*. Si lo encuentra, lo empareja; de lo contrario, la venta se cataloga como "orphan/unmatched" y se descarta del *match*.
4. **Depuración de Posiciones Abiertas (Backend):**
   - El método `compute_open_positions` se ajustó para no devolver `unmatched_sells` como posiciones abiertas. Esto asegura que en la UI solo se vean operaciones de tipo `BUY` como operaciones vivas.
5. **Limpieza de Caché de Trades:**
   - Se vació la tabla local `Trade` en SQLite para forzar una regeneración retroactiva con la nueva lógica estricta al sincronizar de nuevo.
3. **Toggle de Unrealized PnL (Frontend & Backend):**
   - Se modificó el endpoint `/api/stats` para aceptar la bandera `include_unrealized=true|false`.
   - Si está activa, el backend consulta el precio de mercado actual y calcula la ganancia flotante de todos los longs abiertos, sumándola al cálculo total neto del día.
   - En el frontend (`page.tsx`, `use-trades.ts`, `api.ts`) se cableó este estado reactivo dentro de un `<input type="checkbox">` de TailwindCSS.

## Impacto
El proyecto quedó ajustado específicamente al estilo de trading del usuario (Long-Only, entradas completas sin parcialidades), evitando registros fantasma de Shorting y permitiéndole flexibilizar los reportes de rendimiento al añadir o restar su posición flotante actual en tiempo real con solo un clic.
