# PLAN DE EJECUCIÓN - Corrección Error "Min Notional"

## Objetivos
1.  **Conversión Notional-Contracts**: Modificar `bot_service.py` para que el `trade_amount` sea tratado como Valor Dólar (Notional), en lugar de Cantidad de Contratos.
2.  **Resolución de Límite (Binance)**: Cumplir con la restricción `$5.00` de Binance Futures ajustándose al Market Price en vivo.

## Hoja de Ruta (Ejecutada)
- [x] **Fase 1: Motor Autónomo (Backend)**
    - [x] `bot_service.py`: Recuperar el Market Price real con `fetch_ticker(symbol)` antes de enviar la orden.
    - [x] Calcular la cantidad requerida de contratos = `trade_amount / cur_price`.
    - [x] Formatear el resultado usando CCXT `exchange.amount_to_precision(symbol, quantity)` para evitar el error `code:-4111 Precision Error`.
- [x] **Fase 2: Interfaz de Usuario (Frontend)**
    - [x] Actualizar el Helper Text de `settings/page.tsx` para aclarar "Monto Inversión (USDC)", evitando ambigüedades.

## Log de Cambios
- **2026-04-01 01:53**: Generación del plan arquitectónico para corrección del cálculo Notional.
- **2026-04-01 01:56**: Aprobación del usuario. Inicio de la ejecución técnica.
- **2026-04-01 01:58**: Ejecución de código finalizada. Pipeline Notional-to-Contracts implementado globalmente respetando lote y precio.

## ESTADO: FINALIZADO
- Feature completada y verificada. Archivo migrado a logs.
