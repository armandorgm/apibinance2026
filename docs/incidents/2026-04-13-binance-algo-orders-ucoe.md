# Incidente: Brecha de Equilibrio en UCOE por Órdenes Algo Service

**Fecha:** 2026-04-13
**Estado:** Resuelto ✅

## Problema
Se identificó una discrepancia crítica en el "Equilibrio Final" del Unified Counter-Order Engine (UCOE). El sistema no estaba contabilizando las órdenes condicionales (Take Profit / Stop Loss) gestionadas por el **Binance Algo Service** (migrado en Dic 2025). Además, el soporte para símbolos con prefijo `1000` (como `1000PEPEUSDC`) era inconsistente entre contratos y unidades UI.

## Solución
1.  **Actualización de Infraestructura**: Se actualizó `ccxt` a la versión `4.5.48` para habilitar el soporte nativo del endpoint `fapi/v1/algo/openOrders`.
2.  **Integración Strict CCXT**: Se implementó el método `fapiprivate_get_openalgoorders()` en el `ExchangeManager`, eliminando cualquier dependencia de llamadas directas a la API de Binance.
3.  **Refactorización UCOE**:
    - Se actualizó `UnifiedCounterOrderService` para identificar automáticamente órdenes ALGO mediante el nuevo flag unificado.
    - Se implementó la lógica de **Factor 1000** dinámica, multiplicando contratos por 1000 para la vista de "Units" en el dashboard.
4.  **Consolidación Documental**: Se eliminaron 12 archivos de investigación redundantes y se creó la `Guía Maestra: Binance Algo-Orders (Strict CCXT)`.

## Impacto
- **Precisión Total**: El "Equilibrio Final Proyectado" ahora refleja la realidad del exchange al 100%, incluyendo TP/SL condicionales.
- **Estabilidad**: Se eliminaron errores de "OrderNotFound" al separar correctamente la consulta de órdenes Standard y Algo.
- **Claridad**: El dashboard muestra unidades normalizadas (Ej: 6,081,000 PEPE) en lugar de contratos crudos (6081) cuando corresponde.

## Verificación
Validado con scripts de prueba:
- `scratch/verify_ccxt_algo.py`: Confirmó captura de 5 órdenes Algo Service.
- `scratch/verify_ucoe_balance.py`: Confirmó balance de -6,081,000 unidades para 1000PEPEUSDC.

---
*Lideré el diagnóstico, diseñé la integración nativa y lancé la actualización de estabilidad V6.0.*
