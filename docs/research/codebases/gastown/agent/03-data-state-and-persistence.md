# Data, State, And Persistence

## State Map

| State | Location / owner | Notes |
| --- | --- | --- |
| Town Beads | `~/gt/.beads/`, `hq-*` | Cross-rig coordination, Mayor mail, agent identity, role definitions (`external/gastown/docs/design/architecture.md:10`, `external/gastown/docs/design/architecture.md:15`). |
| Rig Beads | `<rig>/mayor/rig/.beads/`, project prefix | Implementation issues, MRs, project molecules, rig-level agent beads (`external/gastown/docs/design/architecture.md:24`). |
| Dolt databases | `~/gt/.dolt-data/<db>` | One Dolt SQL server per town; Beads talks over MySQL protocol (`external/gastown/docs/design/architecture.md:148`, `external/gastown/docs/design/architecture.md:150`). |
| Routes | `~/gt/.beads/routes.jsonl` | Maps prefixes such as `hq-`, `gt-`, `bd-` to town or rig canonical Beads paths (`external/gastown/docs/design/architecture.md:175`). |
| Git source | `<rig>/.repo.git`, `<rig>/mayor/rig` | Shared bare repo plus canonical clone used as worktree base (`external/gastown/internal/rig/manager.go:420`, `external/gastown/internal/rig/manager.go:527`). |
| Worker git state | `<rig>/polecats/<name>/<rig>/`, `<rig>/refinery/rig`, `<rig>/crew/<name>` | Polecats/refinery are worktrees; crew are full clones (`external/gastown/docs/design/architecture.md:135`, `external/gastown/docs/design/architecture.md:145`). |
| Town config | `mayor/town.json`, `mayor/rigs.json`, `settings/config.json`, `mayor/daemon.json`, `mayor/accounts.json` | Created during install and used by config/daemon/session startup (`external/gastown/docs/design/architecture.md:100`, `external/gastown/internal/cmd/install.go:229`). |
| Rig config | `<rig>/config.json`, `<rig>/settings/config.json` | Rig identity, Beads prefix, settings, merge queue and agent overrides (`external/gastown/docs/design/architecture.md:114`, `external/gastown/internal/config/loader.go:168`). |
| Agent runtime settings | Role-specific settings dirs, `.runtime`, hook files | Produced by runtime/config/hooks paths before session start (`external/gastown/internal/witness/manager.go:172`, `external/gastown/internal/hooks/installer.go:24`). |
| Tmux sessions | tmux server | Source of truth for session running state for Witness/Refinery/Deacon/Mayor and worker sessions (`external/gastown/internal/witness/manager.go:32`, `external/gastown/internal/refinery/manager.go:64`). |
| Heartbeats | Session heartbeat files and agent bead state | Polecat heartbeats are touched by `gt` commands; Deacon heartbeat drives stuck detection (`external/gastown/internal/cmd/root.go:144`, `external/gastown/internal/daemon/daemon.go:1490`). |
| Events/mail/nudges | `events/`, Beads mail, tmux nudges | Used for startup propulsion, merge notifications, lifecycle requests, and fallback wakeups (`external/gastown/internal/session/startup.go:59`, `external/gastown/internal/daemon/lifecycle.go:41`, `external/gastown/internal/witness/handlers.go:335`). |
| Logs/telemetry | daemon logs, agent JSONL logs, OpenTelemetry export | Daemon uses lumberjack rotation and optional OTel; witness can stream Claude Code JSONL (`external/gastown/internal/daemon/daemon.go:225`, `external/gastown/internal/witness/manager.go:279`). |

## Beads And Dolt

The documented Beads architecture has two levels: town-level `hq-*` for cross-rig coordination and rig-level project prefixes for implementation work (`external/gastown/docs/design/architecture.md:5`). Agent bead storage follows the same split: Mayor/Deacon/Boot/Dogs live in town Beads, while Witness/Refinery/Polecats/Crew live in rig Beads (`external/gastown/docs/design/architecture.md:32`).

