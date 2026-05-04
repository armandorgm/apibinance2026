# Incident Report: 2026-05-04 — Reactor Auto-Shutdown (V5.9.46)

## Problema

El `CloseFillReactor` (Bot B) se apagaba sin intervención del usuario. Al investigar, se identificaron **tres vectores de apagado involuntario**:

**VECTOR 1 (Crítico):** `reactor_routes.py` llamaba a `close_fill_reactor.disable()` cuando `init_chase()` retornaba `success=False` por razones **transitorias de mercado** (precio no disponible, 20 intentos -5022 agotados). El reactor quedaba desactivado aunque el usuario no lo hubiera solicitado.

**VECTOR 2:** En `_delayed_chase`, si `init_chase` fallaba en un follow-up, el ciclo terminaba con `logger.error()` y no reintentaba. El reactor permanecía en `is_enabled=True` pero sin ningún task activo — efectivamente muerto hasta el próximo evento de fill.

**VECTOR 3:** El reactor no tenía persistencia en DB. Cualquier restart del backend (uvicorn, crash) borraba el estado en memoria, requiriendo re-activación manual.

## Solución (V5.9.46)

### Fix 1 — Eliminar rollback automático (`reactor_routes.py`)
Diseñé la lógica para que el reactor NO se deshabilite cuando Bot A falla al arrancar. El endpoint retorna `success: True` con un warning descriptivo. Solo el usuario puede deshabilitar el reactor.

### Fix 2 — Retry automático en `_delayed_chase` (`close_fill_reactor.py`)
Implementé un retry único tras 30 segundos si `init_chase` falla en un follow-up. Si el retry también falla, el reactor permanece `enabled` esperando el próximo evento de fill en lugar de morir silenciosamente.

### Fix 3 — Persistencia con `ReactorConfig` (`database.py`, `close_fill_reactor.py`, `main.py`)
- Diseñé el modelo `ReactorConfig` (SQLModel) con patrón singleton (id=1, upsert).
- Implementé `_save_to_db()` llamado automáticamente en `enable()` y `disable()`.
- Implementé `load_from_db()` invocado en `startup_event` de FastAPI.
- El reactor ahora sobrevive reinicios de backend completamente.

### Archivos modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/api/reactor_routes.py` | Eliminado rollback automático |
| `backend/app/services/close_fill_reactor.py` | Retry en `_delayed_chase` + `_save_to_db` / `load_from_db` |
| `backend/app/db/database.py` | Nuevo modelo `ReactorConfig` |
| `backend/app/main.py` | Wired `load_from_db()` en startup event |

## Impacto

- El reactor ya no se apaga solo por fallos transitorios de mercado.
- Los ciclos fallidos ahora tienen un segundo intento automático a los 30s.
- El estado del reactor sobrevive cualquier reinicio del backend sin intervención manual.
- Verificación de sintaxis exitosa en todos los archivos modificados.
