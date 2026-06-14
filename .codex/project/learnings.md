# Durable Learnings

Add entries here only after a fact, fix, or pattern has been verified and is likely to recur.
Keep entries short. Never store secrets or machine-local paths.

## Entry Format

### YYYY-MM-DD - Short Title

- Scope:
- Trigger:
- Rule:
- Evidence:
- Related docs:

---

### 2026-06-13 - Track upstream projects as submodules

- Scope: `external/gascity` and `external/gastown`.
- Trigger: deciding how to keep upstream projects inside the parent repo without tracking all internals.
- Rule: keep upstream projects as Git submodules under `external/`; the parent repo tracks only commit pointers.
- Evidence: `.gitmodules` declares both submodules on `main`; `README.md` documents clone and sync commands.
- Related docs: `README.md`, `.gitmodules`, `.codex/project/repo-map.md`.

### 2026-06-13 - Beads is the durable work tracker

- Scope: project work items, blockers, decisions, and handoff state.
- Trigger: initializing Beads for this repo.
- Rule: use `bd` for durable work state; use `.beads/issues.jsonl` as the git-reviewable mirror; do not commit/push or sync remotes unless authorized.
- Evidence: `.beads/config.yaml` enables auto-export to `issues.jsonl`; `.beads/beads.md` defines policy.
- Related docs: `.beads/beads.md`, `.codex/project/tracking.md`.

### 2026-06-13 - Prefer repo-native Codex primitives over Claude plugin internals

- Scope: Codex orchestration decisions.
- Trigger: comparing Codex Cloud, CLI, SDK, app-server, MCP, and the installed Claude Code Codex plugin.
- Rule: use `codex exec`, `codex exec resume`, and `codex review` as the default automation foundation; keep the Claude plugin as an interactive convenience layer.
- Evidence: current research note records official-doc and local-plugin findings.
- Related docs: `docs/research/codex-usage-options.md`, `.codex/project/tools.md`.

### 2026-06-13 - Codex loads repo-local .codex skills here

- Scope: repo-local Codex skills.
- Trigger: migrating Claude skills and commands into Codex-native surfaces.
- Rule: keep active repo-local Codex skills under `.codex/skills` in this repository.
- Evidence: `codex debug prompt-input` with a temporary `CODEX_HOME` listed `.codex/skills/codebase-architecture-research/SKILL.md` as an available skill.
- Related docs: `.codex/README.md`, `.agents/README.md`, `.codex/project/repo-map.md`, `.codex/docs/codex-migration-notes.md`.
