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
- `.claude/project/*.md` inherited from the prior setup

## Files Updated

- `.claude/project/brief.md`
- `.claude/project/docs-index.md`
- `.claude/project/repo-map.md`
- `.claude/project/verification.md`
- `.claude/project/invariants.md`
- `.claude/project/tools.md`
- `.claude/project/tracking.md`
- `.claude/project/learnings.md`
- `.claude/project/adoption-report.md`

## What Changed

- Replaced copied source-project facts with Agent Orchestrators facts.
- Marked `external/gascity` and `external/gastown` as submodule upstreams, not parent-repo source trees.
- Removed Python/Temporal/Postgres/MLflow verification assumptions from the project overlay.
- Added current structural verification commands for Git, submodules, Beads, Claude settings, and hooks.
- Recorded current open gaps: no first-party `src/`, `tests/`, `docs/`, `scripts/`, CI, workstream renderer, or project-native Codex wrappers yet.
- Made `docs/research/codex-usage-options.md` the current Codex research note.

## Assumptions

- "Adapt `.claude/project`" means update the repo-specific overlay only, not the reusable harness commands, skills, agents, or rules.
- The parent repo remains a harness/orchestration repo unless the user later adds first-party implementation code.
- Copied skills that are still useful but project-coupled will be adapted in later passes after this overlay is reviewed.

## Conflicts Or Gaps

- `AGENTS.md` references the generic workstream model and `docs/workstreams/`, but that directory is only a placeholder until the renderer and real workstreams exist.
- `architecture-trace`, `component-review`, and `experiment-tracking` still contain inherited project-specific assumptions.
- `.claude/docs/codex-usage-guide.md` and `.claude/docs/codex-discussions.md` are useful history, but the repo-level Codex research now lives in `docs/research/codex-usage-options.md`.
- The current verification surface is structural. It should be expanded when the repo gains first-party code, manifests, CI, or runtime scripts.

## Recommended Next Review Step

Review the overlay for correctness, especially:

1. whether the repo scope should stay "harness/adoption" or already describe a concrete orchestrator implementation;
2. whether `docs/brainstorms/`, real workstream content, and `scripts/bd-render-tracking.sh` should be bootstrapped next;
3. which inherited skills should be adapted, parked, or removed first.
