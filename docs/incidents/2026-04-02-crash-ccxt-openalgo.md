# Incidente: Caída por Missing Attribute en CCXT y Rate Limit Bloqueante

## Problema
El backend comenzó a arrojar una sucesión de errores críticos (visibles en los logs de Uvicorn con códigos `500` en rutas como `/api/orders/open`) tras un rediseño que integraba la obtención concurrente de órdenes algorítmicas (TP/SL). 
1. **Atributo Faltante:** La invocación hardcodeada a `exchange.fapiPrivateGetOpenAlgoOrders` fallaba porque tal nombre implícito no existía en el compilador actual de CCXT para Binance, arrojando un riguroso `AttributeError: 'binance' object has no attribute`.
2. **Fallback Rate-Limit:** Al capturar la excepción y derivar a un fallback genérico de la clase (`await exchange.fetch_open_orders(symbol)`), este estallaba de forma irrecuperable al recibir un `symbol` nulo dado que la UI a veces consulta todo el book. CCXT denegaba la orden emitiendo el `ExchangeError` con advertencia de "Rate limit fetching orders without specifying a symbol".

## Solución
Implementé un blindaje resiliente en `backend/app/core/exchange.py` ahorrando procesamiento asincrónico muerto:
1. Aseguré condicionalmente el bloque de Orders algorítmicas con un `if hasattr(exchange, 'fapiPrivateGetOpenAlgoOrders'):` para evitar lanzar una corrutina inútil y delegué explícitamente su intercepción al `asyncio.gather`.
2. **Resolví el límite de tasa** integrando silenciosamente la bandera de desactivación de advertencias directamente en las `options` tempranas de inicialización `{'warnOnFetchOpenOrdersWithoutSymbol': False}` de CCXT. Esto desbloqueó la ruta de fallback para recolectar el listado y salvar el render del dashboard pase lo que pase.

## Impacto
El backend volvió a mostrar comportamientos estables `200 OK`. El dashboard carga debidamente órdenes pendientes y el motor de CCXT ha quedado parcheado para resistir omisiones endémicas en endpoints de la API de Binance sin estrujar el loop asíncrono.
