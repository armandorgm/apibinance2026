# Implementación del Motor de Tareas (Task Scheduler & Pipeline Engine)

## Cambios Realizados

Siguiendo el diseño propuesto y el feedback recibido, se ha implementado la arquitectura del motor de automatización *en limpio*, aprovechando el recreamiento de la base de datos para omitir scripts de migración redundantes y enfocar el esfuerzo en la arquitectura SOLID.

### 1. Base de Datos & Persistencia (Fase 1)
- Se inyectó la tabla polimórfica `BotPipeline` al hub SQlite que empaqueta las configuraciones funcionales completas directamente en un campo JSON dinámico (`pipeline_config`), cumpliendo el principio Open/Closed para parámetros iterativos.

### 2. Evaluador de Nodos y Acciones (Fase 2)
Se ha reemplazado exitosamente el rígido motor funcional por el **PipelineEngine** modular que consta de tres piezas inyectables:
- **`BaseDataProvider`**: Abstracciones tipadas que devuelven data (e.g. `CurrentPriceProvider`, `LastEntryPriceProvider`). Aquí se enchufarán los futuros RSI, SMA.
- **`BaseEvaluator`**: Módulo matemático y lógico. El actual `RelationalEvaluator` arma un árbol condicional cruzando dos data providers + un offset para devolver triggers estables.
- **`BaseAction`**: Envoltorio final polimórfico (e.g., `BuyMinNotionalAction`).

### 3. API REST y Frontend (Fase 3 y 4)
- Añadidas las rutas CRUD de Tareas Programmadas para Binance (`/api/bot/pipelines`).
- Añadida ruta de metadatos `metadata` (exponiendo al frontend automáticamente qué variables puede cruzar el usuario tras una actualización).
- Creada página local de Frontend en **[`/pipelines`](http://localhost:3000/pipelines)** interconectada mediante el componente `PipelineBuilder`, utilizando dependencias nativas del stack sin dependencias oscuras. Todo reactivo y polivalente.

---
> [!NOTE] 
> La arquitectura ya procesa el loop del backend consumiendo el nuevo Engine y publicando las señales como lo hacía originalmente pero con la nueva flexibilidad atómica. Se han dejado las bases preparadas para incorporar el evento de `ON_TICK` en el futuro.
