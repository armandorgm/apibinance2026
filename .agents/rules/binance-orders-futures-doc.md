---
trigger: always_on
---

parámetros configurables para una orden de futuros USDⓈ-M de Binance, con ejemplos de código en Python:Acá está la referencia completa de todos los parámetros configurables para una orden de futuros USDⓈ-M de Binance, con código en Python listo para usar:Algunos puntos clave a tener en cuenta:

**Endpoint principal:** `POST /fapi/v1/order` — requiere firma HMAC-SHA256 y API key en el header.

**Combinaciones inválidas a evitar:**
- `reduceOnly` no se puede usar en Hedge Mode ni junto con `closePosition`
- `price` y `priceMatch` son mutuamente excluyentes
- `selfTradePreventionMode` solo tiene efecto cuando `timeInForce` es `IOC`, `GTC` o `GTD`

**Cambio importante en 2025:** A partir del 2025-12-09, las órdenes condicionales (STOP_MARKET, TAKE_PROFIT_MARKET, STOP, TAKE_PROFIT, TRAILING_STOP_MARKET) migran al Algo Service. Las que uses en `/fapi/v1/order` después de esa fecha recibirán el error `-4120 STOP_ORDER_SWITCH_ALGO`. El nuevo endpoint es `/fapi/v1/algo/newOrder`.

**Testnet:** El REST base URL para testnet es `https://demo-fapi.binance.com` — ideal para probar toda la configuración sin riesgo.

¿Querés que profundice en algún tipo de orden específico, el manejo de errores, o la implementación del Algo Service para las órdenes condicionales?