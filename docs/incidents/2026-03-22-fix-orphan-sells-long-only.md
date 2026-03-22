# Problema: Orphan Sells y Falta de Exact Match en Long-Only

## Descripción
Se detectaron tres problemas críticos en la lógica del tracker:
1. Las ventas que ocurrían antes de cualquier compra (Orphan Sells) se emparejaban con compras futuras, creando operaciones "Short" falsas en un sistema diseñado para Long-only.
2. El algoritmo FIFO original dividía ejecuciones (fills) de forma agresiva, dificultando el seguimiento de órdenes completas de Binance.
3. No había una forma clara de visualizar el PnL no realizado (flotante) de posiciones abiertas.

## Solución
- **Rediseñé** el núcleo de emparejamiento en `tracker_logic.py` para agrupar fills por `order_id` antes de procesarlos.
- **Implementé** la restricción de Orden Temporal: un Sell solo puede cerrar un Buy si `buy.timestamp < sell.timestamp`.
- **Implementé** el "Exact Match": solo se cierran trades si las cantidades acumuladas de las órdenes son idénticas.
- **Lancé** actualizaciones en el frontend para resaltar visualmente las posiciones Huérfanas (naranja) vs las Abiertas (azul).
- **Integré** el soporte para `unrealized_pnl` en las estadísticas del dashboard.

## Impacto
La precisión de los cálculos de PnL ahora coincide exactamente con la operativa real de Binance Futures. Se eliminaron los trades ficticios generados por ordenamientos incorrectos y se mejoró la visibilidad del capital en riesgo (posiciones abiertas).

## Verificación
Validé la solución mediante un suite de pruebas personalizado (`test_verification.py`) que simuló escenarios de fills fragmentados, ventas huérfanas y emparejamientos exactos, resultando en un 100% de éxito.
