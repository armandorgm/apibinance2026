# 2026-04-04 — Migration to Universal AGENTS.md Standard

## Problem

The project's AI agent configuration was fragmented across 5 separate files in 3 different proprietary formats:
- `.cursorrules` — Cursor-only dev profile and code style
- `.gemini/gemini.md` — Antigravity-only execution protocol (6 rules)
- `.agents/agents.md` — Antigravity-only agent role definitions
- `.agents/rules/*.md` — Antigravity-only project structure, Binance API notes, documentation protocol
- No standard file existed for cross-tool compatibility (RooCode, Continue, GitHub Copilot, etc.)

This fragmentation meant different AI tools operated with different subsets of rules, creating inconsistencies in agent behavior and making onboarding of new tools expensive.

## Solution

**Designed** and **Implemented** a single `AGENTS.md` file at the project root following the emerging standard adopted by RooCode, Continue, Cursor, GitHub Copilot, Claude Dev, and other AGENTS.md-aware tools.

### Changes Implemented

| File | Action | Result |
|------|--------|--------|
| `AGENTS.md` (root) | **Created** | Universal source of truth — all rules in English |
| `.cursorrules` | **Updated** | Redirect to AGENTS.md (Cursor backward compat) |
| `.gemini/gemini.md` | **Updated** | Redirect to AGENTS.md (Antigravity backward compat) |
| `.agents/agents.md` | **Updated** | Redirect to AGENTS.md |
| `.agents/rules/` | **Deleted** | Content fully consolidated into AGENTS.md |
| `docs/PROJECT_MAP.md` | **Updated** | New section documenting AGENTS.md as config authority |
| `.agents/workflows/` | **Preserved** | Still active as Antigravity slash commands |
| `.agents/skills/` | **Preserved** | Still active for Antigravity skill execution |

### Content Consolidated into AGENTS.md

1. Project overview and structure (from `binance-workspace-project-rules.md`)
2. Key components table (Backend + Frontend)
3. Binance Futures API critical notes + 2025 breaking change (from `binance-orders-futures-doc.md`)
4. Agent roles: Architect / Developer / Tester / Orchestrator (from `agents.md`)
5. Execution standards — 6 rules including `.temp/` lifecycle (from `gemini.md`)
6. GitFlow quick reference (from `gitflow-process.md`)
7. Documentation protocol — PROJECT_MAP.md rules (from `human-agent-incremental-project-doc.md`)
8. Developer profile, principles, code style TS + Python (from `.cursorrules`)
9. Security and database standards

## Impact

- **All AI tools** (Antigravity, Cursor, RooCode, Continue, GitHub Copilot, etc.) now read the same unified ruleset
- **Zero knowledge loss** — all content preserved, language upgraded to English for maximum compatibility
- **Cleaner project root** — `.agents/rules/` folder removed, structure simplified
- **Backward compatibility maintained** — redirect files kept for Cursor and Antigravity
- Future agents and sessions can be onboarded with a single file read
