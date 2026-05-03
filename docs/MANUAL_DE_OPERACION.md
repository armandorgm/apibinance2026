# Manual de Operación: apibinance2026

Este manual detalla el funcionamiento y uso de los componentes avanzados de trading automatizado implementados en el sistema: **Chase V2**, **Native OTO** y el **StrategyEngine**.

---

## 1. StrategyEngine (Motor de Estrategia)

El `StrategyEngine` (técnicamente `PipelineEngine` en el código) es el orquestador central que gestiona el ciclo de vida de las operaciones automatizadas.

### Funciones Principales
- **Evaluación de Reglas**: Monitorea continuamente (Polling) las condiciones definidas en la base de datos para disparar nuevas operaciones.
- **Gestión de Procesos en Tiempo Real**: Maneja los "Ticks" provenientes de WebSockets para las estrategias activas.
- **Sistema de Plugins (Handlers)**: Delega la lógica específica a diferentes manejadores según el tipo (`CHASE_V2`, `NATIVE_OTO`, `ADAPTIVE_OTO`).
- **Polling Fallback**: Cada 15 ticks, verifica el estado de las órdenes vía REST API para asegurar que no se pierdan ejecuciones si el WebSocket falla.

---

## 2. Chase V2 (Persecución Agresiva Maker)

Chase V2 es un servicio diseñado para ejecutar órdenes de entrada como **Maker** (Post-Only), evitando el pago de comisiones de Taker y buscando el mejor precio posible en el libro de órdenes.

### Cómo funciona
1. **Suscripción en Tiempo Real**: Al iniciar, el sistema se suscribe al WebSocket del símbolo.
2. **Colocación Post-Only**: Intenta colocar una orden `LIMIT` con instrucción `GTX` (Post-Only). Si la orden se ejecutaría inmediatamente (Taker), Binance la rechaza y el bot reintenta a un precio un "tick" más alejado.
3. **Persecución (Chasing)**: Si el precio se aleja, el bot modifica la orden existente para mantenerse en la primera posición del libro (Top of Book).
4. **Resiliencia**: Si la conexión se resetea (Error 10054), el sistema reintenta automáticamente hasta 5 veces y recrea la sesión si es necesario.

### Inicialización vía API
**Endpoint:** `POST /api/chase/init`
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "side": "buy",
  "amount": 100.0,
  "profit_pc": 0.01
}
```
*`profit_pc` define el porcentaje de Take Profit que se colocará automáticamente una vez que la entrada sea completada.*

---

## 3. Native OTO (Scaling con Órdenes Nativas)

El sistema **Native OTO** utiliza las capacidades nativas de Binance para gestionar el escalado de posiciones y la toma de beneficios con alta confiabilidad.

### Características
- **Binance Native Connector**: Utiliza el driver oficial para realizar modificaciones de órdenes (`PUT /fapi/v1/order`), lo cual es más rápido y estable que CCXT para estas tareas.
- **Reducción de Riesgo**: Al usar órdenes nativas de Binance, el sistema puede gestionar el Take Profit (TP) directamente en el servidor de Binance, reduciendo la dependencia del bot local una vez colocada la orden.
- **Sincronización de Tiempo**: El motor sincroniza automáticamente el reloj con los servidores de Binance al iniciar para evitar errores de timestamp.

---

## 4. Resolución de Problemas Comunes

### Error [WinError 10054]
Este error indica que el host remoto (Binance) cerró la conexión. 
**Solución Implementada:**
- El sistema ahora detecta este error y realiza hasta 5 reintentos con backoff exponencial.
- En el tercer fallo consecutivo, se cierra y recrea la sesión de red (`UMFutures` o `CCXT`) para limpiar conexiones viciadas.

### Órdenes Rechazadas por Post-Only
Es normal ver logs de "Post-Only rejection". Esto significa que el bot está funcionando correctamente, evitando entrar como Taker. El bot reajustará el precio y volverá a intentar en el siguiente tick.

---

*Documentación generada por Antigravity AI - 2026-04-24*
