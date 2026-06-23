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
- Related docs: `README.md`, `.gitmodules`, `.claude/project/repo-map.md`.

### 2026-06-13 - Beads is the durable work tracker

- Scope: project work items, blockers, decisions, and handoff state.
- Trigger: initializing Beads for this repo.
- Rule: use `bd` for durable work state; use `.beads/issues.jsonl` as the git-reviewable mirror; do not commit/push or sync remotes unless authorized.
- Evidence: `.beads/config.yaml` enables auto-export to `issues.jsonl`; `.beads/beads.md` defines policy.
- Related docs: `.beads/beads.md`, `.claude/project/tracking.md`.

### 2026-06-13 - Prefer repo-native Codex primitives over Claude plugin internals

- Scope: Codex orchestration decisions.
- Trigger: comparing Codex Cloud, CLI, SDK, app-server, MCP, and the installed Claude Code Codex plugin.
- Rule: use `codex exec`, `codex exec resume`, and `codex review` as the default automation foundation; keep the Claude plugin as an interactive convenience layer.
- Evidence: current research note records official-doc and local-plugin findings.
- Related docs: `docs/research/codex-usage-options.md`, `.claude/project/tools.md`.

### 2026-06-22 - Isolate multi-tool harness experiments from the first executing run

- Scope: multi-tool harness experiments that clone + run many third-party analysis tools (e.g. the 8-tool codebase-analysis study on paperclip).
- Trigger: tools that install globally, phone home (telemetry), log to `~/`, or write index artifacts into the target tree — any of which can leak across experiments.
- Rule: enforce three isolation planes — (1) per-tool dirs + a read-only canonical subject + per-tool writable copies; (2) no global installs, invoke by explicit local path; (3) a tool-local `HOME` plus telemetry/log kill-switches, applied from the FIRST run that EXECUTES a tool, not just the heavy phase. Then run an INDEPENDENT orchestrator-side audit — do not trust worker self-reports.
- Evidence: all 8 Phase-B runs audited clean, but the independent audit caught 2 Phase-A leaks the self-reports missed (codegraph `~/.codegraph` telemetry with a `machine_id`; graphify `~/.cache/graphify-queries.log`) — created before the HOME-hardening existed; both removed.
- Related docs: `docs/research/harness/isolation-contract.md`, `docs/research/harness/results/_isolation_audit.md`, `docs/research/harness/findings.md`.
