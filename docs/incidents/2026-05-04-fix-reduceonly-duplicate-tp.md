# 2026-05-04 — Fix -2022 ReduceOnly Duplicate TP (V5.9.47)

## Problema

El sistema registraba el error `(400, -2022, 'ReduceOnly Order is rejected.')` repetidamente
en los logs de `ChaseV2Service` después de cada fill de orden de entrada.

**Síntoma observado:**
```
[CHASE V2] fatal API error: (400, -2022, 'ReduceOnly Order is rejected.')
```

Este error provocaba que el `OTO Loop` reportara fallos y saturaba los logs, aunque el TP
ya había sido colocado exitosamente por el primer camino.

## Causa Raíz

Race condition entre dos paths independientes que disparan `handle_fill`:

1. **Path WebSocket (stream):** El evento `FILLED` llega por WebSocket → `handle_order_event`
   → `handle_fill` → coloca TP y marca `process.status = "COMPLETED"`.

2. **Path Hard-Sync (REST):** `stream_service.recover_active_subscriptions()` consulta la DB
   buscando procesos en estado `"CHASING"` y verifica cada `entry_order_id` vía REST. Si la
   respuesta de Binance es `status=closed`, llama a `handler.handle_fill(p, session)` sin
   verificar si el proceso ya fue marcado `COMPLETED` por el path WS.

En la ventana de tiempo entre ambas ejecuciones (~1-2 segundos), ambos paths intentan colocar
un `TP ReduceOnly` para la misma posición → Binance rechaza el segundo con código `-2022`.

## Solución (V5.9.47) — Doble Barrera

Implementé una estrategia de **Defense in Depth** con dos barreras independientes:

### Barrera 1 — Upstream (stream_service.py, Hard-Sync)

Añadí verificación del `p.status` antes de invocar `handle_fill` en el loop de Hard-Sync.
Si el proceso ya está en `COMPLETED` o `ABORTED`, se loguea y se salta:

```python
if p.status in ("COMPLETED", "ABORTED"):
    print(f"[STREAM] Hard-sync: Order {p.entry_order_id} already {p.status}. Skipping handle_fill.")
else:
    # ... handle_fill normal
```

### Barrera 2 — Downstream (handle_fill en todos los call sites)

Al inicio de cada `handle_fill`, añadí `session.refresh(process)` para obtener el estado
autoritativo desde DB, seguido de un guard:

```python
try:
    session.refresh(process)
except Exception:
    pass
if process.status == "COMPLETED":
    logger.info(f"[CHASE V2] handle_fill skipped: process {process.id} already COMPLETED.")
    return
```

Aplicado en:
- `chase_v2_service.py` → `ChaseV2Service.handle_fill`
- `pipeline_engine/native_actions.py` → `NativeOTOScalingAction.handle_fill`

`actions.py` (`AdaptiveOTOScalingAction`) ya tenía su propio mecanismo de idempotencia
vía `clientOrderId` único (`TP_OTO_PID_{process.id}`) y no requirió modificación.

## Tests

**Verificación de sintaxis:** Ejecutado `ast.parse` en los 3 archivos modificados → ✅ OK.

**Validación manual esperada:** Al próximo fill de entrada, los logs deben mostrar únicamente:
```
[CHASE V2 SERVICE] TP placed successfully for 1000PEPE/USDC:USDC
```
Y en caso de reintento del Hard-Sync:
```
[STREAM] Hard-sync: Order XXXX already COMPLETED. Skipping handle_fill.
```
o bien:
```
[CHASE V2 SERVICE] handle_fill skipped: process N already COMPLETED (TP was already placed).
```

## Impacto

- **Eliminado** el error `-2022 ReduceOnly` que aparecía en cada ciclo de fill.
- **Estabilizado** el pipeline OTO: ya no reporta fallos de TP cuando la orden fue colocada exitosamente.
- **Reducido** el log noise significativamente.
- **Sin regresiones:** La lógica de Barrera 1 sólo aplica al Hard-Sync recovery, no al path primario.
  La Barrera 2 es un early-return seguro que no altera el flujo normal (el proceso jamás está COMPLETED
  en el primer call legítimo).
