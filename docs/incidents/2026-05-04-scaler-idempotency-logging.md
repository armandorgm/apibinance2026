# INCIDENTE: Trazabilidad Ambigua en Idempotencia de ScalerBot

**Fecha:** 2026-05-04
**ID Conversación:** 7b9831be-9df5-492b-a357-689774bf91d9

## Problema
El `ScheduledScalerBot` (Bot C) reportaba saltos de ciclo (skipping) con el mensaje genérico `Active scaler Chase detected` sin proporcionar detalles sobre qué proceso específico (`BotPipelineProcess`) estaba bloqueando la ejecución. Esto dificultaba la validación por parte del usuario de si el salto era legítimo o causado por un proceso "fantasma" o de otro origen (Manual/Reactor).

## Solución
- **Refactorización de Detección:** Se rediseñó el método de validación de idempotencia para recuperar el objeto de proceso completo en lugar de un simple booleano.
- **Transparencia en Logs:** Se actualizaron los logs y las señales del bot (`BotSignal`) para incluir el `ID` del proceso bloqueante y su `originator`.
- **Precisión Lingüística:** Se corrigió el mensaje para que sea descriptivo del origen real del bloqueo (ya sea un Chase lanzado por el propio Scaler, por el Reactor o Manualmente).

## Impacto
Se Lideró la mejora en la observabilidad del sistema de escalado. Ahora, ante un ciclo saltado, el administrador puede verificar instantáneamente el ID del proceso responsable, facilitando la auditoría y limpieza de estados incoherentes en la base de datos sin necesidad de inspección manual profunda.

## Rama recomendada
`feature/scaler-idempotency-logs`

## Tests realizados
- Validación de sintaxis y tipado (SQLModel).
- Verificación de la inyección de metadatos en `BotSignal`.
