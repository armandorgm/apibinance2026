# Incidente: Implementación de Estrategia Reactiva de TP y Robustez de Scaler

**Fecha:** 2026-05-04  
**Estado:** Resuelto  

## Problema
El sistema experimentaba rechazos intermitentes de órdenes Take Profit (TP) con el error `-2022` (ReduceOnly rejected) en Binance Futures. Esto ocurría principalmente durante ciclos de recuperación o cuando la posición se cerraba externamente (o por un TP previo) antes de que el bot intentara colocar un nuevo TP. Las verificaciones proactivas de posición antes de cada orden añadían latencia innecesaria y no eliminaban completamente las condiciones de carrera.

## Solución
Implementé un **Patrón Reactivo "Try-Before-Check"**:
1. **Eliminación de Latencia**: Se removieron los checks proactivos `has_open_position` en `ChaseV2Service` y `NativeOTOScalingAction`. El sistema ahora intenta colocar el TP directamente al detectar un fill.
2. **Manejo Reactivo**: Se añadió un bloque de captura específico para errores `-2022`. Solo si ocurre el error, el sistema consulta la posición. Si se confirma que es `0`, el proceso se marca como `ORPHAN_NO_POSITION` (ABORTED) y se limpian los recursos (suscripciones, streams).
3. **Robustez de Scaler**: Refiné la lógica de inferencia del `ScheduledScalerBot` para que sea capaz de recuperarse de estados de "posición plana" (flat) asumiendo un lado `LONG` por defecto, permitiendo el reinicio autónomo de ciclos tras un descarte de proceso huérfano.
4. **Logs de Alta Fidelidad**: Se enriqueció la trazabilidad para identificar exactamente por qué el bot elige un lado o precio específico durante la recuperación.

## Impacto
- **Latencia**: Reducción significativa del tiempo entre el fill de entrada y la colocación del TP al eliminar una llamada API bloqueante.
- **Estabilidad**: El bot ya no se bloquea ni inunda los logs con errores `-2022` infinitos; ahora los gestiona como estados terminales válidos de limpieza.
- **Autonomía**: El Scaler Bot puede ahora cerrar ciclos fallidos y abrir nuevos sin intervención manual.

## Tests realizados
- Verificación en logs reales: Se capturó un evento de rechazo `-2022` que disparó correctamente la validación reactiva, marcando el proceso como `ORPHAN` y permitiendo al Scaler iniciar un nuevo ciclo exitoso inmediatamente después.

**Implementado por**: Antigravity AI Agent