The implementation enforces the Dolt backend operationally. Daemon startup checks town and each registered rig's `.beads/metadata.json` and blocks startup when the backend is not `dolt` (`external/gastown/internal/daemon/daemon.go:1057`). The daemon also ensures Dolt server health and propagates `GT_DOLT_PORT`, `BEADS_DOLT_PORT`, `GT_DOLT_HOST`, and `BEADS_DOLT_SERVER_HOST` to child sessions so `bd` does not start rogue local Dolt instances (`external/gastown/internal/daemon/daemon.go:297`, `external/gastown/internal/daemon/daemon.go:303`, `external/gastown/internal/daemon/daemon.go:316`, `external/gastown/internal/daemon/daemon.go:329`).

Beads CLI access is wrapped by `internal/beads`. The wrapper injects compatibility flags such as `--allow-stale`, injects `--flat` for JSON list output, and unwraps routed issue IDs (`external/gastown/internal/beads/beads.go:54`, `external/gastown/internal/beads/beads.go:123`, `external/gastown/internal/beads/beads.go:148`).

## Routing And Redirects

Routes are explicit. The architecture doc shows `routes.jsonl` entries mapping prefixes to rig paths and says routes point to `mayor/rig` because canonical Beads lives there (`external/gastown/docs/design/architecture.md:175`, `external/gastown/docs/design/architecture.md:185`). `Manager.AddRig` appends the route during rig creation (`external/gastown/internal/rig/manager.go:856`).

Worktrees do not own independent Beads DBs. The docs state they use `.beads/redirect` files pointing at the canonical Beads location; `ResolveBeadsDir` follows redirects so agents in a rig share the same database (`external/gastown/docs/design/architecture.md:193`, `external/gastown/docs/design/architecture.md:203`). The code sets up these redirects for witness, polecats, and refinery during startup/provisioning (`external/gastown/internal/witness/manager.go:160`, `external/gastown/internal/polecat/manager.go:725`, `external/gastown/internal/rig/manager.go:758`).

## Identity Schemes

Agent identity is encoded at several layers:

- Beads IDs use prefixes plus role/name identifiers, e.g. town `hq-mayor`, rig `<prefix>-<rig>-witness`, `<prefix>-<rig>-polecat-<name>` (`external/gastown/docs/design/architecture.md:37`).
- Human/worker identities use path-like forms such as `<rig>/crew/<name>` and `<rig>/polecats/<name>` (`external/gastown/docs/overview.md:81`).
- Lifecycle identity parsing supports town singletons, `rig-witness`, `rig-refinery`, `rig-crew-name`, `rig-polecat-name`, and `rig/polecats/name` formats (`external/gastown/internal/daemon/lifecycle.go:221`).
- Startup environment variables are generated centrally by `config.AgentEnv` and related config resolution functions (`external/gastown/internal/config/env.go:79`).

The docs emphasize identity and attribution: git commits, Beads issues, and events preserve actor identity, even for cross-rig worktrees (`external/gastown/docs/overview.md:165`).

## Read And Write Paths

### Config write paths

Install and rig add write most structural config:

- `gt install` writes town and rig registry files, runtime settings, daemon config, formulas, agent beads, and hook/command provisioning (`external/gastown/internal/cmd/install.go:229`, `external/gastown/internal/cmd/install.go:286`, `external/gastown/internal/cmd/install.go:331`, `external/gastown/internal/cmd/install.go:381`, `external/gastown/internal/cmd/install.go:426`).
- config loader functions use atomic load/save for `mayor/rigs.json` and validate rig merge queue settings (`external/gastown/internal/config/loader.go:84`, `external/gastown/internal/config/loader.go:226`).
- rig creation saves rig config, settings, and registry entries (`external/gastown/internal/rig/manager.go:402`, `external/gastown/internal/rig/manager.go:874`, `external/gastown/internal/rig/manager.go:905`).

### Work assignment path

