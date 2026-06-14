# Adoption Report

Status: draft adapted overlay for Agent Orchestrators

Date: 2026-06-13

## Inputs Read

- `README.md`
- `.gitmodules`
- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`
- `.beads/beads.md`
- `.beads/config.yaml`
- `.beads/README.md`
- `docs/research/codex-usage-options.md`
- `.codex/project/*.md` inherited from the prior setup

## Files Updated

- `.codex/project/brief.md`
- `.codex/project/docs-index.md`
- `.codex/project/repo-map.md`
- `.codex/project/verification.md`
- `.codex/project/invariants.md`
- `.codex/project/tools.md`
- `.codex/project/tracking.md`
- `.codex/project/learnings.md`
- `.codex/project/adoption-report.md`

## What Changed

- Replaced copied source-project facts with Agent Orchestrators facts.
- Marked `external/gascity` and `external/gastown` as submodule upstreams, not parent-repo source trees.
- Removed Python/Temporal/Postgres/MLflow verification assumptions from the project overlay.
- Added current structural verification commands for Git, submodules, Beads, Codex settings, hooks, rules, and skills.
- Recorded current open gaps: no first-party `src/`, `tests/`, `scripts/`, CI, workstream renderer, or standalone CLI wrapper scripts yet.
- Made `docs/research/codex-usage-options.md` the current Codex research note.
- Added Codex-native skills, agents, hooks, rules, and project overlay under `.codex/`.

## Assumptions

- "Adapt `.codex/project`" means update the repo-specific overlay only, not the reusable harness commands, skills, agents, hooks, or rules unless the user explicitly asks for a migration pass.
- The parent repo remains a harness/orchestration repo unless the user later adds first-party implementation code.
- Copied skills that are still useful but project-coupled should be refined in later passes after real usage exposes drift.

## Conflicts Or Gaps

- `AGENTS.md` references the generic workstream model and `docs/workstreams/`, but that directory is only a placeholder until the renderer and real workstreams exist.
- Legacy Claude-specific assets remain under `.claude/`; use them only for Claude Code runs.
- `.codex/docs/codex-usage-guide.md` and `.codex/docs/codex-discussions.md` are useful history, but the repo-level Codex research now lives in `docs/research/codex-usage-options.md`.
- The current verification surface is structural. It should be expanded when the repo gains first-party code, manifests, CI, or runtime scripts.

## Recommended Next Review Step

Review the overlay for correctness, especially:

1. whether the repo scope should stay "harness/adoption" or already describe a concrete orchestrator implementation;
2. whether `docs/brainstorms/`, real workstream content, and `scripts/bd-render-tracking.sh` should be bootstrapped next;
3. which inherited skills should be tightened after first Codex usage.
