# Core Architecture

## Architectural Thesis

Gas Town is best understood as a stateful orchestration shell around git repositories and agent CLIs. The durable source of truth is a combination of filesystem layout, git repositories/worktrees, Beads records backed by Dolt, tmux sessions, and small config/runtime files. The `gt` binary coordinates transitions among those state stores; long-running AI agents execute work by reading hooks and Beads state, then reporting completion through `gt done`, Beads fields, events, nudges, or mail.

The repo documentation states the same shape: a town has infrastructure directories and per-project rigs, and each rig has a bare repo, canonical Beads database, witness/refinery/crew/polecat directories (`external/gastown/docs/overview.md:156`). The technical architecture adds that town Beads and rig Beads deliberately separate cross-rig coordination from implementation work (`external/gastown/docs/design/architecture.md:5`).

## Core Modules And Responsibilities

| Area | Main paths | Responsibility |
| --- | --- | --- |
| CLI control plane | `cmd/gt/main.go`, `internal/cmd/*` | Cobra command graph, setup checks, user commands, town/rig/work dispatch operations. The root pre-run initializes town/session registry and touches polecat heartbeats (`external/gastown/internal/cmd/root.go:25`, `external/gastown/internal/cmd/root.go:120`, `external/gastown/internal/cmd/root.go:144`). |
| Config and runtime agent registry | `internal/config/*` | Town/rig settings, role agent resolution, startup command construction, identity environment, built-in agent presets (`external/gastown/internal/config/types.go:40`, `external/gastown/internal/config/agents.go:55`). |
| Rig lifecycle | `internal/rig/*`, `internal/cmd/rig.go` | Creates project containers, shared bare repos, canonical clones, Beads/Dolt metadata, worktree parents, witness/refinery/crew/polecat directories, routes, and rig registry entries (`external/gastown/internal/rig/manager.go:307`, `external/gastown/internal/rig/manager.go:420`, `external/gastown/internal/rig/manager.go:856`). |
| Work ledger | `internal/beads/*` | Wraps `bd`, adds Gas Town types, routing, MRs, agent beads, custom statuses, and compatibility shims. Beads IDs are the primary work identifiers (`external/gastown/README.md:76`, `external/gastown/internal/constants/constants.go:167`). |
| Dispatch and task binding | `internal/cmd/sling*.go`, `internal/hook*`, `internal/formula`, `internal/wisp` | Converts beads/mail/formulas into hooked work, creates convoys or molecules, assigns workers, and starts sessions (`external/gastown/internal/cmd/sling.go:25`, `external/gastown/internal/cmd/sling_dispatch.go:60`). |
| Worker management | `internal/polecat`, `internal/crew`, `internal/witness` | Allocates workers, creates worktrees/clones, manages tmux sessions, observes worker health, handles completion safety nets (`external/gastown/internal/polecat/manager.go:140`, `external/gastown/internal/cmd/crew.go:29`, `external/gastown/internal/witness/manager.go:32`). |
| Merge queue | `internal/refinery`, `internal/cmd/mq_submit.go` | Creates Beads-backed MRs, scores queue items, claims MRs, runs gates, squashes or PR-merges branches, and closes source work (`external/gastown/internal/cmd/mq_submit.go:78`, `external/gastown/internal/refinery/engineer.go:499`). |
| Supervision | `internal/daemon`, `internal/deacon`, `internal/boot`, `internal/dog` | Recovery daemon, Deacon patrol agent, dogs, Dolt health, stuck detection, lifecycle requests, maintenance (`external/gastown/internal/daemon/daemon.go:48`, `external/gastown/internal/deacon/manager.go:43`). |
| Communication | `internal/mail`, `internal/nudge`, `internal/events`, `internal/protocol`, `internal/channelevents` | Mailboxes, tmux nudges, event files, channel events, session beacons and handoffs (`external/gastown/internal/session/startup.go:27`, `external/gastown/internal/witness/protocol.go:13`). |
| Integration runtime | `internal/hooks`, `internal/plugin`, `internal/acp`, `internal/agent/provider`, `internal/wrappers` | Provider-specific hooks/settings, plugin sync, ACP proxy/protocol, command wrappers (`external/gastown/internal/hooks/installer.go:1`, `external/gastown/internal/plugin/sync.go:21`, `external/gastown/internal/acp/proxy.go:42`). |

## Ownership Boundaries

Town-level state owns cross-rig coordination:

- town Beads at `~/gt/.beads/`, `hq-*` prefix, Mayor/Deacon/Boot/Dog agent beads, role definitions, mail, strategic coordination (`external/gastown/docs/design/architecture.md:10`, `external/gastown/docs/design/architecture.md:15`).
- town config under `mayor/` and `settings/`, including `town.json`, `rigs.json`, `daemon.json`, `accounts.json`, and `settings/config.json` (`external/gastown/docs/design/architecture.md:94`).
- daemon, Deacon, Mayor, feed curator, convoy manager, Dolt server manager, and town maintenance (`external/gastown/internal/daemon/daemon.go:48`, `external/gastown/internal/daemon/daemon.go:492`, `external/gastown/internal/daemon/daemon.go:500`).

Rig-level state owns implementation work:

