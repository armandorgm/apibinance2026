# Incidente: Fallos en Chase V2 y AdaptiveOTO por Margen Insuficiente

**Fecha:** 2026-04-26
**ID de Conversación:** 93eac2ca-bbaa-4c96-a62e-b3ab6ff32711

## Problema
Se identificaron casos donde el servicio `ChaseV2` y las acciones del `Pipeline Engine` (como `AdaptiveOTOScalingAction`) intentaban colocar órdenes en Binance sin verificar previamente el balance disponible. Esto resultaba en:
1. Errores `-2019 (Account has insufficient balance)` reportados por la API de Binance.
2. Procesos que quedaban en estado "CHASING" o "WAITING_FILL" en la base de datos a pesar de que la orden nunca se creó exitosamente.
3. Inconsistencia entre el estado del bot y la realidad del exchange.

## Solución
Se implementó un sistema de **Verificación de Margen Proactiva (Leverage Aware)**:

1.  **ExchangeManager (`backend/app/core/exchange.py`)**:
    *   Se añadió el método `check_margin_availability(symbol, notional_usd)`.
    *   Este método consulta el balance disponible (`availableBalance`) del activo correspondiente (USDT/USDC).
    *   Obtiene el apalancamiento actual del símbolo para calcular el margen requerido real.
    *   Aplica un multiplicador de seguridad (1.05x) para cubrir pequeñas variaciones de precio/fees.

2.  **ChaseV2Service (`backend/app/services/chase_v2_service.py`)**:
    *   Se integró la validación al inicio de `init_chase`.
    *   Si no hay margen, el servicio aborta inmediatamente con un error descriptivo antes de suscribirse a streams o crear registros en la DB.

3.  **Pipeline Engine Actions (`backend/app/services/pipeline_engine/actions.py`)**:
    *   Se añadió la misma validación en `BuyMinNotionalAction` y `AdaptiveOTOScalingAction`.
    *   Evita que las reglas automáticas del bot generen procesos "huérfanos" por falta de fondos.

## Impacto
*   **Robustez**: Eliminación de estados inconsistentes en la DB por falta de fondos.
*   **Feedback**: El usuario recibe un mensaje claro de "Insufficient Margin" en lugar de un error genérico de ejecución.
*   **Ahorro de Recursos**: Se evita la apertura innecesaria de conexiones WebSocket y creación de tareas asíncronas para órdenes que fallarán.

## Pruebas Realizadas
*   Se creó un script de verificación (`backend/scratch/test_margin_logic.py`) que valida la lógica de cálculo contra la API real de Binance.
*   Verificado que el sistema detecta correctamente la falta de fondos y calcula el margen necesario basado en el apalancamiento del símbolo.

**Reporte generado por Antigravity IDE.**