Dispatch writes both Beads and git/runtime state. `executeSling` locks, validates, creates or reuses a worker, optionally creates convoy/formula/wisp state, hooks the bead, logs events, updates agent bead state, stores fields on the source bead, and starts the session (`external/gastown/internal/cmd/sling_dispatch.go:60`, `external/gastown/internal/cmd/sling_dispatch.go:97`, `external/gastown/internal/cmd/sling_dispatch.go:331`, `external/gastown/internal/cmd/sling_dispatch.go:350`, `external/gastown/internal/cmd/sling_dispatch.go:357`).

### Git write path

Polecats work on branches in worktrees. Completion through `gt done` protects uncommitted work and stashes, auto-commits when safe, rebases, and submits/updates the queue (`external/gastown/internal/cmd/done.go:299`, `external/gastown/internal/cmd/done.go:355`, `external/gastown/internal/cmd/done.go:697`). Refinery then performs merges, gates, pushes, branch deletion, and source issue closure (`external/gastown/internal/refinery/engineer.go:499`, `external/gastown/internal/refinery/engineer.go:1167`).

### Merge request path

MRs are Beads issues labeled `gt:merge-request`. `mq submit` checks target, dependencies, branch existence, pushed commit SHA, creates or deduplicates MRs, and nudges refinery (`external/gastown/internal/cmd/mq_submit.go:164`, `external/gastown/internal/cmd/mq_submit.go:207`, `external/gastown/internal/cmd/mq_submit.go:235`, `external/gastown/internal/cmd/mq_submit.go:260`, `external/gastown/internal/cmd/mq_submit.go:290`).

## Consistency And Concurrency

- Dispatch uses a per-bead lock to prevent simultaneous assignment of the same bead (`external/gastown/internal/cmd/sling_dispatch.go:97`).
- Polecat manager uses per-polecat and pool locks to prevent duplicate allocation (`external/gastown/internal/polecat/manager.go:214`).
- Config resolution is serialized around the global agent registry to avoid concurrent mutation (`external/gastown/internal/config/loader.go:20`).
- Hook/template writes are atomic to avoid partial JSON files during concurrent spawns (`external/gastown/internal/hooks/installer.go:134`).
- Daemon uses an exclusive file lock to prevent multiple town daemons from running (`external/gastown/internal/daemon/daemon.go:435`).
- Refinery merge slots guard target branch pushing and avoid overlapping pushes (`external/gastown/internal/refinery/engineer.go:1988`).
- Daemon starts per-rig heartbeat operations through a bounded worker pool so one slow rig does not block all others (`external/gastown/internal/daemon/daemon.go:120`).

## Failure Modes To Watch

- Dolt server down or wrong backend: daemon blocks or health ticker restarts Dolt; agent env must carry the right port/host (`external/gastown/internal/daemon/daemon.go:1003`, `external/gastown/internal/daemon/daemon.go:1057`).
- Stale lifecycle mail: daemon ignores and deletes stale lifecycle requests before action to avoid repeated execution (`external/gastown/internal/daemon/lifecycle.go:75`, `external/gastown/internal/daemon/lifecycle.go:91`).
- Zombie tmux sessions: Witness/Deacon/Mayor managers treat tmux session existence and agent process liveness separately (`external/gastown/internal/witness/manager.go:45`, `external/gastown/internal/deacon/manager.go:80`, `external/gastown/internal/daemon/daemon.go:1850`).
- Empty refinery queue: daemon avoids spawning new refinery sessions with no pending refinery events to avoid wasting API credits (`external/gastown/internal/daemon/daemon.go:1801`).
- Missing pushed branch: `mq submit` verifies branch availability; refinery failure handling has branch-not-found escalation (`external/gastown/internal/cmd/mq_submit.go:367`, `external/gastown/internal/refinery/engineer.go:1294`).
- Repeated failed MRs: MR scoring penalizes retry count and caps the penalty to reduce thrashing without permanent starvation (`external/gastown/internal/refinery/score.go:28`, `external/gastown/internal/refinery/score.go:117`).

