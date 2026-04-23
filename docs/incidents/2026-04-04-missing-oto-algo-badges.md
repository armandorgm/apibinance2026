# Reporte de Incidente: Omisión de Propiedades de Vinculación OTO (Algo/TP)

- **Fecha**: 2026-04-04
- **Componentes Afectados**: `backend/app/domain/orders/order_factory.py`, `backend/app/api/routes.py`, `backend/app/domain/orders/base_order.py`

## Problema
El panel histórico no mostraba los "badges" (`Take Profit`, `Algo`, `Auto`) para órdenes condicionales abiertas. La interfaz visualizaba un placeholder carente de tipo para todas las órdenes pendientes procedentes de la SAPI Algorítmica de Binance. Se originaron discrepancias en la lectura de la API FAPI para símbolos como `1000PEPEUSDC` donde 8 órdenes pendientes (TP) se encontraban "huérfanas" dentro de los cruces del backend respecto de las operaciones activas. Al investigar y simular las peticiones con CCXT, se descubrió que el reciente refactor "Origin-Centric" mediante su factoría `OrderFactory` había eliminado inadvertidamente la extracción de los identificadores temporales críticos (`createTime`, mapeado a `create_time_ms`) y el derivado del tipo en Binance (`conditional_kind`).

## Solución
1. *Diseñé* una extensión para la clase de configuración `BaseOrder` para soportar explícitamente los campos metadata binance: `order_type`, `create_time_ms`, y `conditional_kind`.
2. *Implementé* extracción segura en el `OrderFactory` en el mapeo `AlgoOrder` que toma el valor exacto de `createTime` transformándolo en el `int` idóneo y descifra el subtipo OTO llamando al helper estático local.
3. *Restauré* la propagación de estos meta-datos esenciales hacia `OrderResponse` del endpoint para que FastAPI exponga estos datos explícitos a la UI del dashboard, permitiendo la re-integración del motor algorítmico contenido en `conditional_exit_link.py`.
4. Los tests se validaron al 100%.

## Impacto
El proyecto recobra la usabilidad de su panel del bot permitiendo enlazar de nuevo las órdenes condicionadas con `createTime` a los registros de trades activos mediante la variable reactivada en `get_trade_history()`.
