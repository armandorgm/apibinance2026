# Reporte de Incidente: Corrección de Truncamiento de IDs y Doble Prefijo (CC...)

**Fecha:** 2026-04-09  
**Estado:** Resuelto  

## Problema
Se identificaron tres problemas críticos en la visualización de órdenes de Binance:
1. **Truncamiento Visual:** El dashboard (específicamente "Órdenes Abiertas") truncaba los IDs largos mediante CSS, impidiendo la trazabilidad completa.
2. **Doble Prefijo:** Algunos IDs aparecían con doble letra (ej. `CC7378054921`) debido a una redundancia en la lógica de hidratación entre los modelos de dominio y las rutas de la API.
3. **Colisión de IDs #0:** Las posiciones abiertas y órdenes pendientes compartían el ID genérico `#0`, lo que causaba errores de renderizado en React y dificultaba la identificación individual.

## Solución
- **Frontend:** Implementé la eliminación de las clases de truncamiento en `open-trades-table.tsx` y actualicé las `keys` de React para usar el `entry_order_id` completo.
- **Deduplicación de IDs:** Rediseñé la propiedad `id` en `BaseOrder.py` y el ayudante `live_prefix_id` en `routes.py` para que sean idempotentes, evitando la duplicación de prefijos (B/C).
- **Hidratación de IDs Únicos:** Lancé una actualización en las rutas de la API que asigna IDs sintéticos únicos (negativos) a las trades unrealized/pending basándose en el hash de sus datos de origen, garantizando que cada fila sea única.

## Impacto
- **Trazabilidad Total:** Ahora es posible copiar y pegar el ID completo directamente desde el dashboard a Binance para auditoría.
- **Estabilidad de UI:** Se eliminaron los problemas de renderizado causados por claves duplicadas.
- **Consistencia Visual:** Los IDs ahora siguen el estándar del glosario (`B` para básico, `C` para condicional) sin duplicaciones estéticas.

---
*Lideré la investigación, Diseñé la solución idempotente e Implementé los cambios en frontend y backend.*
