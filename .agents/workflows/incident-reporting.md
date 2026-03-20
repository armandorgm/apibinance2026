---
description: Reglas para la documentación y registro de incidentes.
---
1. No generar archivos de "procedimiento" o "intentos" dispersos en la raíz.
2. Usar la carpeta `.temp/` para borradores internos (está en .gitignore).
3. Al alcanzar la solución final, generar UN SOLO archivo en `docs/incidents/`.
4. Nomenclatura: `YYYY-MM-DD-descripcion-breve.md`.
5. Estructura del archivo: 
   - Problema inicial.
   - Solución técnica aplicada.
   - Impacto.
6. Al finalizar, notificar al usuario que el registro de incidentes ha sido actualizado.
