# ESTÁNDARES DEL PROYECTO

## Formateo de Datos (Frontend)
- **Precios**: Usar `formatPrice` de `@/lib/utils`. No usar `.toFixed(2)` directamente, ya que rompe la visualización de activos con precios bajos.
- **Cantidades**: Usar `formatAmount` para mantener consistencia decimal.
- **Porcentajes**: Usar `formatPercentage`.

## Lógica de Negocio (Backend)
- **Matching**: Se debe seguir el principio de "Buy before Sell" y coincidencia exacta de cantidad (o manejo de remanentes si se decide extender).
- **PnL**: El PnL neto debe incluir todas las comisiones (`entry_fee` y `exit_fee`).

## Documentación
- Cada corrección significativa debe generar un reporte en `docs/incidents/`.
- El `PROJECT_MAP.md` debe actualizarse al introducir nuevos módulos o cambiar flujos de datos.

## Estilo de Código
- Mantener tipado estricto en TypeScript.
- Seguir las reglas de linting de Next.js y PEP8 para el backend.
