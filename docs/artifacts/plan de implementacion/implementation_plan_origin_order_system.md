# Plan de Implementación – Origin‑Centric Order System

## Objetivo
Reestructurar el modelo de órdenes para separar **naturaleza técnica** (Standard vs Algo) y **origen** (Bot, Manual, Auto‑Algo) manteniendo los principios SOLID, habilitando badges claros y evitando que una orden Algo sea tratada como entrada.

---

## Cambios Propuestos

### 1️⃣ Dominio de Órdenes (Backend)
- **Crear paquete** `backend/app/domain/orders/` con:
  - `base_order.py` → `BaseOrder` (ABC) y enum `Originator`.
  - `standard_order.py` → `StandardOrder` (hereda de `BaseOrder`).
  - `algo_order.py` → `AlgoOrder` (hereda de `BaseOrder`).
  - `origin_resolver.py` → función que, a partir de la respuesta cruda de Binance y de la tabla `BotSignal`, devuelve el `originator` y el flag `can_be_entry`.
- **Factory** `order_factory.py` que recibe el dict de Binance y devuelve la instancia correcta.

### 2️⃣ Persistencia
- **Nueva tabla** `orders` (SQLModel) con columnas:
  - `id`, `symbol`, `side`, `amount`, `price`, `status`, `datetime`, `originator`, `order_type` (`standard`/`algo`), `can_be_entry`.
- **FK opcional** `order_id` en la tabla `fills` para enlazar cada fill a su orden.
- **Migración**: script `migrate_existing_orders.py` que recorra `fills` y `BotSignal` para poblar la tabla `orders` y establecer `originator`.

### 3️⃣ Capa de Integración (ExchangeManager)
- Modificar `fetch_open_orders` para:
  1. Llamar a ambos endpoints (standard + algo) en paralelo.
  2. Pasar cada registro a `OrderFactory` → instancia `BaseOrder`.
  3. Aplicar `origin_resolver` para rellenar `originator` y `can_be_entry`.
  4. Guardar/actualizar la tabla `orders`.
- Exponer nuevo endpoint **/api/orders/unified** que devuelva la lista de `BaseOrder` serializada.

### 4️⃣ Motor de Matching (TradeTracker)
- Cambiar la firma de los métodos para recibir `BaseOrder`.
- Antes de crear una posición, validar `order.can_be_entry()`; si es `False`, registrar como **trade de salida** y no como apertura.
- Añadir lógica para marcar `is_algo_exit` cuando `order.originator == Originator.AUTO`.

### 5️⃣ Frontend – UI y API
- **Extender** `frontend/lib/api.ts` con nuevos campos en la interfaz `Order`:
  ```ts
  originator: 'BOT' | 'MANUAL' | 'AUTO';
  can_be_entry: boolean;
  is_algo?: boolean;
  ```
- **Actualizar** `useOrders` hook (nuevo hook `useUnifiedOrders`) que consuma `/api/orders/unified`.
- **Modificar** `trade-table.tsx`:
  - Mostrar badge de origen (🤖 BOT, 👤 MANUAL, ⚡ AUTO).
  - Columna “Entrada” solo para órdenes con `can_be_entry === true`.
  - Columna “Salida” puede contener cualquier orden, incluido `AlgoOrder`.
- **Diseño**: usar colores diferenciados (púrpura para AUTO‑Algo, azul para BOT, gris para MANUAL) y tooltip explicativo.

### 6️⃣ Tests
- **Unitarios** para cada subclase (`StandardOrder`, `AlgoOrder`) y para `origin_resolver`.
- **Integración**:
  - Simular respuesta combinada de Binance y validar que el endpoint `/api/orders/unified` devuelve la estructura esperada.
  - Verificar que `TradeTracker` rechaza usar una `AlgoOrder` como entrada.
- **E2E** (cypress) para la tabla de historial: badges correctos, columnas filtradas.

### 7️⃣ Documentación y Registro
- Actualizar `docs/PROJECT_MAP.md` con nuevo nodo **Domain → Orders**.
- Añadir sección en `docs/STANDARDS.md` describiendo la regla *“AlgoOrder never entry”*.
- Generar incidente en `docs/incidents/` al cerrar la tarea.

---

## Preguntas Abiertas (User Review Required)

> [!IMPORTANT]
> 1. **Persistencia de `fills` → `order_id`**: ¿Deseas que cada `fill` tenga una FK obligatoria a `orders` (requiere migración completa) o prefieres mantenerla opcional por ahora?
> 2. **Endpoint nuevo vs reutilizar `/orders/open`**: ¿Prefieres crear `/api/orders/unified` o sobrescribir el existente `/orders/open`?
> 3. **Badge visual**: Confirmar los textos e íconos exactos (🤖 BOT, 👤 MANUAL, ⚡ AUTO) y los colores que deseas.

---

## Verificación
- **Automated Tests**: `pytest` para backend, `npm test` para frontend, y Cypress para UI.
- **Manual**: Abrir el dashboard, cambiar origen de órdenes y validar que los badges aparecen y que las columnas de entrada/salida se comportan según `can_be_entry`.

---

## Cronograma Tentativo
| Etapa | Duración estimada | Responsable |
|-------|-------------------|--------------|
| Creación de dominio y factory | 2 días | Backend Dev |
| Persistencia y migración | 1 día | DB Engineer |
| Modificación de ExchangeManager | 1 día | Backend Dev |
| Refactor de TradeTracker | 1 día | Backend Dev |
| Extensión de API y hooks | 1 día | Frontend Dev |
| UI (badges, columnas) | 1 día | Frontend Dev |
| Tests unitarios/integración | 1 día | QA Engineer |
| Documentación y cierre | 0.5 día | Docs Owner |

Total: **≈ 8.5 días** (una semana laboral con margen).

---

*Una vez aprobado este plan, crearé el archivo `task_algo_origin_system.md` y comenzaré la ejecución.*
