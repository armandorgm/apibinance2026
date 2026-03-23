---
description: Branching strategy and git usage according to GitFlow.
---
1. Ensure you are on the `develop` branch.
2. Create a feature branch: `git checkout -b feature/name develop`.
3. Work on your feature.
4. **Project Map**: Update `docs/PROJECT_MAP.md` incrementally (see [STANDARDS.md](file:///f:/apibinance2026/docs/STANDARDS.md)).
5. When finished, merge to `develop` with non-fast-forward:
   ```bash
   git checkout develop
   git merge --no-ff feature/name
   ```
6. Delete the feature branch: `git branch -d feature/name`.
7. For hotfixes, use `hotfix/name` starting from `main`.

> [!NOTE]
> Consulte siempre [STANDARDS.md](file:///f:/apibinance2026/docs/STANDARDS.md) para cumplir con los criterios de calidad y documentación antes de cerrar una tarea.
