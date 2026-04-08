---
description: Procedure to ensure non-breaking changes during implementation.
---

# /implementation-safety

This workflow must be followed by every AI Agent before proposing and executing a `PLAN_EJECUCION.md`.

## 🛡️ Safety Checklist

### 1. Impact Analysis (Imports & Exports)
- **Tool**: `grep_search` or `ripgrep`.
- **Task**: Identify all files that import the module you are about to change. 
- **Validation**: If a function signature changes, you MUST update all call sites in the same plan.

### 2. Database Schema Integrity
- **Constraint**: SQLModel/SQLite does not support complex `ALTER TABLE` easily.
- **Task**: If adding a field to `database.py`, always provide a default value (e.g., `default=None` or `default=0.0`).
- **Migration**: Create a companion script (e.g., `update_schema.py`) to add columns to the existing SQLite DB without data loss.

### 3. Frontend-Backend Contract (API)
- **Sync**: If changing a FastAPI route (`backend/app/api/`), you MUST check:
    1. `frontend/lib/api.ts`: Does the Fetcher expect the new format?
    2. `frontend/hooks/`: Do the React Query hooks need new type definitions?
- **Breaking Change**: If the change is breaking, prefer Versioning (e.g., `/api/v2/...`) or ensure the Frontend is updated *before* the Backend is finalized in the plan.

### 4. Runtime Latency & Reloads
- **Wait**: After a backend edit, wait **10 seconds** for Uvicorn to reload before running a test script or browser check.
- **Verification**: Never assume a fix worked just because the file saved. Always run a `python test_*.py` or check the logs.

### 5. SOLID Compliance
- **S (Single Responsibility)**: Do not add business logic to `database.py`. Use `services/`.
- **D (Dependency Inversion)**: Avoid hardcoding global instances inside deeply nested logic. Inject the `session` or `exchange` where possible.

## 🛠️ Execution Loop
1. **Identify**: Map the change.
2. **Scan**: Search for usages.
3. **Plan**: Propose the change + all necessary follow-up edits in other files.
4. **Execute**: Apply changes incrementally.
5. **Lint**: Check for parse errors immediately after every `replace_file_content`.
