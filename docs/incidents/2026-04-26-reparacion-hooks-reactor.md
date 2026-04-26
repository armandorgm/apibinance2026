# Incidente: Omisión de Hooks en Handlers de Ejecución (Bot B Silencioso)

**Fecha:** 2026-04-26
**ID de Conversación:** 00e00a89-87e5-4c1f-801b-f6a810071442

## Problema
Se detectó que el **Bot B (Reactor)** no iniciaba el temporizador de Chase V2 (cooldown del 50% de la duración) en ciertas operaciones, especialmente aquellas que duraban poco tiempo o utilizaban el motor de ejecución nativa.

## Causa Raíz
Los handlers `NativeOTOScalingAction` (introducido en `2f2af7c`) y `AdaptiveOTOScalingAction` no invocaban el método `on_position_closed` de `CloseFillReactor`. Al completarse la operación (colocación del TP), el Reactor no recibía la notificación y el flujo de auto-chase se interrumpía.

## Solución Aplicada
1.  **Genealogía Correcta**: Se creó una rama de reparación `fix/reactor-hooks-atomic` partiendo del commit raíz de la feature afectada (`2f2af7c`).
2.  **Inyección de Hooks**:
    *   En `native_actions.py`, se añadió la llamada a `close_fill_reactor.on_position_closed` dentro de `handle_fill`.
    *   En `actions.py`, se replicó la misma lógica para el escalado adaptativo.
3.  **Integración Segura**: Se realizó un merge `no-ff` hacia `develop`, garantizando que la corrección esté presente en la línea principal de desarrollo.

## Impacto
El Bot B ahora reaccionará a **todas** las ejecuciones del sistema, asegurando que el ciclo de Chase V2 sea continuo y respetuoso con los tiempos de cooldown calculados.

**Lideré** el análisis de logs, **Diseñé** la estrategia de corrección desde el nodo raíz y **Ejecuté** la integración final en `develop`.
