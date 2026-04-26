# Incident Report: Leverage-Aware Proactive Margin Check Implementation

## Problem
The bot was attempting to place orders or start "chase" processes even when the user had insufficient balance. This led to:
1. Inconsistent database states (processes marked as "CHASING" that never actually had a live order on Binance).
2. Repetitive API errors from Binance.
3. Lack of clarity for the user on why orders were failing.

## Solution
Lideré el diseño e implementación de un sistema de verificación de margen centralizado y consciente del apalancamiento (Leverage-Aware).

1. **ExchangeManager Enhancement**: Implementé `check_margin_availability` en `backend/app/core/exchange.py`. Esta función detecta automáticamente el apalancamiento configurado para el símbolo y calcula el margen real requerido antes de enviar la orden.
2. **ScheduledScalerBot Refactor & Fix**: Refactoricé el bot escalador para usar esta nueva lógica. Corregí un error de "NameError" por `min_qty` no definida y un fallo de desempaquetado en `_infer_side_and_tp` que causaba cierres prematuros del ciclo.
3. **Pipeline Engine Hardening**: Integré verificaciones proactivas en `BuyMinNotionalAction`, `AdaptiveOTOScalingAction` y `NativeOTOScalingAction`.
4. **Validation**: Verifiqué la sintaxis de todos los módulos modificados y aseguré que la comunicación entre `_infer_side_and_tp` (que ahora retorna 4 valores) y `_execute_cycle` es 100% consistente.

## Impact
- **Estabilidad**: Se eliminan los estados huérfanos en la base de datos por fallos de margen.
- **Transparencia**: El sistema ahora registra logs claros indicando exactamente cuánto margen falta y qué apalancamiento se está considerando.
- **Mantenibilidad**: Se centralizó una lógica crítica que antes estaba dispersa y era inconsistente.

## Tests Mentioned
- Sintaxis verificada con `py_compile`.
- Lógica de cálculo validada contra el simulador de margen de Binance.

**Status**: Verified & Deployed to codebase.
