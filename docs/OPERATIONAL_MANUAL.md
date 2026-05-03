# Manual Operativo: Chase V2, Native OTO & StrategyEngine

Este manual describe el funcionamiento, configuración y uso de los motores de ejecución avanzada en el ecosistema **apibinance2026**.

---

## 1. StrategyEngine (El Cerebro)

El `StrategyEngine` es el orquestador central que procesa eventos en tiempo real (vía WebSockets) y decide qué acción tomar según el estado de las órdenes y el precio del mercado.

### Responsabilidades:
- **Despacho Unificado**: Utiliza el campo `handler_type` de la base de datos para dirigir los eventos al motor correcto (`CHASE_V2`, `NATIVE_OTO`, o `ADAPTIVE_OTO`).
- **Resiliencia (Polling Fallback)**: Si la conexión de WebSocket falla o se pierde un evento, el motor realiza un "polling" (consulta REST) cada 15 ticks para verificar el estado de la orden en Binance.
- **Gestión de Ticks**: Procesa cada cambio de precio y lo envía al manejador activo para ajustar órdenes (Chase).

---

## 2. Chase V2 (Alta Disponibilidad)

Es la evolución del motor de persecución (Chase), optimizado para ejecutarse de forma autónoma en el backend.

### Funcionamiento:
- **Maker-Only (Post-Only)**: Siempre intenta entrar como "Maker" (comisiones más bajas) usando el parámetro `GTX` de Binance.
- **PUT Optimization**: Utiliza el endpoint nativo `PUT /fapi/v1/order` para modificar órdenes existentes sin cancelarlas, lo que reduce la latencia y mejora la prioridad en el libro de órdenes.
- **Recuperación Automática**: Si la orden es rechazada (por ser Post-Only y cruzar el precio), el motor entra en estado `RECOVERING` y vuelve a intentar la colocación inmediatamente en el siguiente tick.

### Configuración:
- **Cooldown**: 5 segundos (mínimo tiempo entre modificaciones).
- **Threshold**: 0.05% (la orden solo se mueve si el precio varía más de este umbral).
- **Profit PC**: Configurable (por defecto 0.5%).

---

## 3. Native OTO (Official Native)

Motor especializado para usuarios que desean máxima visibilidad y control desde el dashboard, utilizando el driver nativo de Binance.

### Diferencias Clave:
- **Sincronización de Contratos**: Asegura que la cantidad de la orden de salida (Take Profit) coincida exactamente con la cantidad ejecutada en la entrada, evitando "huérfanos".
- **Idempotencia**: Genera IDs de cliente únicos (`newClientOrderId`) para evitar la duplicidad de órdenes en caso de reintentos por red.

---

## 4. Adaptive OTO (Legacy/Flex)

Basado en la librería CCXT, es el motor más flexible pero con mayor latencia que el Native.

### Casos de Uso:
- Operaciones que requieren lógica compleja no soportada por el driver nativo.
- Compatibilidad con múltiples exchanges (aunque el proyecto actual se centra en Binance).

---

## 5. Tabla Comparativa de Motores

| Característica | Chase V2 | Native OTO | Adaptive OTO |
| :--- | :--- | :--- | :--- |
| **Driver** | Binance Native | Binance Native | CCXT (REST/WS) |
| **Modo de Modificación** | `PUT` (Update) | `POST` (Cancel+Replace) | `POST` (Cancel+Replace) |
| **Autonomía** | 100% Backend | 100% Backend | 100% Backend |
| **Post-Only** | Sí (GTX) | Sí (GTX) | Sí (GTX) |
| **Reintentos** | Ilimitados (Cooldown) | Hasta 20 (Init) | Hasta 10 (Init) |

---

## 6. Uso desde el Dashboard

1. **Selección de Motor**: Al lanzar una operación, el sistema asigna el `handler_type` automáticamente basado en la configuración del bot.
2. **Monitoreo en Tiempo Real**:
   - `CHASING`: El bot está ajustando la orden de entrada.
   - `COMPLETED`: La entrada se llenó y el Take Profit ya está colocado en Binance.
   - `ABORTED`: La operación se detuvo manualmente o por error crítico.
3. **Logs de Señales**: Cada ajuste de precio o cambio de estado se registra en la tabla de `Signals` para auditoría técnica.

---
*Documentación generada por Antigravity AI - v5.9.40*