- each rig has a project prefix, rig Beads in `mayor/rig/.beads`, a shared `.repo.git`, and workspaces for refinery, witness, crew, and polecats (`external/gastown/docs/design/architecture.md:24`, `external/gastown/docs/design/architecture.md:114`).
- witness and refinery are one per rig and persistent; polecats have persistent identity but task-scoped sessions; crew are user-managed full clones (`external/gastown/docs/overview.md:28`, `external/gastown/docs/overview.md:39`, `external/gastown/docs/overview.md:74`).

The dependency direction is mostly town to rig to worker. `gt install` creates a town, `gt rig add` creates rig containers, `gt sling` binds work to workers, workers submit MRs, and refinery merges back into the rig's target branch. Workers should not be treated as owning the queue or global coordination; they own execution of their hook.

## Key Abstractions

### Town

A town is the top-level workspace and control boundary. It holds town Beads, central Dolt data, daemon state, Mayor and Deacon homes, global settings, and registered rigs (`external/gastown/docs/design/architecture.md:82`). `gt install` creates this structure, writes `mayor/town.json` and `mayor/rigs.json`, initializes Git, initializes town Beads, starts/initializes Dolt, creates agent beads, and provisions commands/hooks (`external/gastown/internal/cmd/install.go:50`, `external/gastown/internal/cmd/install.go:202`, `external/gastown/internal/cmd/install.go:348`).

### Rig

A rig wraps a single project repository. The `rig.Rig` model carries name, path, git URLs, Beads config, known polecats/crew, and booleans for witness/refinery/mayor state (`external/gastown/internal/rig/types.go:8`). `Manager.AddRig` creates the rig directory, config, shared bare repo, canonical mayor clone, rig Beads DB, role files, refinery worktree, crew/witness/polecat directories, routes, agent beads, plugin directories, and registry entry (`external/gastown/internal/rig/manager.go:307`, `external/gastown/internal/rig/manager.go:420`, `external/gastown/internal/rig/manager.go:527`, `external/gastown/internal/rig/manager.go:758`, `external/gastown/internal/rig/manager.go:905`).

### Bead

Gas Town uses Beads issues as durable work records. Bead IDs carry a prefix plus a short ID, and prefix routes map IDs to town or rig databases (`external/gastown/README.md:80`, `external/gastown/docs/design/architecture.md:175`). Agent beads track lifecycle state for agents; MR beads track merge requests; convoys and molecules track higher-level work coordination (`external/gastown/docs/design/architecture.md:32`, `external/gastown/internal/constants/constants.go:167`).

### Hook

A hook is an agent's current assignment, expressed through Beads state and runtime files. The project docs state the core rule as: if work is on the hook, the agent runs it (`external/gastown/docs/overview.md:180`). Dispatch code materializes that by hooking a bead to an agent, setting assignment fields, and starting or nudging the session (`external/gastown/internal/cmd/sling_dispatch.go:331`, `external/gastown/internal/cmd/sling_dispatch.go:357`, `external/gastown/internal/cmd/sling_dispatch.go:379`).

### Polecat

A polecat is a worker identity and workspace lifecycle. The manager allocates names, locks a pool, derives branch names, creates a worktree, redirects Beads to the canonical DB, provisions runtime settings and startup hooks, creates/reopens an agent bead, and returns the worker as `StateWorking` (`external/gastown/internal/polecat/manager.go:532`, `external/gastown/internal/polecat/manager.go:657`, `external/gastown/internal/polecat/manager.go:725`).

### Refinery

Refinery owns merge queue execution. Queue state is Beads-backed, not in a private daemon database. The manager lists Beads issues labeled `gt:merge-request`, scores/sorts them, and exposes queue items (`external/gastown/internal/refinery/manager.go:333`). The engineer then validates branch state, runs gates, merges, pushes, closes MRs/source issues, and handles failure recovery (`external/gastown/internal/refinery/engineer.go:499`, `external/gastown/internal/refinery/engineer.go:1167`, `external/gastown/internal/refinery/engineer.go:1294`).

### Daemon, Deacon, Witness

The daemon is the non-agent recovery loop. Deacon and Witness are agent sessions it keeps alive. Daemon comments explicitly describe it as recovery-focused: feed subscription handles normal wake; daemon is the safety net for dead sessions, GUPP violations, and orphaned work (`external/gastown/internal/daemon/daemon.go:48`). Deacon starts as a tmux session with role settings and a startup prompt to run patrol (`external/gastown/internal/deacon/manager.go:73`, `external/gastown/internal/deacon/manager.go:109`). Witness is rig-scoped and uses tmux as source of truth for session state (`external/gastown/internal/witness/manager.go:32`, `external/gastown/internal/witness/manager.go:45`).

## Central Versus Peripheral

Central:

- Beads/Dolt stores, route files, agent beads, MRs, convoys, molecules.
- Git repository layout, worktrees, canonical clones, branch naming, merge queue.
- `gt` command flow and tmux agent session lifecycle.
- Agent runtime registry, startup env, hooks, and nudge/event/mail channels.
- Daemon, Deacon, Witness, Refinery recovery and patrol behaviors.

Peripheral for this research pass:

- Visual styling and theme code, except where it affects tmux session setup.
- Web/TUI dashboards, except as observation surfaces.
- Release pipelines, package publishing, and npm package scaffolding.
- Individual plugin business logic, except the plugin loading/sync contract.
- Model evaluation harnesses, except as evidence that provider selection is first-class.

