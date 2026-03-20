---
description: Branching strategy and git usage according to GitFlow.
---
1. Ensure you are on the `develop` branch.
2. Create a feature branch: `git checkout -b feature/name develop`.
3. Work on your feature.
4. When finished, merge to `develop` with non-fast-forward:
   ```bash
   git checkout develop
   git merge --no-ff feature/name
   ```
5. Delete the feature branch: `git branch -d feature/name`.
6. For hotfixes, use `hotfix/name` starting from `main`.
