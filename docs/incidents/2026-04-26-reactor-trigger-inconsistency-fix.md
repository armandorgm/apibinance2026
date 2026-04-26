# Incident Report: 2026-04-26 - Inconsistencia en Trigger del Reactor (Bot B) con Bot C (Adaptive OTO)

## Problema
Se identificó una inconsistencia en la propagación de eventos de ciclo de vida (entry/exit fills) entre los diferentes motores de ejecución. Mientras que el **Bot A (Chase V2/Native OTO)** notificaba correctamente al **Reactor (Bot B)** al completarse una operación, el **Bot C (Adaptive OTO)** carecía de estos hooks. Esto impedía que el Reactor detectara los cierres de posición de las operaciones escaladas y lanzara los Chases de seguimiento automáticos.

Adicionalmente, el usuario solicitó una mayor visibilidad de los eventos recibidos vía WebSocket para facilitar el debugging del flujo de órdenes.

## Solución
1.  **Refactorización de `AdaptiveOTOScalingAction`**:
    -   Se implementaron los métodos `handle_entry_fill` y `handle_exit_fill` para centralizar la lógica de finalización de cada etapa.
    -   Se integraron los hooks asíncronos `close_fill_reactor.on_entry_fill()` y `close_fill_reactor.on_exit_fill()`.
    -   Se corrigió un comportamiento en `handle_order_event` que no distinguía correctamente entre el llenado de la entrada y la salida (TP), asegurando que el proceso no se marque como `COMPLETED` hasta que el TP sea ejecutado.
2.  **Mejora de Observabilidad en `StrategyEngine`**:
    -   Se añadió logging detallado (nivel `INFO`) en `evaluate_stream_order` para trazar la llegada de eventos de WebSocket, el matching con procesos activos y el despacho hacia los handlers correspondientes.
3.  **Sincronización de Timestamps**:
    -   Se aseguró que `entry_fill_at` y `exit_fill_at` se actualicen correctamente para que el Reactor pueda calcular el cooldown dinámico (50% de la duración del ciclo).

## Impacto
-   **Funcionalidad**: El Reactor (Bot B) ahora funciona de manera consistente tanto con el Bot A como con el Bot C.
-   **Estabilidad**: Se previene el cierre prematuro de procesos de escalado.
-   **Mantenibilidad**: Mejor trazabilidad de eventos de mercado en los logs del sistema.

## Pruebas Realizadas
-   Verificación estática de la inyección de dependencias (DIP) para evitar ciclos entre `AdaptiveOTOScalingAction` y `CloseFillReactor`.
-   Inspección de la lógica de matching de órdenes en `StrategyEngine`.
-   Validación de la persistencia de estados en `BotPipelineProcess`.

---
*Lideré el diagnóstico y la implementación de la unificación del ciclo de vida del pipeline para el ecosistema multilineal.*
