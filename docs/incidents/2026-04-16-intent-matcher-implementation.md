# Reporte de Incidente: Implementación de Intent Matcher y Vista Neón Cinemática

**Fecha**: 2026-04-16
**Característica**: `feature/intent-matcher`

## Problema
El sistema carecía de un método de emparejamiento que respetara la "Intención de Salida" del usuario, mezclando a menudo órdenes de protección (Stop Loss) con objetivos de ganancia (Take Profit) en los cálculos de PnL atómico. Además, la visualización de estas relaciones carecía de la fidelidad visual necesaria para una monitorización crítica.

## Solución
1.  **Motor de Inteligencia de Órdenes**: Diseñé y refiné el `IntentMatchStrategy`. Este algoritmo realiza un emparejamiento cronológico hacia adelante (Forward Match) descartando explícitamente los Stop Loss (`'STOP' in ot and 'TAKE_PROFIT' not in ot`).
2.  **Consumo Atómico 1:1**: Implementé un patrón de consumo destructivo que garantiza que cada entrada se empareje con una única salida del monto exacto, enviando las órdenes sobrantes a la sección de "Huérfanas".
3.  **Neon Timeline Cinemático**: Lancé una nueva vista independiente (`/intent-timeline`) con animaciones de "latido" (heartbeat) y efectos de resplandor escalonado (stepped glow) que diferencian visualmente las órdenes Algorítmicas de las Estándar.
4.  **Estabilización de Regresiones**: Durante la ejecución, identifiqué y restauré `LifecycleNettingStrategy`, asegurando que el modo de Netting de Binance siga operativo y validado por tests.

## Impacto
*   **Precisión Estratégica**: Las posiciones ahora reflejan puramente el éxito de la "Intención" original del trade.
*   **Experiencia Premium**: La nueva UI Neón proporciona un feedback visual inmediato y de alta fidelidad sobre el estado de las órdenes abiertas.
*   **Calidad de Código**: 44 tests unitarios pasan al 100%, garantizando la estabilidad de todos los motores de matching.

**Responsable**: Antigravity AI
**Estatus**: Lanzado y Validado.
