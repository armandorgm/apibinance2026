# Plan de Implementación: Long-Only Exact Match & Unrealized Toggle

## Propósito
Abordar 3 problemas/requerimientos:
1. Asegurar que las ventas sin compra previa no creen operaciones "Cortas" (Short) falsas, sino que solo se permita operativa Long.
2. Cambiar la lógica de emparejamiento para que solo haga match si la cantidad (`amount`) de la compra y la venta es exactamente igual, sin dividir operaciones parcialmente.
3. Mostrar todas las operaciones sin match en una lista, y proveer un botón o selector (`toggle`) al usuario para incluir o excluir su "Unrealized PnL" (ganancia flotante) en el cálculo de las estadísticas de PnL promedio/total.

## Cambios Propuestos

### 1. Backend: Lógica Estricta de Cantidades & Agrupación (tracker_logic.py)
Actualmente el código junta cualquier compra con cualquier venta usando `min(buy, sell)`, particionándolos.
Lo vamos a reemplazar por **Exact Match**:
Para que un `sell` se cierre contra un `buy`, su `amount` debe ser idénticamente igual.
*Nota crucial para revisión:* En Binance, si ingresas una orden de compra por 1.0 BTC al mercado, a veces la API te lo subdivide en múltiples ejecuciones/fills (ej. 0.3 y 0.7). Si luego vendes 1.0 en un solo fill, las cantidades no coincidirán y se tratarán como *Unmatched*. 
**Solución a implementar para esto**: Antes de usar "Exact Match", agruparemos los fills por su campo `order_id` sumando sus cantidades y costos (Agrupando "Fills" en "Órdenes" sólidas). ¿Es correcto?

### 2. Backend: Opcionalización del Unrealized PnL (routes.py)
En este momento, el endpoint `/api/stats` suma todas las ganancias de las operaciones *cerradas*.
Añadiremos un nuevo parámetro de consulta: `?include_unmatched=true|false`.
Si es *true*, el backend tomará todas las posiciones abiertas (Unmatched/Open) que están vivas en el tracker, consultará el precio actual en Binance (o usará un aproximado), y sumará su "Ganancia No Realizada" al PnL Total y PnL Promedio.

### 3. Frontend: Agregando el Toggle y Visualización (page.tsx y use-trades.ts)
Añadiremos un interruptor interactivo (Toggle Switch) en el dashboard: **[x] Incluir operaciones abiertas (Unmatched) en las Estadísticas.**
La tabla de "Historial de Operaciones" seguirá mostrando hasta abajo los trades sin *exit_price*, lo que indica que no han hecho match.

## Verification Plan
1. Agrupar fills por `order_id` manualmente en un entorno de pruebas.
2. Tratar de emparejar dos órdenes; si los montos totales son diferentes (ej. Buy 1.0, Sell 0.5) deben quedar en el limbo como `Unmatched`.
3. Validar con el Toggle si la ganancia total sube/baja de acuerdo a la valoración en tiempo real de los Unmatched trades.
