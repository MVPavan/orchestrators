# Gas Town Codebase Architecture Research

Analysis date: 2026-06-13
Target path: `external/agent-systems/gastown`
Source commit: `407e109d1743`
Source branch status at read time: `main...origin/main`, clean

## System Purpose

Gas Town is a Go CLI and runtime for coordinating many AI coding agents across one or more repositories. The README describes it as a multi-agent orchestration system for Claude Code, GitHub Copilot, Codex, Gemini, and other agents, with persistent work tracking through git-backed hooks and a Beads ledger (`external/agent-systems/gastown/README.md:3`, `external/agent-systems/gastown/README.md:7`, `external/agent-systems/gastown/README.md:11`). Its central problem is not model inference; it is durable coordination: preserving assignment state, identity, handoffs, issue state, merge queue state, and session recovery when individual agent sessions restart or fail (`external/agent-systems/gastown/README.md:13`, `external/agent-systems/gastown/README.md:16`).

## Reading Map

- `01-core-architecture.md`: architectural thesis, major packages, ownership boundaries, and which parts are core versus peripheral.
- `02-runtime-lifecycle.md`: install, rig creation, work dispatch, worker startup, completion, merge queue, and supervision flows.
- `03-data-state-and-persistence.md`: Beads/Dolt, git worktrees, config files, runtime state, events, mail, identity, and consistency assumptions.
- `04-integration-and-extension-points.md`: supported agent runtimes, hooks, plugins, ACP proxy, provider registry, PR providers, and environment contracts.
- `05-operational-model.md`: build, test, run, inspect, and parent-repo/submodule caveats.
- `90-open-questions.md`: remaining uncertainty, inferred claims, and recommended follow-up reads or experiments.
- `../html/index.html`: human review summary derived from this Markdown set.

## Core Architecture In 11 Points

1. Gas Town is organized around a town workspace containing cross-rig coordination state and per-project rigs, not around a single central service process (`external/agent-systems/gastown/docs/design/architecture.md:82`).
2. `gt` is the control-plane CLI. Every command goes through a Cobra root command with pre-run setup for CLI theme, telemetry, town/session registry initialization, branch warnings, polecat heartbeat updates, and Beads version checks (`external/agent-systems/gastown/internal/cmd/root.go:25`, `external/agent-systems/gastown/internal/cmd/root.go:98`, `external/agent-systems/gastown/internal/cmd/root.go:120`, `external/agent-systems/gastown/internal/cmd/root.go:144`).
3. Beads is the durable work ledger. Gas Town uses town-level Beads for cross-rig coordination and rig-level Beads for implementation work, merge requests, project issues, molecules, and agent beads (`external/agent-systems/gastown/docs/design/architecture.md:5`, `external/agent-systems/gastown/docs/design/architecture.md:10`, `external/agent-systems/gastown/docs/design/architecture.md:24`).
4. Dolt server mode is the persistence backend for Beads. Docs say one Dolt SQL server per town and no embedded fallback; daemon startup also blocks rigs that are not using the Dolt backend (`external/agent-systems/gastown/docs/design/architecture.md:148`, `external/agent-systems/gastown/docs/design/architecture.md:150`, `external/agent-systems/gastown/internal/daemon/daemon.go:1057`).
5. Rigs are project containers around a repository. Each rig has a shared bare repo, a canonical `mayor/rig` clone, a rig Beads database, refinery and polecat worktrees, witness state, and crew clones (`external/agent-systems/gastown/internal/cmd/rig.go:37`, `external/agent-systems/gastown/docs/design/architecture.md:114`, `external/agent-systems/gastown/docs/design/architecture.md:120`).
6. Polecats are autonomous workers with persistent identity but ephemeral sessions; crew are persistent human-owned full clones (`external/agent-systems/gastown/README.md:64`, `external/agent-systems/gastown/docs/overview.md:70`, `external/agent-systems/gastown/docs/overview.md:74`).
7. Work dispatch is driven by `gt sling`: it validates target state, can spawn a polecat, optionally creates a convoy, instantiates formulas or wisps, hooks the bead, stores assignment fields, and starts the worker session (`external/agent-systems/gastown/internal/cmd/sling.go:25`, `external/agent-systems/gastown/internal/cmd/sling_dispatch.go:60`).
8. Agent sessions are tmux sessions. Managers for Deacon, Witness, Refinery, Mayor, polecats, and crew build startup commands, pass role environment variables, install runtime settings, wait for agent readiness, and use `gt prime --hook` or startup fallback prompts (`external/agent-systems/gastown/internal/deacon/manager.go:73`, `external/agent-systems/gastown/internal/witness/manager.go:104`, `external/agent-systems/gastown/internal/refinery/manager.go:108`).
9. Refinery is the merge queue processor. Merge requests are Beads issues labeled `gt:merge-request`; the engineer can process single MRs or batch-then-bisect stacks, run gates, push/verify, and close both MR and source issue (`external/agent-systems/gastown/internal/refinery/types.go:1`, `external/agent-systems/gastown/internal/refinery/batch.go:190`, `external/agent-systems/gastown/internal/refinery/engineer.go:499`).
10. The daemon is recovery-focused. It runs a heartbeat loop, keeps Dolt, Deacon, Witnesses, Refineries, Mayor, convoys, and maintenance dogs alive, and uses tmux plus heartbeat files plus Beads state as health signals (`external/agent-systems/gastown/internal/daemon/daemon.go:48`, `external/agent-systems/gastown/internal/daemon/daemon.go:485`, `external/agent-systems/gastown/internal/daemon/daemon.go:1437`, `external/agent-systems/gastown/internal/daemon/daemon.go:1697`).
11. Agent runtimes are registry-driven. The built-in preset registry includes Claude, Gemini, Codex, Cursor, Auggie, AMP, OpenCode, Copilot, Pi, OMP, Mistral Vibe, and Groq Compound; preset metadata controls commands, resume style, hooks, instructions files, process names, and ACP support (`external/agent-systems/gastown/internal/config/agents.go:18`, `external/agent-systems/gastown/internal/config/agents.go:55`, `external/agent-systems/gastown/internal/config/agents.go:226`).

