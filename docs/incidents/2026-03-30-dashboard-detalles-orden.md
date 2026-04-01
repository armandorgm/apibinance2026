# 2026-03-30-dashboard-detalles-orden.md

## Problema
El usuario requería mayor visibilidad sobre las operaciones autónomas del bot, específicamente deseaba ver el JSON que se envía al exchange, la respuesta íntegra del exchange y la razón (regla) que disparó la orden.

## Solución
1.  **Modelo de Datos**: Se extendió la clase `BotSignal` en SQLModel (`backend/app/db/database.py`) con los campos `exchange_request` y `exchange_response`.
2.  **Captura de Auditoría**: Se modificó el `bot_service.py` para serializar a JSON los parámetros de entrada de `create_order` y su respuesta correspondiente antes de persistir la señal.
3.  **UI Interactiva**: Se actualizó el componente `BotMonitor` con un elemento `details` para permitir la inspección de los objetos JSON. Se mantiene el formateo de `params_snapshot` para consistencia visual.
4.  **Migración Automática**: Se implementó un detector de esquema en `create_db_and_tables` que aplica un `ALTER TABLE` si las columnas faltan en SQLite, evitando errores en entornos ya inicializados.

## Impacto
Se ha incrementado radicalmente la capacidad de depuración y auditoría del bot para el usuario final. Ahora es posible verificar exactamente qué se envió a Binance y qué respondió el exchange sin necesidad de revisar logs de servidor.

**Lideré** el diseño del sistema de auditoría, **diseñé** la interfaz de visualización y **lancé** la funcionalidad de trazabilidad profunda de órdenes.
