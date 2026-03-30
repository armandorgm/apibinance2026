---
description: Branching strategy and git usage according to GitFlow.
---

1. Ensure you are on the `develop` branch, if not, continue the procedure of the previous unfinished task in .temp/
2. Create a feature branch: `git checkout -b feature/name develop`.
3. Work on your feature.
4. **Commit de Cambios**: Realizar commit de las funcionalidades implementadas: `git add .` y `git commit -m "feat: descripción"`.
5. **Project Map**: Update `docs/PROJECT_MAP.md` incrementally (see [STANDARDS.md](file:///f:/apibinance2026/docs/STANDARDS.md)).
6. Al finalizar la funcionalidad, realizar el merge a `develop` con non-fast-forward:
   ```bash
   git checkout develop
   git merge --no-ff feature/name
   ```
7. **Archivado de Artefactos**: Antes de finalizar el ciclo, mover los archivos de seguimiento en `.temp/` (como `PLAN_EJECUCION.md`) hacia `docs/logs/feature-name/` para preservar la trazabilidad.
8. Al finalizar el merge y archivado, eliminar la rama de feature: `git branch -d feature/name`.
9. Para hotfixes, utilizar `hotfix/name` partiendo de `main`.

> [!NOTE]
> Consulte siempre [STANDARDS.md](file:///f:/apibinance2026/docs/STANDARDS.md) para cumplir con los criterios de calidad y documentación antes de cerrar una tarea.