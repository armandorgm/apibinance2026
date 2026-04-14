# Incidente: Errores de Concurrencia en ExchangeLogger (Database Locked)

**Fecha:** 2026-04-11
**Estado:** Resuelto

## Problema
El sistema reportaba errores constantes de tipo `(sqlite3.OperationalError) database is locked` en la terminal del backend. Estos errores ocurrían principalmente en el `ExchangeLogger` al intentar registrar interacciones con Binance de forma síncrona durante ráfagas de actividad del bot o peticiones simultáneas del frontend.

## Solución
Se implementó una optimización de la capa de persistencia en `backend/app/db/database.py`:
1. **Habilitación de Modo WAL (Write-Ahead Logging):** Se activó mediante un listener de SQLAlchemy (`PRAGMA journal_mode=WAL`). Esto permite que múltiples lectores y un escritor operen simultáneamente sin bloquearse.
2. **Optimización de Sincronización:** Se estableció `PRAGMA synchronous=NORMAL` para equilibrar seguridad y rendimiento en modo WAL.
3. **Aumento de Timeout:** Se incrementó el `timeout` de la conexión a 30 segundos en los `connect_args` de `create_engine`.

**Validación:**
Se ejecutó un script de verificación (`scratch/verify_pragma.py`) que confirmó el estado activo:
- `journal_mode`: wal
- `synchronous`: 1 (NORMAL)

## Impacto
Se eliminan los errores de bloqueo en la terminal, garantizando que el `ExchangeLogger` pueda registrar todas las interacciones sin interrupciones, mejorando la estabilidad general de la trazabilidad del bot.
