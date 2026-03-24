# 2026-03-24 — Fix: Estrategias de Matching FIFO/LIFO no respetaban su contrato

**Fecha:** 2026-03-24  
**Rama:** `feature/modular-matching-logic`

## Problema

Tras el refactor modular (Patrón Strategy), tres bugs hacían que FIFO y LIFO puro se comportaran como Atomic Match:

1. **routes.py `GET /trades/history`** — Condición `if strategy in [...] and logic.lower() != "fifo"` era contradictoria: FIFO siempre caía al `else` y leía la DB pre-guardada con `atomic_fifo`. Nunca ejecutaba `FIFOMatchStrategy` en vivo.
2. **routes.py `POST /sync/historical`** — `process_and_save_trades()` se llamaba sin `strategy_name`, guardando siempre con `atomic_fifo` sin importar la estrategia elegida por el usuario.
3. **tracker_logic.py `compute_open_positions()`** — Recibía el parámetro `logic` pero lo ignoraba: internamente re-implementaba la detección de emparejados con `abs(buy.amount - sell.amount) < 1e-8` (lógica Atomic), produciendo posiciones flotantes incorrectas al usar FIFO/LIFO.

## Solución

**Implementé y Diseñé** las correcciones en dos archivos:

- **`routes.py`**: Simplifiqué la condición a `if strategy != "atomic_fifo"` — todo lo que no sea `atomic_fifo` calcula en vivo. Pasé `strategy_name=logic` al sync histórico.
- **`tracker_logic.py`**: Refactoricé `compute_open_positions()` para delegar en `match_trades(fills, logic)` (la strategy correcta), colectar los timestamps de entry/exit usados, y reportar solo los no emparejados — garantizando consistencia total con el historial.

**Lancé** la suite de tests:
- Creado `backend/tests/test_matching_strategies.py`: 5 clases, 16 casos parametrizados (exact match, partial match, inverted, FIFO vs LIFO order, open positions por estrategia).
- Actualizados `test_lifo.py` (asserts formales) y `test_verification.py` (API corregida de `_match_trades` → `match_trades`).

## Resultado de Tests

```
16 passed ✓  (test_matching_strategies.py)
test_lifo.py → All assertions passed ✓
test_verification.py → VERIFICATION SUCCESSFUL
```

## Impacto

- FIFO puro ahora **empareja por orden temporal con cantidades parciales** — los trades flotantes antiguos son ahora candidatos válidos.
- LIFO puro ídem desde el extremo más reciente.
- Las posiciones flotantes en el dashboard reflejan la misma estrategia que el historial de trades cerrados.
- El sync histórico ahora guarda correctamente según la estrategia elegida.
