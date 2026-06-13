# Docs Index

Status: adapted for Agent Orchestrators on 2026-06-13

Use this file to find the right source before guessing. Prefer current repo files over inherited harness docs.

## Current Project Docs

| Path | Purpose | Authority | Read When |
| --- | --- | --- | --- |
| `README.md` | Public repo summary, submodule layout, clone/sync commands | authoritative | Understanding the parent repo and upstream sync model |
| `AGENTS.md` | Always-loaded agent operating guide | authoritative, pending cleanup | Starting any agent work in this repo |
| `CLAUDE.md` | Claude entry point pointing at `AGENTS.md` | authoritative | Claude Code startup |
| `.gitmodules` | Submodule path, URL, and branch declarations | authoritative | Working with `external/gascity` or `external/gastown` |
| `.beads/beads.md` | Beads policy, work item conventions, generated mirror rules | authoritative | Creating, claiming, closing, or syncing issues |
| `.beads/config.yaml` | Beads sync/export configuration | authoritative | Debugging issue tracker persistence or sync |
| `RESEARCH/codex-usage-options.md` | Current Codex surface comparison and adoption recommendation | authoritative research note | Deciding how to invoke Codex from Claude, Gemini, shell, cloud, SDK, or MCP |

## Claude Harness Docs

| Path | Purpose | Authority | Read When |
| --- | --- | --- | --- |
| `.claude/project/brief.md` | Repo-specific facts and constraints | authoritative | Orienting on project scope |
| `.claude/project/repo-map.md` | Physical tree and navigation | authoritative | Finding where things live |
| `.claude/project/verification.md` | Trusted verification commands for current repo state | authoritative | Before claiming work is complete |
| `.claude/project/invariants.md` | Mechanically checkable project facts | authoritative | Running `/check-invariants` or reviewing risky changes |
| `.claude/project/tools.md` | Tool and runtime routing guidance | authoritative | Choosing Beads, Codex, Claude plugin, Gemini, or docs research |
| `.claude/project/tracking.md` | Durable work/run tracking policy | authoritative | Recording work, research, or future experiments |
| `.claude/project/learnings.md` | Durable verified learnings | supporting | Looking for recurring repo-specific decisions |

## Legacy Or Candidate Docs

These files came from the copied harness and may contain useful patterns, but they are not current project truth until adapted.

| Path | Current Status | Use With Care |
| --- | --- | --- |
| `.claude/docs/codex-usage-guide.md` | Claude-plugin-oriented Codex guide from prior setup | Cross-check against `RESEARCH/codex-usage-options.md` before applying |
| `.claude/docs/codex-discussions.md` | Discussion history for Codex plugin usage | Treat as historical notes |
| `.claude/docs/beads-issue-tracking-adoption.md` | Beads adoption notes | Useful background; `.beads/beads.md` wins |
| `.claude/docs/mlflow-experiment-tracking-adoption.md` | Prior experiment-tracking adoption plan | Not current policy for this repo |

## Upstream Submodule Docs

| Path | Meaning |
| --- | --- |
| `external/gascity/README.md`, `external/gascity/AGENTS.md`, `external/gascity/CLAUDE.md` | Upstream project docs. Read when inspecting gascity, but do not treat them as parent-repo policy. |
| `external/gastown/README.md`, `external/gastown/AGENTS.md` | Upstream project docs. Read when inspecting gastown, but do not treat them as parent-repo policy. |

## Planned But Not Present Yet

| Planned Path | Intended Purpose |
| --- | --- |
| `docs/brainstorms/` | Durable brainstorm and requirements inbox |
| `docs/workstreams/` | Workstream charters, roadmaps, plans, and Beads-generated mirrors |
| `scripts/bd-render-tracking.sh` | Renderer for Beads-generated workstream views |
| `docs/architecture-trace/` | Architecture trace outputs after the skill is generalized |
| `docs/reviews/` | Component/system review outputs after the skill is generalized |
