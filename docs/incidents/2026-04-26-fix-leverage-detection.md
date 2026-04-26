# Incidente: Fallo en Detección de Apalancamiento (Leverage 1x)

**Fecha:** 2026-04-26
**Estado:** Resuelto
**Severidad:** Media (Causaba falsos positivos de "Saldo insuficiente")

## Problema
Se detectó que el método `check_margin_availability` en `ExchangeManager` fallaba al recuperar el apalancamiento real de un símbolo, resultando en un valor por defecto de `1x`. Esto provocaba que el cálculo del margen requerido fuera excesivamente alto (ej: pidiendo el 100% del nocional como colateral), causando que órdenes válidas fueran rechazadas por el bot con el mensaje "Insufficient balance".

El problema radicaba en que el driver nativo de Binance (`get_position_risk`) a veces retorna una lista vacía para símbolos sin posiciones activas o bajo ciertas condiciones de cuenta, y no había una lógica de reintento o fuente alternativa.

## Solución
1. **Robustez en Driver Nativo:** Se actualizó `BinanceNativeEngine.get_position_risk` para permitir llamadas sin símbolo (retornando el riesgo de toda la cuenta).
2. **Lógica de Fallback Doble:**
   - Si la consulta por símbolo específico falla, se intenta una consulta a nivel de cuenta.
   - Si ambas fallan, se utiliza CCXT (`fetch_positions`) como fuente de respaldo, la cual demostró ser más fiable para obtener el apalancamiento actual de un símbolo incluso sin posición abierta.
3. **Validación:** Se verificó mediante el script `scratch/test_leverage.py` que, ante el fallo del driver nativo, el sistema recupera correctamente el apalancamiento (ej: 37x para PEPE) vía CCXT, ajustando el margen requerido de forma precisa.

## Impacto
Se eliminan los falsos positivos de "Insufficient balance" en el bot, permitiendo que las órdenes se ejecuten con el colateral correcto basado en el apalancamiento configurado en Binance.

## Tests realizados
- Ejecución de `scratch/test_leverage.py` simulando fallo en driver nativo.
- Verificación de logs de `check_margin_availability` confirmando el uso del fallback de CCXT.
