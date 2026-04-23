# Incidente: Robustez del Motor Chase y Algoritmo Front-Running Maker

**Fecha:** 2026-04-23
**Estado:** Resuelto
**Rama:** `fix/chase-engine-robustness`

## Problema
1. **Rechazos Post-Only (-5022):** El bot quedaba bloqueado cuando Binance rechazaba una orden por violar la condición Post-Only (el precio ya había sido cruzado por el mercado).
2. **Eficiencia de Entrada:** La lógica de "chase" anterior era reactiva y a menudo entraba como Taker o fallaba en posicionarse competitivamente en el libro.
3. **Errores de Importación:** Se detectó un error circular en `strategy_engine.py` que impedía el arranque del flujo de evaluación de ticks.

## Solución
1. **Algoritmo Front-Running Maker:**
   - Diseñé e implementé una lógica dinámica en `native_actions.py`.
   - **Longs:** `Bid + 1 tick` (siempre que `Bid + 1 < Ask`).
   - **Shorts:** `Ask - 1 tick` (siempre que `Ask - 1 > Bid`).
   - Fallback automático al mejor Bid/Ask si el spread es de solo 1 tick para maximizar probabilidad de ser Maker sin violar Post-Only.
2. **Manejo de Error -5022:**
   - Implementé un bloque `try-except` específico para capturar el error de Binance.
   - Lancé un estado de `RECOVERING` que limpia el ID de la orden fallida, permitiendo al motor re-intentar la entrada en el siguiente tick con el precio actualizado.
3. **Estabilización de Infraestructura:**
   - Lideré la corrección de imports en `strategy_engine.py` delegando la carga de acciones al `registry.py`.
   - Añadí `get_tick_size` en `exchange.py` para asegurar que el desplazamiento de precio sea el mínimo permitido por el símbolo.

## Impacto
- **Mayor Fill Rate como Maker:** Reducción drástica del pago de comisiones Taker.
- **Resiliencia:** El bot ya no se detiene ante errores de red o rechazos de Post-Only; ahora se auto-recupera en milisegundos.
- **Escalabilidad:** La lógica es ahora compatible con cualquier símbolo de Binance gracias al uso de `tick_size` dinámico.

## Tests Realizados
- Validación manual en el Debugger de Chase V2.
- Verificación de logs en tiempo real confirmando el cálculo de `Bid + 1 tick`.
- Simulación de error -5022 forzado, verificando la purga del estado y re-entrada exitosa.
