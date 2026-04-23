# PLAN DE EJECUCIÓN - Bot Trade Amount Configuration

## Objetivos
1.  **Monto de Orden (Trade Amount)**: Hacer configurable la cantidad operada por el bot desde la vista `Configuración del Bot` (`/settings`) para mitigar rechazos como `"min notional"` en Binance. Se asume un valor por defecto de 5.01 USD.
2.  **Protección Backend**: Evitar que se configuren valores perjudiciales (<= 0 o min notional invalid) desde el endpoint.

## Hoja de Ruta (Ejecutada por Agentes Backend/Frontend UI)
- [x] **Fase 1: Capa de Datos (Backend)**
    - [x] Agregar el nuevo campo `trade_amount: float = Field(default=5.01)` en `database.py`.
    - [x] Actualizar migración SQL `ALTER TABLE` manual durante `create_db_and_tables`.
- [x] **Fase 2: Conexión Frontend Configuración**
    - [x] Añadir parametrización de `trade_amount: Optional[float] = None` al router `routes.py`, con validación HTTPException status 400.
    - [x] Extender `BotConfig` interface en `frontend/lib/api.ts`.
- [x] **Fase 3: Rendering e inyección de datos (Frontend)**
    - [x] Campo numérico (`<input type="number" step="0.0001" />`) insertado en la UI `frontend/app/settings/page.tsx` con manejo de estados para guardar. Helper text incluido con luz ámbar informando "min notional > 5 USD".
- [x] **Fase 4: Motor Autónomo Trade Logic**
    - [x] Sustituir montos fijos en `bot_service.py` leyendo `config.trade_amount` y pasándolo limpiamente a `_process_result()` a lo largo de su ciclo de vida en `evaluate_and_execute()`.

## Log de Cambios
- **2026-04-01 01:23**: Generación del plan arquitectónico.
- **2026-04-01 01:28**: Usuario aprueba el plan con default=5.01 y activación de la protección de backend.
- **2026-04-01 01:31**: Finalización de inyección de código. `PROJECT_MAP.md` actualizado para reflejar la erradicación del test_amount hardcodeado para delegar total soberanía al usuario.

## ESTADO: FINALIZADO
- Feature lista para ser comiteada. Archivo migrado a `docs/logs/`.
