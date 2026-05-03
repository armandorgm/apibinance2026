---
description: Branching strategy and git usage according to GitFlow with Knowledge Extraction.
---

1. **Estado Inicial**: Asegurarse de estar en la rama `develop`. Si hay una tarea pendiente en `.temp/`, completarla o postergarla según los estándares.
2. **Rama de Feature**: Crear rama: `git checkout -b feature/nombre-descriptivo develop`.
3. **Desarrollo**: Implementar la funcionalidad o corrección.
4. **Validación y Feedback (CRÍTICO)**: Antes de commitear o cerrar, el agente DEBE solicitar aprobación explícita del usuario:
   - Pregunta: *"¿La implementación fue un éxito o se encontraron bloqueos/errores?"*
   - Acción: Documentar el resultado (éxitos, fallos y soluciones aplicadas) en **su sección** de el `PLAN_EJECUCION.md`.
5. **Commit de Cambios**: Realizar commit bajo la identidad del usuario: `git add .` y `git commit -m "feat: descripción (via AI Agent)"`.
6. **Project Map**: Actualizar `docs/PROJECT_MAP.md` incrementalmente (ver [STANDARDS.md](file:///f:/apibinance2026/docs/STANDARDS.md)).
7. **Extracción de Conocimiento (Knowledge Feed)**: Antes de limpiar, procesar el "junk" generado (scripts de scratch, investigaciones temporales, logs):
   - **Documentar**: Volcar la esencia técnica en un reporte formal en `docs/research/` o `docs/knowledge/`.
   - **Archivar**: Mover archivos con valor de trazabilidad a `docs/archive/`.
   - **Eliminar**: Borrar archivos redundantes o sin valor futuro.
8. **Merge Estratégico**: Realizar el merge a `develop` con non-fast-forward:
   ```bash
   git checkout develop
   git merge --no-ff feature/nombre-descriptivo -m "merge: descripción [AI-Assisted]"
   ```
9. **Archivado de Logs**: Mover el contenido de **su sección** de `.temp/PLAN_EJECUCION.md` (incluyendo el reporte de validación) a `docs/logs/nombre-feature/`.
10. **Limpieza Final**: 
    - Eliminar la rama de feature: `git branch -d feature/nombre-descriptivo`.
    - Borrar **únicamente su sección** de `.temp/PLAN_EJECUCION.md`. No borrar el archivo si existen otros planes pendientes.
11. **Hotfixes**: Utilizar `hotfix/nombre` partiendo de `main`.

> [!IMPORTANT]
> Ninguna tarea se considera finalizada sin el volcado de conocimiento y la validación del usuario sobre el éxito/fracaso de la implementación.