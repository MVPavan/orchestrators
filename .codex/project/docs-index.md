# Docs Index

Status: adapted for Agent Orchestrators on 2026-06-13

Use this file to find the right source before guessing. Prefer current repo files over inherited harness docs.

## Current Project Docs

| Path | Purpose | Authority | Read When |
| --- | --- | --- | --- |
| `README.md` | Public repo summary, submodule layout, clone/sync commands | authoritative | Understanding the parent repo and upstream sync model |
| `AGENTS.md` | Always-loaded agent operating guide | authoritative | Starting any agent work in this repo |
| `CLAUDE.md` | Claude entry point pointing at `AGENTS.md` | authoritative | Claude Code startup |
| `.gitmodules` | Submodule path, URL, and branch declarations | authoritative | Working with `external/gascity` or `external/gastown` |
| `.beads/beads.md` | Beads policy, work item conventions, generated mirror rules | authoritative | Creating, claiming, closing, or syncing issues |
| `.beads/config.yaml` | Beads sync/export configuration | authoritative | Debugging issue tracker persistence or sync |
| `docs/research/codex-usage-options.md` | Current Codex surface comparison and adoption recommendation | authoritative research note | Deciding how to invoke Codex from Codex, Claude, Gemini, shell, cloud, SDK, or MCP |
| `.codex/config.toml` | Project-scoped Codex config | authoritative when trusted by Codex | Checking Codex project settings |
| `.codex/hooks.json` | Codex lifecycle hook registration | authoritative when trusted by Codex | Checking Codex hook wiring |
| `.codex/rules/default.rules` | Codex exec-policy rules | authoritative when trusted by Codex | Checking high-risk command policy |
| `.codex/skills/` | Repo-local Codex skills | authoritative | Reusable workflows and migrated command flows |
| `.codex/agents/` | Repo-local Codex custom agents | authoritative | Subagent role behavior |
| `.codex/docs/codex-migration-notes.md` | Source-backed record of Claude-to-Codex mapping decisions | authoritative migration note | Understanding why migrated surfaces live where they do |

## Codex Project Docs

| Path | Purpose | Authority | Read When |
| --- | --- | --- | --- |
| `.codex/project/brief.md` | Repo-specific facts and constraints | authoritative | Orienting on project scope |
| `.codex/project/repo-map.md` | Physical tree and navigation | authoritative | Finding where things live |
| `.codex/project/verification.md` | Trusted verification commands for current repo state | authoritative | Before claiming work is complete |
| `.codex/project/invariants.md` | Mechanically checkable project facts | authoritative | Running `$check-invariants` or reviewing risky changes |
| `.codex/project/tools.md` | Tool and runtime routing guidance | authoritative | Choosing Beads, Codex, Claude plugin, Gemini, or docs research |
| `.codex/project/tracking.md` | Durable work/run tracking policy | authoritative | Recording work, research, or future experiments |
| `.codex/project/learnings.md` | Durable verified learnings | supporting | Looking for recurring repo-specific decisions |

## Legacy Or Candidate Docs

These files came from the copied harness and may contain useful patterns, but they are not current project truth until adapted.

| Path | Current Status | Use With Care |
| --- | --- | --- |
| `.codex/docs/codex-usage-guide.md` | Claude-plugin-oriented Codex guide from prior setup | Cross-check against `docs/research/codex-usage-options.md` before applying |
| `.codex/docs/codex-discussions.md` | Discussion history for Codex plugin usage | Treat as historical notes |
| `.codex/docs/beads-issue-tracking-adoption.md` | Beads adoption notes | Useful background; `.beads/beads.md` wins |
| `.codex/docs/mlflow-experiment-tracking-adoption.md` | Prior experiment-tracking adoption plan | Not current policy for this repo |

## Legacy Claude Harness

| Path | Current Status | Use With Care |
| --- | --- | --- |
| `.claude/` | Claude Code-specific source harness retained for Claude runs | Do not treat it as Codex authority unless the task is explicitly Claude-local |

## Upstream Submodule Docs

| Path | Meaning |
| --- | --- |
| `external/gascity/README.md`, `external/gascity/AGENTS.md`, `external/gascity/CLAUDE.md` | Upstream project docs. Read when inspecting gascity, but do not treat them as parent-repo policy. |
| `external/gastown/README.md`, `external/gastown/AGENTS.md` | Upstream project docs. Read when inspecting gastown, but do not treat them as parent-repo policy. |

## Planned But Not Present Yet

| Planned Path | Intended Purpose |
| --- | --- |
| `docs/brainstorms/` | Durable brainstorm and requirements inbox |
| `docs/workstreams/` | Placeholder now; later workstream charters, roadmaps, plans, and Beads-generated mirrors |
| `scripts/bd-render-tracking.sh` | Renderer for Beads-generated workstream views |
