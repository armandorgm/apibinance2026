# Incidente: Unificación de Despacho de Eventos en StrategyEngine (Chase V2, Native OTO, Adaptive OTO)

**Fecha**: 2026-04-23
**Problema**: El `StrategyEngine` carecía de un mecanismo robusto para distinguir qué motor de ejecución (Chase V2, Native OTO o Adaptive OTO) debía manejar los eventos de WebSockets para cada proceso activo, lo que generaba ambigüedad en el despacho de ticks y fills.

**Solución**:
1. **Extensión del Modelo**: Se añadió el campo `handler_type` a la tabla `bot_pipeline_processes` para identificar explícitamente el motor responsable.
2. **Refactorización del Despacho**: Se modificó `StrategyEngine.dispatch_event` para utilizar este nuevo campo, eliminando heurísticas basadas en sub-estados.
3. **Migración de Datos**: Se ejecutó un script de migración para actualizar la base de datos existente y retroalimentar los registros previos.
4. **Estandarización de Acciones**: Se actualizaron los servicios `ChaseV2Service` y las clases de acción (`NativeOTOScalingAction`, `AdaptiveOTOScalingAction`) para persistir el `handler_type` correcto al inicio de cada operación.
5. **Documentación**: Se creó el manual operativo `docs/OPERATIONAL_MANUAL.md` detallando las diferencias técnicas y de configuración entre los motores.

**Impacto**:
- Mayor estabilidad en la persecución de órdenes (Chase).
- Eliminación de falsos positivos en el despacho de eventos.
- Trazabilidad total de qué motor está operando cada símbolo en tiempo real.

**Tests**:
- Se verificó la consistencia del esquema de base de datos.
- Se validó el flujo de despacho en el código de `strategy_engine.py`.

---
*Reporte generado por Antigravity AI*
