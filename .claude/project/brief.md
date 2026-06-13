# Project Brief

Status: early harness/adoption phase

Last updated: 2026-06-13

## What This Repo Is

Agent Orchestrators is a workspace for designing, testing, and standardizing multi-agent orchestration workflows.

The project direction is subscription-first where practical: use local CLI products such as Codex CLI, Claude Code, and Gemini CLI when they provide enough capability. API-based providers remain valid when automation, CI, SDK control, or non-interactive execution needs them.

This repository is currently a parent/harness repo. It does not yet contain a first-party application source tree.

## Upstream Projects

The repo tracks upstream projects as Git submodules under `external/`:

| Path | Upstream | Branch |
| --- | --- | --- |
| `external/gascity` | `https://github.com/gastownhall/gascity.git` | `main` |
| `external/gastown` | `https://github.com/gastownhall/gastown.git` | `main` |

Only submodule commit pointers belong to this parent repo. The internal files and history of those projects stay in their own repositories.

## Current Stack

- **Version control:** Git parent repo plus Git submodules for upstream projects.
- **Issue tracking:** Beads (`bd`) with local Dolt storage and `.beads/issues.jsonl` as the git-reviewable mirror.
- **Agent runtimes:** Claude Code harness, Codex CLI/plugin research, Gemini CLI as a likely peer runtime.
- **Research artifacts:** `docs/research/`.
- **First-party application code:** not present yet.
- **Workstream docs:** `docs/workstreams/` exists as a placeholder; real workstreams and generated mirrors are not bootstrapped yet.

## How Work Happens

- Durable work is tracked in Beads. Use `.beads/beads.md` as the project policy.
- Research decisions should land under `docs/research/` unless they belong in a formal project doc.
- The reusable Claude harness lives under `.claude/`, but `.claude/project/` is the repo-specific overlay.
- External repos are inspected as references or upstreams. Do not edit their internals from the parent repo unless the task explicitly asks for submodule work.

## Non-Negotiable Constraints

- Keep `external/gascity` and `external/gastown` as submodules, not copied source trees.
- Do not hand-edit Beads-generated workstream mirrors once the renderer exists; update Beads first, then regenerate.
- Do not commit or push unless explicitly asked or an active workflow grants that authority.
- Do not claim tests or runtime behavior for first-party code until such code and verification commands exist.
- Prefer repo-relative paths in docs, prompts, and plans.

## Open Adoption Gaps

- `docs/brainstorms/` and `scripts/bd-render-tracking.sh` are not present yet. `docs/workstreams/` exists as a placeholder only.
- `architecture-trace`, `component-review`, and experiment-tracking skills still need adaptation before use.
- The Codex integration research is captured in `docs/research/codex-usage-options.md`, but project-native wrappers are not implemented yet.
