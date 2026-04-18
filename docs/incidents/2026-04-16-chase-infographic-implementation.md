# Incidente: Implementación de Infograma Dinámico para Chase Entry
Fecha: 2026-04-16

## Problema
El usuario reportó falta de visibilidad en el estado del proceso "Chase Entry" (AdaptiveOTOScaling). Los registros desaparecían inmediatamente después de ser llenados, lo que impedía confirmar el éxito del Take Profit (OTO) visualmente. Además, los rechazos de 'Post-Only' de Binance ocurrían discretamente, dejando al usuario confundido sobre por qué la orden no avanzaba.

## Solución
- **Diseñé** e **implementé** un sistema de sub-estados granulares en el backend (`WAITING_FILL`, `CHASING`, `RECOVERING`, `DONE`).
- **Extendí** el modelo `BotPipelineProcess` para persistir el estado finalizado durante 60 segundos (TTL).
- **Lancé** el componente `ChaseInfographic.tsx` que muestra una línea de tiempo dinámica y métricas de distancia de precio en tiempo real.
- **Implementé** una lógica de limpieza automática de base de datos para procesos expirados.

## Impacto
Mejora crítica en la observabilidad del bot de trading. Los usuarios ahora tienen una trazabilidad visual de cada decisión del motor Chase, incluyendo la brecha de precio exacta y el progreso paso a paso hasta la colocación del TP. Se redujo la incertidumbre en fallos de 'Post-Only' mediante indicadores de reintento explícitos.

## Tests realizados
- Migración de DB SQLite validada.
- Verificación de tipos en React.
- Validación de persistencia temporal en API routes.
