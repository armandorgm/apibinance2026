# Fix NameError en Sincronización Histórica (2026-03-20)

## Problema inicial
Al renombrar la clase principal de `FIFOTracker` a `TradeTracker` para soportar tanto FIFO como LIFO, se omitió actualizar la referencia en el endpoint de sincronización histórica (`/sync/historical`) en el archivo `routes.py`. Esto habría provocado un `NameError` al intentar sincronizar operaciones previas.

## Solución técnica aplicada
1. **Backend (`routes.py`)**:
   - Se actualizó la instanciación en la línea 320 de `tracker = FIFOTracker(symbol)` a `tracker = TradeTracker(symbol)`.

## Impacto
Se previno un error tipo 500 (`NameError`) en el backend cuando los usuarios utilicen la función "Cargar previos (7 días)" desde el frontend, asegurando que la recolección histórica siga funcionando correctamente con la nueva estructura de clases.