## Read Next Source Files

- `external/agent-systems/gastown/internal/cmd/root.go`: global CLI lifecycle and dependency checks.
- `external/agent-systems/gastown/internal/cmd/install.go`: town/HQ bootstrap, Beads/Dolt initialization, config creation, hook/plugin provisioning.
- `external/agent-systems/gastown/internal/rig/manager.go`: rig creation, repository layout, Beads setup, routes, agent directories, and registration.
- `external/agent-systems/gastown/internal/cmd/sling_dispatch.go`: dispatch transaction from bead to polecat/formula/hook/session.
- `external/agent-systems/gastown/internal/polecat/manager.go`: worker identity allocation, worktree creation, branch naming, runtime settings, agent bead creation.
- `external/agent-systems/gastown/internal/cmd/done.go` and `external/agent-systems/gastown/internal/cmd/mq_submit.go`: worker completion and MR submission.
- `external/agent-systems/gastown/internal/refinery/engineer.go`, `batch.go`, `score.go`, `manager.go`: merge queue implementation.
- `external/agent-systems/gastown/internal/daemon/daemon.go`, `lifecycle.go`: background recovery, lifecycle mail, Dolt health, and patrol management.
- `external/agent-systems/gastown/internal/config/agents.go`, `loader.go`, `env.go`: runtime agent resolution and startup command generation.
- `external/agent-systems/gastown/internal/hooks/installer.go`: generic hook/settings installation across agent providers.

## Scope Limits

- This pass did not run Gastown tests or start Gastown services. It is source and docs analysis only.
- Web UI, TUI, release workflows, npm package distribution, and visual theming were intentionally de-prioritized unless they affected orchestration behavior.
- Plugin internals were sampled only at the sync/extension boundary, not audited plugin-by-plugin.
- ACP/proxy support was mapped as an integration surface, not fully protocol-tested.
- The source code under `external/agent-systems/gastown` was treated as an external submodule and was not modified.

