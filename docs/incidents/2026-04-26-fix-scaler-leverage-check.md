# Incidente: 2026-04-26 - Error de Margen en ScheduledScalerBot (Bot C)

## Problema
El `ScheduledScalerBot` (Bot C) reportaba un error de "Insufficient balance" (Balance insuficiente) al intentar ejecutar un ciclo de escalado, a pesar de que el usuario tenía una posición abierta con apalancamiento (leverage=3). El bot comparaba el balance disponible directamente con el valor nocional total de la orden requerida (Notional * Factor de Seguridad), ignorando que el margen real necesario es mucho menor debido al apalancamiento.

**Ejemplo del Log:**
`[SCALER] Balance Check: available=4.7153 USDC, required=5.5078 USDC`
`WARNING: Insufficient balance: 4.7153 < 5.5078 required.`

## Solución
Implementé el reconocimiento de apalancamiento en el ciclo de ejecución del bot:
1. **Extracción de Leverage**: Modifiqué `_infer_side_and_tp` para capturar el campo `leverage` desde el endpoint `positionRisk` de Binance.
2. **Cálculo de Margen Requerido**: Actualicé `_execute_cycle` para calcular el costo como `(notional / leverage)`.
3. **Mejora de Logs**: Se añadió transparencia al log de "Balance Check", mostrando ahora el margen requerido, el valor nocional total y el apalancamiento aplicado.

**Tests realizados:**
- Validación de sintaxis con `py_compile`.
- Inspección de la respuesta de `binance_native` para asegurar la existencia del campo `leverage`.
- Simulación lógica: Con 4.71 USDC disponibles y 5.50 USDC nocional, a 3x el margen requerido es ~1.84 USDC. El check ahora es `4.71 > 1.84` (PASS).

## Impacto
El Bot C (Scaler) ahora puede operar correctamente en cuentas con balances pequeños que utilizan apalancamiento, evitando skips innecesarios de ciclos de trading. No se detectaron efectos secundarios en otros componentes (impact analysis limitado a `scaler_routes.py` y `main.py`).

---
*Lideré el diseño de la solución, implementé los cambios en el servicio del bot y lancé la actualización al runtime local.*
