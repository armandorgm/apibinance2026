# Incidente: Refactorización de Números Mágicos (Encapsulación de Constantes)
Fecha: 2026-05-04
Estado: Resuelto
Rama recomendada: refactor/constants-encapsulation

## Problema
Los servicios `CloseFillReactor`, `ChaseV2Service` y `ScheduledScalerBot` contenían múltiples valores literales (números mágicos) dispersos en la lógica de negocio. Esto dificultaba el mantenimiento, la auditoría de parámetros críticos (como umbrales de riesgo y tiempos de reintento) y aumentaba el riesgo de inconsistencias al modificar parámetros compartidos.

## Solución
Se lideró y ejecutó una refactorización integral siguiendo los principios de encapsulación y código limpio:
1. **Identificación**: Se auditaron los tres servicios para extraer porcentajes de riesgo, multiplicadores de tiempo, IDs de persistencia y umbrales de apalancamiento.
2. **Encapsulación**: Se movieron todos los valores a constantes de clase documentadas en la cabecera de cada servicio.
3. **Estandarización**: Se implementaron constantes de utilidad como `PERCENT_MULTIPLIER` (100.0) y `SECONDS_PER_HOUR` (3600) para unificar las conversiones matemáticas.
4. **Validación**: Se realizó una comprobación de sintaxis (`py_compile`) y un "dry run" mental de la lógica impactada.

### Cambios Clave:
- **CloseFillReactor**: Centralización de `COOLDOWN_MULTIPLIER`, `RETRY_DELAY_SECONDS` y `CONFIG_DB_ID`.
- **ChaseV2Service**: Extracción de `BACKOFF` parameters, `TIMESTAMP_MS_MULTIPLIER` y `CLIENT_ORDER_ID_PREFIX`.
- **ScheduledScalerBot**: Unificación de `PROFIT_FLOOR`, `BALANCE_SAFETY_MULTIPLIER` y lógica de inferencia de apalancamiento.

## Impacto
- **Mantenibilidad**: Los ajustes de parámetros de trading ahora se realizan en un solo lugar por servicio.
- **Legibilidad**: El código es auto-documentado, eliminando la ambigüedad de valores como `0.5` o `30.0`.
- **Estabilidad**: Se redujo el riesgo de errores tipográficos en IDs de base de datos y multiplicadores.

## Tests realizados
- Validación de sintaxis Python 3.11 en todos los archivos modificados.
- Verificación de consistencia de nombres entre definición y uso.
