# Tools & Subagents — when to reach for what

Routing triggers live in `AGENTS.md`; this file holds the per-tool operating detail.

## Codex (one-way, best-effort critic)

- **When:** plan/doc critique (`rescue`), standard diffs (`review`), deep/cross-boundary diffs
  (`adversarial-review`). Skip for `small` tasks unless risk is unusual.
- **How:** follow [`.claude/commands/use-codex.md`](../commands/use-codex.md) — authoritative; it owns the
  invocation path (Agent subagent vs Bash; Skill path banned) and the operational rules (zombie check,
  one job at a time, `--effort low` floor, gate off). Deep reference: `.claude/docs/codex-usage-guide.md`.
- **Capacity errors:** retry once → proceed without Codex and log the skip. Never blocking.
- Codex reviews your completed output; do not assume a reverse loop exists.

## docs-researcher (library/API documentation)

- **When:** unsure about a library, framework, SDK, API, CLI tool, or cloud service — methods, signatures,
  config keys, version-specific behavior, migration steps. Any question where training data may be stale.
- **Not for:** refactoring, writing scripts, debugging business logic, code review, general concepts.
- **How:** Agent tool, `subagent_type: "docs-researcher"` (Context7-wired, runs on Haiku). Give it the
  library name, the specific question, and the repo-pinned version if relevant.

## experiment-tracking (MLflow)

- **When:** any experiment producing params/metrics/output files (sweeps, benchmarks, calibrations).
- **How:** the `experiment-tracking` skill; policy fence in [`tracking.md`](tracking.md).

## html-artifact

- **When:** human-facing documents (reports, plans, explainers) that benefit from richer structure than
  markdown. Not for git/CLI/agent-destined content.
- **How:** the `html-artifact` skill.
