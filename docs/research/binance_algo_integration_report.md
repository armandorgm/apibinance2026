# Knowledge Report: Binance Algo Orders & UCOE Engine V5.9

**Fecha:** 2026-04-14
**Autor:** Armando Gonzalez (via Antigravity AI)
**Estado:** Implementado y Validado

## 1. Integración de Algo Orders (TP/SL/Trailing)

### Descubrimiento Técnico
Se identificó que las órdenes condicionales de Binance Futures (Take Profit, Stop Loss, Trailing Stop) no residen en el mismo endpoint que las órdenes estándar (`/fapi/v1/openOrders`).

*   **Endpoint Real:** `GET /fapi/v1/openAlgoOrders`
*   **Compatibilidad CCXT:** En versiones anteriores a la 4.5 (como la utilizada en este entorno), el método nativo `fapiprivate_get_openalgoorders` puede no estar presente o ser inestable.
*   **Solución Modular:** Se optó por una llamada manual mediante el motor de peticiones de CCXT:
    ```python
    res = await exchange.request('openAlgoOrders', 'fapiPrivate', 'GET', params)
    ```

### Clasificación y Normalización
Se utilizó el patrón **OrderFactory** (SOLID) para unificar la entrada de datos:
*   Las órdenes se etiquetan con `_source='algo'` o `_source='standard'`.
*   Se extrae la cantidad original (`origQty`) y el tipo de activación (`stopPrice`).

---

## 2. Motor UCOE V5.9 (Unified Counter-Order Engine)

### El Concepto de "Equilibrio Final"
El motor ahora calcula la exposición neta combinando tres capas de datos:
1.  **Posición Actual (Pos Units):** Contratos abiertos en el mercado.
2.  **Órdenes Algo (Algo Ops):** TP, SL y Trailing activos.
3.  **Órdenes Básicas (Basic Ops):** Límite y Mercado estándar.

**Fórmula de Equilibrio:**
`Resultado Neto = PosUnits + StandardOrders + (AlgoOrders - StopLossOrders)`
*Nota: Se excluyen los Stop Loss del balance de cobertura para evitar sesgos de seguridad en la proyección.*

### Ajuste de "True Units"
Se eliminó el factor de normalización (Legacy Factor 1000) para símbolos como `1000PEPE`. Ahora el sistema opera 1:1 con el conteo de contratos de la plataforma, eliminando la ambigüedad en el cálculo de márgenes.

---

## 3. Incidentes y Soluciones Críticas

| Incidente | Causa Raíz | Solución |
|-----------|------------|----------|
| **Error -1021 (Timestamp)** | Desincronización de reloj local vs servidor. | Activado `adjustForTimeDifference: True` y aumentado `recvWindow` a 10s en `exchange.py`. |
| **AttributeError en Balance** | Faltaban wrappers en `ExchangeManager` tras la refactorización. | Restaurados `fetch_balance()` y `fetch_my_trades()` delegando al objeto CCXT. |
| **Duplicación de Unidades** | El sistema sumaba Algo Orders y Standard Orders erróneamente. | Implementado `OrderFactory` como fuente única de verdad para evitar doble conteo. |

---

## 4. Archivo de Investigación (Noise Reduction)

Se han procesado más de 50 scripts de diagnóstico. Los hallazgos clave se han consolidado en este documento. Los scripts originales han sido archivados para mantener la limpieza del entorno de ejecución.

**Ubicación de Referencias Archivadas:** `docs/archive/research/algo-orders/`
