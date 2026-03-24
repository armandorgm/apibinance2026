# Incidente: Refactor Modular de Lógica de Matching (SOLID)

**Fecha:** 2026-03-23
**Descripción:** Refactorización de la lógica de emparejamiento de trades para cumplir con los principios SOLID y soportar múltiples metodologías de cálculo de PnL.

## Problema
La lógica inicial de emparejamiento estaba acoplada a un único método híbrido que priorizaba la coincidencia exacta de cantidades (Quantity Match), lo que dificultaba la extensión hacia otros métodos estándares como FIFO o LIFO puros sin duplicar código o introducir condicionales complejos.

## Solución
- **Diseñado e Implementado** el Patrón Strategy en `tracker_logic.py`.
- **Implementadas 3 Estrategias:**
    - `FIFOMatchStrategy`: FIFO puro con soporte para cierres parciales.
    - `LIFOMatchStrategy`: LIFO puro con soporte para cierres parciales.
    - `AtomicMatchStrategy`: Lógica de coincidencia exacta 1:1, optimizada para el flujo de Binance Buy + Take Profit.
- **Refactorizado** `TradeTracker` para delegar la lógica de matching a la estrategia seleccionada.
- **Actualizada la Interfaz (Frontend):**
    - Añadido selector de metodología con opciones: Atomic (FIFO/LIFO) y FIFO/LIFO Puro.
    - Sincronización integrada para enviar el parámetro `logic` seleccionado por el usuario.
- **Actualizados** los endpoints de la API en `routes.py` para aceptar el parámetro `logic` en las operaciones de sincronización y reporte.

## Impacto
- El sistema es ahora **modular y extensible** según los principios SOLID.
- Se ha clarificado la metodología de emparejamiento personalizada bajo el nombre **ATOMIC_MATCH**.
- Mayor precisión en el cálculo de PnL para diferentes perfiles de trading (scalping vs holding).

## Verificación
- Se ejecutó `test_modular_matching.py` validando que cada estrategia produce los resultados esperados con datos de prueba de Binance.
- Verificación de tipos y consistencia de datos en el formateo de trades.
