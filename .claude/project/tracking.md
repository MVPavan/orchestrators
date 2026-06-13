# Tracking Policy

Status: adapted for Agent Orchestrators on 2026-06-13

## Work Tracking

Beads is the durable work tracker for this repo.

- Use Beads for tasks, bugs, features, epics, decisions, blockers, and durable follow-ups.
- Use in-turn checklists for transient execution steps only.
- Every mutating Beads command should include an actor when practical: `--actor "<runtime>:<session-or-purpose>"`.
- Refresh `.beads/issues.jsonl` after issue changes that should survive through git.
- Use `.beads/beads.md` as the policy source of truth.

## Research Tracking

Use `RESEARCH/` for durable research notes that inform project direction.

Current research:

- `RESEARCH/codex-usage-options.md`

Research notes should include:

- date
- question being answered
- verified local facts
- external sources when used
- recommendation and known caveats

## Workstream Tracking

The intended workstream model is:

- `docs/brainstorms/` for requirements and exploratory decisions
- `docs/workstreams/<name>/README.md` for workstream charter
- `docs/workstreams/<name>/roadmap.md` for phased plan
- `docs/workstreams/<name>/plans/` for per-phase plans
- Beads epics and children for live work state
- generated mirrors under `docs/workstreams/.../tracking/`

This structure is not bootstrapped yet. Until it exists, do not pretend generated workstream status files are available.

## Experiment Or Run Tracking

No experiment tracker is configured for this repo yet.

Do not use inherited MLflow or prior-project tracking conventions as current project policy. If this repo later evaluates orchestrator runs, choose and document the tracking stack first. Candidate dimensions include:

- runtime: Claude Code, Codex CLI, Gemini CLI, API provider
- mode: interactive, noninteractive, cloud, MCP, SDK
- task type: review, implementation, research, orchestration
- artifacts: prompts, command logs, JSONL event streams, diffs, final reports
- metrics: success, cost, latency, resume behavior, verification result

Until then, keep concrete run findings in `RESEARCH/` or Beads issues as appropriate.
