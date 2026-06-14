# Operational Model

## Build And Test

Gastown is a Go module:

- module: `github.com/steveyegge/gastown` (`external/gastown/go.mod:1`)
- declared Go version: `1.26.2` (`external/gastown/go.mod:3`)
- key dependencies: Cobra, Beads, Dolt, tmux-adjacent subprocess code, Testcontainers, OpenTelemetry (`external/gastown/go.mod:17`, `external/gastown/go.mod:18`, `external/gastown/go.mod:20`, `external/gastown/go.mod:22`).

Main Make targets:

- `make build`: builds `gt-proxy-server`, `gt-proxy-client`, and `gt` (`external/gastown/Makefile:35`).
- `make test`: runs `test-makefile` then `go test ./...` (`external/gastown/Makefile:182`).
- `make test-e2e-container`: runs Docker-based e2e tests; comments say container is the only supported e2e path (`external/gastown/Makefile:188`).
- `make install`: builds, installs to `~/.local/bin`, removes stale binaries, restarts daemon when running, and syncs plugins (`external/gastown/Makefile:102`, `external/gastown/Makefile:115`, `external/gastown/Makefile:125`).
- `make safe-install`: replaces the binary without restarting daemon or killing sessions (`external/gastown/Makefile:130`).

From the parent `orchestrators` repo, treat these commands as submodule operations. Do not run install/restart targets casually from parent analysis work because they may mutate `~/.local/bin`, daemon sessions, and runtime plugin dirs.

## Local Run Model

Nominal runtime setup:

1. Build/install `gt`.
2. `gt install <town>` creates the town/HQ (`external/gastown/internal/cmd/install.go:50`).
3. `gt rig add <name> <git-url>` creates a rig container (`external/gastown/internal/cmd/rig.go:53`).
4. `gt rig boot <rig>` or daemon patrol starts witness/refinery for the rig (`external/gastown/internal/cmd/rig.go:147`, `external/gastown/internal/daemon/daemon.go:1697`, `external/gastown/internal/daemon/daemon.go:1774`).
5. `gt sling <bead> <target>` dispatches work (`external/gastown/internal/cmd/sling.go:25`).
6. Polecat runs work, calls `gt done`, and refinery merges (`external/gastown/internal/cmd/done.go:30`, `external/gastown/internal/refinery/engineer.go:499`).

The actual long-running work happens in tmux sessions. Managers create sessions using initial commands plus environment variables so child agent processes inherit the correct Beads/Dolt/identity context from process start (`external/gastown/internal/deacon/manager.go:125`, `external/gastown/internal/witness/manager.go:190`, `external/gastown/internal/refinery/manager.go:209`).

## Inspection And Diagnostics

Useful diagnostic surfaces:

- `gt doctor`: workspace diagnostic command (`external/gastown/internal/cmd/doctor.go:23`).
- `gt health`: data-plane health report (`external/gastown/internal/cmd/health.go:86`).
- `gt rig status [rig]`: detailed rig and worker status (`external/gastown/internal/cmd/rig.go:228`).
- `gt quota status/scan/rotate/watch`: account quota management and rate-limit response (`external/gastown/internal/cmd/quota.go:37`).
- `gt estop` / `gt thaw`: emergency freeze and resume (`external/gastown/internal/cmd/estop.go:28`, `external/gastown/internal/cmd/estop.go:88`).
- `gt seance`: session discovery and predecessor conversation (`external/gastown/README.md:106`, `external/gastown/internal/cmd/seance.go:34`).
- Beads commands such as `bd show`, `bd list`, and Gas Town `gt mail`, `gt hook`, `gt nudge` for work/message state (`external/gastown/docs/design/architecture.md:188`, `external/gastown/AGENTS.md:76`).

Runtime files to inspect:

- town: `mayor/town.json`, `mayor/rigs.json`, `mayor/daemon.json`, `settings/config.json`, `.beads/routes.jsonl`, `.dolt-data/`.
- rig: `<rig>/config.json`, `<rig>/mayor/rig/.beads`, `<rig>/refinery/rig`, `<rig>/witness`, `<rig>/polecats`, `<rig>/crew`.
- daemon: `daemon/daemon.lock`, PID/state files, Dolt state/logs, rotating daemon log (`external/gastown/docs/design/architecture.md:94`, `external/gastown/internal/daemon/daemon.go:217`).

## Operational Invariants

- Dolt backend is required for daemon-managed operation; daemon startup blocks non-Dolt Beads DBs (`external/gastown/internal/daemon/daemon.go:1057`).
- One daemon per town; daemon uses an exclusive file lock (`external/gastown/internal/daemon/daemon.go:435`).
- Worktrees share canonical Beads by redirect; they should not become independent Beads stores (`external/gastown/docs/design/architecture.md:193`).
- Root context files are intentionally minimal. Architecture docs state only town-root `CLAUDE.md` exists on disk; full context is injected by `gt prime` via hooks (`external/gastown/docs/design/architecture.md:131`).
- Polecats and refinery are worktrees; crew are full clones (`external/gastown/docs/design/architecture.md:135`, `external/gastown/docs/design/architecture.md:145`).
- The hook/assignment principle is core: agents that find work on their hook should run it (`external/gastown/docs/overview.md:180`).
- Daemon is recovery-focused and feed/event mechanisms are supposed to handle normal wakeups (`external/gastown/internal/daemon/daemon.go:48`, `external/gastown/internal/daemon/daemon.go:485`).

## Parent Repo / Submodule Caveats

For this `orchestrators` repo:

- `external/gastown` is an external codebase. Do not edit its internals unless the user explicitly asks to patch Gastown itself.
- Reports should live under `docs/research/codebases/gastown/`, not in the Gastown submodule.
- To update Gastown later, use normal submodule/origin sync procedures from the parent repo and then refresh these reports if architecture-relevant files changed.
- Avoid running `make install`, daemon start/stop, or `gt install` from analysis tasks unless the user explicitly wants to exercise Gastown; those commands can alter user-level runtime state.
- Running `go test ./...` inside the submodule is source-level verification, but it may require Go 1.26.2, Dolt/Beads/tmux, Docker for e2e paths, and local environment setup.

## What Not To Over-Index On

- The web/TUI layers are useful for observing state but do not define the core orchestration state model.
- Visual themes and command-line presentation helpers are not the architecture.
- Release packaging and Homebrew/npm details matter for distribution, not for understanding dispatch, state, or merge lifecycle.
- Individual plugin implementation details are less important than the plugin sync/execution boundary unless debugging a specific plugin.

