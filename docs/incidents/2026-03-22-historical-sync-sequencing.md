# INCIDENTE: Fallo en Sincronización Histórica (Bucle de 7 Días)

**Fecha**: 2026-03-22
**Estado**: Resuelto
**Autor**: Antigravity

## Problema
El sistema de sincronización histórica (`/sync/historical`) se quedaba bloqueado consultando siempre la misma ventana de tiempo (los últimos 7 días desde "ahora") cuando la base de datos estaba vacía para un símbolo específico y no se encontraban trades en ese periodo. Esto impedía al usuario retroceder más allá de la primera semana si no había actividad reciente.

## Solución
1. **Backend**: Se añadió el parámetro opcional `end_time` al endpoint `/api/sync/historical`. 
   - Si se proporciona, la búsqueda retrocede 7 días desde ese timestamp específico.
   - El endpoint ahora devuelve `start_time` y `end_time` en la respuesta.
2. **Frontend**: Se implementó una lógica de estado (`lastHistoricalEndTime`) en el dashboard.
   - Al recibir una respuesta de sincronización histórica, el frontend guarda el `start_time` y lo usa como `end_time` para la siguiente petición.
   - El botón cambia su texto a "Continuar previos" para indicar que se está retrocediendo secuencialmente.
3. **Persistencia**: Se actualizó `PROJECT_MAP.md` para reflejar estas nuevas responsabilidades.

## Impacto
Los usuarios ahora pueden "backfillear" todo su historial de Binance Futures de forma secuencial, incluso si tienen huecos de inactividad prolongados, simplemente haciendo clic repetido en el botón de carga histórica.

## Verificación
Se ejecutó un script de prueba (`verify_sync.py`) que confirmó:
- La carga por defecto usa los últimos 7 días.
- La carga con `end_time` respecta el timestamp proporcionado y retrocede otros 7 días.
