# PLAN DE EJECUCIÓN - Corrección de Sincronización Histórica

## Objetivo
Corregir la lógica de `sync/historical` para que permita retroceder en el tiempo incluso si no se encuentran registros en la ventana de los últimos 7 días (evitar el bucle de búsqueda en el mismo periodo vacío).

## Estado Inicial
- Rama: develop (o rama actual de trabajo)
- Síntoma: Si no hay trades en los últimos 7 días, "Cargar previos" siempre busca en los mismos 7 días desde "ahora".

## Hoja de Ruta

### Fase 1: Investigación y Reproducción
1. [x] Crear un test que simule una base de datos vacía y verifique que `sync/historical` siempre usa `now` como `end_time`.
2. [x] Verificar en la documentación de CCXT/Binance el límite de tiempo para `fetch_my_trades`.
- [x] Analyze current sync and historical sync logic <!-- id: 0 -->
- [x] Reproduce the issue (identify why it fails when no records are found) <!-- id: 1 -->

### Fase 2: Implementación
3. [x] Modificar `backend/app/api/routes.py`:
    - Añadir parámetro opcional `end_time` a `/sync/historical`.
    - O implementar una tabla de estado de sincronización para persistir el "puntero" hacia atrás.
    - Decisión: Probablemente añadir parámetro `end_time` es más flexible para el frontend.
- [x] Fix the logic in `backend/app/api/routes.py` <!-- id: 2 -->
4. [x] Actualizar el mensaje de respuesta para incluir timestamps exactos de la ventana buscada.
5. [x] (Opcional) Actualizar frontend para manejar el retroceso continuo si no se encuentran datos.

### Fase 3: Verificación
6. [x] Ejecutar el test de reproducción y verificar que ahora se puede avanzar hacia atrás.
7. [x] Pruebas manuales con el usuario (vía script de verificación).

### Fase 4: Cierre
8. [x] Registrar el incidente en `docs/incidents/`.
9. [ ] Consultar sobre eliminación de temporales.
