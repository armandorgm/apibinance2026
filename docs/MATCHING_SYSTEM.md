# Arquitectura del Sistema de Emparejamiento de Trades (Trade Matching)

## 📌 Visión General
El núcleo del proyecto evalúa un registro histórico de operaciones (Fills) extraídas desde Binance Futures y las empareja secuencialmente para calcular el PnL (Ganancias y Pérdidas) neto. Actualmente el sistema es "Long-only", emparejando operaciones de Venta (Salida) contra operaciones de Compra (Entrada) previas.

## 🧩 Componentes Principales

La lógica reside en `backend/app/services/tracker_logic.py`, regida por el Patrón de Diseño "Strategy" a través de la clase base abstracta `MatchStrategy`:

1.  **TrackerLogic (`TradeTracker`)**:
    *   Actúa como el orquestador principal.
    *   **Delegación**: Recibe los `fills` brutos y delega el emparejamiento a una estrategia específica dictada por la UI.
    *   **Pre-procesamiento (`_group_fills_by_order`)**: Agrupa fragmentos de un fill con el mismo `order_id` para reconstruir la orden original antes del emparejamiento, calculando el precio promedio ponderado.
    *   **Open Positions (`compute_open_positions`)**: Mapea qué fragmentos de orden fueron consumidos para identificar compras flotantes ("Open Longs") y ventas huérfanas ("Orphan Sells" o Stop Loss de datos no traqueados).

2.  **Estrategias de Emparejamiento**
    *   **`FIFOMatchStrategy`**: (First-In-First-Out). Toma una orden de Venta y busca iterativamente las Compras **más antiguas** disponibles. Permite **Partial Fills** (si la venta es de 2 BTC, y la compra más antigua es 1 BTC, consume ese 1 BTC y busca el 1 BTC restante en la siguiente compra).
    *   **`LIFOMatchStrategy`**: (Last-In-First-Out). Similar a FIFO, pero ordena los candidatos de Compra descendientemente por fecha. Toma las compras **más recientes** antes de la venta.
    *   **`AtomicMatchStrategy` (Atomic FIFO / Atomic LIFO)**: Diseñado para operaciones donde Binance ejecuta un Buy seguido de un Take Profit exacto. **No hace partial fills**. Solo empareja un Sell con un Buy que tenga **precisamente** la misma cantidad (`abs(buy - sell) < 1e-8`).

## ⚙️ Flujo de Procesamiento

1.  Obtener lista secuencial de `Fill` (ejecuciones) desde DB o Binance.
2.  Agrupar los Fills en Órdenes Unificadas usando `_group_fills_by_order`.
3.  Separar la lista en `buys` y `sells`.
4.  Iterar por los `sells`:
    *   Por cada `sell`, buscar en la lista de `buys` según la regla de la estrategia.
    *   Para cada match (parcial o total), calcular el fee proporcional (`(match_qty / buy_amount) * total_fee`) y el PnL bruto/neto.
    *   Construir el diccionario consolidado de la operación ("Trade") formateando `entry_amount`, `exit_amount`, duraciones y % de retorno.
5.  Restar los montos emparejados del "remainig_qty" del Buy original para no duplicar asignaciones.
6.  Retornar el Array in-memory de Trades emparejados.
