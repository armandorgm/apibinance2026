# Incidente: Órdenes Algo con Unidades en Cero y Desajuste de Mapeo Dominio

## Problema
El usuario reportó que las **Algo Orders** (Take Profits, Stop Loss) se visualizaban con un valor de **0** en el motor UCOE, a pesar de existir órdenes activas en Binance. 

### Análisis de Causa Raíz
1.  **Divergencia de APIs**: Tras la migración de Binance (Diciembre 2025), las órdenes condicionales se gestionan en el "Algo Service". 
2.  **Mapeo Manual Deficiente**: En un intento previo (V5.2) de obtener estas órdenes, se utilizó una petición `request` directa a la API de Binance. El JSON resultante usa la clave `origQty`.
3.  **Fallo de Dominio**: El componente `OrderFactory.py` y el motor UCOE estaban programados para buscar `totalQty` o `quantity` en el caso de fuentes tipo `ALGO`, ignorando el campo `origQty` que Binance entrega para órdenes condicionales (`TAKE_PROFIT_MARKET`, etc.).

### Errores de Diagnóstico Mitigados
*   **Falsa Premisa de `closePosition`**: Se hipotetizó inicialmente que el valor 0 se debía a órdenes de "Cierre de Posición" sin cantidad explícita. La auditoría de los datos brutos (raw) desmintió esto: la información residía en `origQty` y simplemente no estaba siendo leída.

## Solución (V5.4 - "The CCXT Way" + V5.5 "Classification Robustness")
Se restauró la lógica de obtención delegando la normalización a la librería CCXT:
1.  **Unificación**: Se utiliza `exchange.fetch_open_orders(symbol, params={'algoType': 'CONDITIONAL'})`.
2.  **Normalización Automática**: CCXT realiza el mapeo interno de `origQty` -> `amount` de forma nativa.
3.  **Refinamiento de Clasificación (V5.5)**: Se detectó que CCXT a veces mapea `TAKE_PROFIT_MARKET` al tipo genérico `limit` en su campo unificado. Se ajustó el motor UCOE para auditar el campo `info['orderType']` y asegurar que estas órdenes se cuenten como **Algo Orders** y no como **Basic Orders**.
4.  **Preservación de Estabilidad**: Se mantuvieron los ajustes de latencia y la configuración de `warnOnFetchOpenOrdersWithoutSymbol: False`.

## Impacto
*   **Precisión Quirúrgica**: El motor UCOE ahora suma correctamente la exposición de las órdenes pendientes.
*   **Arquitectura Limpia**: Se eliminó código redundante de mapeo manual en la capa de infraestructura (`exchange.py`).
*   **Sincronización**: El Dashboard refleja la realidad de la cuenta sin discrepancias.

---
*Implementado por Antigravity (IA) - 2026-04-12*
