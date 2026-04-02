# Implementación de Monitor de Estrategia Funcional

Este plan detalla la creación de una nueva sección en el dashboard para visualizar en tiempo real (o basado en datos actuales) el estado del Motor de Reglas (`RuleEngine`) y las recomendaciones de trading resultantes.

## User Review Required

> [!IMPORTANT]
> El motor de reglas actualmente es puramente lógico y no persiste "actividades" pasadas. La sección mostrará el **estado actual** de evaluación basado en los datos cargados en el cliente.
> ¿Deseas que también implementemos un log histórico persistente en la base de datos para estas evaluaciones posteriormente?

## Cambios Propuestos

### Componentes de Interfaz

#### [NEW] [strategy-status.tsx](file:///f:/apibinance2026/frontend/components/strategy-status.tsx)
Creación de un componente premium que:
- Muestre el contexto actual (Edad de compra, Trades activos, Rango).
- Renderice una lista de las reglas definidas en `tradingStrategy.ts`.
- Muestre visualmente (Icons/Colors) cuál regla está disparando un trigger.
- Proponga la acción recomendada (`NEW_ORDER`, `UPDATE_RANGE`).

#### [MODIFY] [page.tsx](file:///f:/apibinance2026/frontend/app/page.tsx)
- Integración del `StrategyStatus` bajo las tarjetas de estadísticas.
- Lógica para extraer el `TradingContext` a partir de los `trades` obtenidos de la API.

### Lógica de Negocio (Frontend)

- Implementar un helper `getTradingContext(trades: Trade[]): TradingContext` que calcule:
    - `last_purchase_time`: Timestamp del trade más reciente.
    - `active_trades_count`: Cantidad de posiciones abiertas.
    - `last_range`: Valor por defecto o derivado (si es posible).

## Plan de Verificación

### Pruebas Manuales
1.  Verificar que el Monitor cambie de estado al alternar entre símbolos con diferentes historiales.
2.  Validar que el trigger de "24h" se active correctamente si el último trade es antiguo.
3.  Simular "Active Trades" para ver el escalado de rangos (Reglas 2 y 3).

### Diseño Estético
- Uso de **vibrantes gradientes** y **efectos hover**.
- Micro-animaciones en los indicadores de Trigger.
- Colores para estados: Indigo/Amber/Emerald.
