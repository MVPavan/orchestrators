# Operational Model

## Build And Install

Gas City is a Go project. `make build` compiles `./cmd/gc` into `bin/gc` with version metadata, and `make install` installs it into the Go bin directory (`external/gascity/Makefile:69`, `external/gascity/Makefile:96`). The README also documents Homebrew install and source build, with Go and ICU requirements for the source path (`external/gascity/README.md:75`, `external/gascity/README.md:88`).

Useful first commands from the upstream README:

- Install/build: `make install` (`external/gascity/README.md:82`, `external/gascity/README.md:88`).
- Initialize and start a city: `gc init`, `gc start` (`external/gascity/README.md:89`, `external/gascity/README.md:91`).
- Add a rig and create work: `gc rig add`, `bd create`, `gc session attach mayor` in the quickstart example (`external/gascity/README.md:93`, `external/gascity/README.md:100`).

## Dependencies

The README lists tmux, git, jq, pgrep, lsof as always-required, with Dolt, bd, and flock required for the default `bd` beads provider; `gh` and provider CLIs are optional/per-provider (`external/gascity/README.md:47`, `external/gascity/README.md:67`). The same section notes `GC_BEADS=file` or `[beads] provider = "file"` as a no-Dolt/no-bd/no-flock path (`external/gascity/README.md:65`, `external/gascity/README.md:67`).

Operationally, this means local smoke work can often use fake/file providers, but realistic controller/store behavior depends on tmux and the configured bead/provider stack.

## Supervisor Operation

Default supervisor config lives in `GC_HOME` or the built-in `.gc` home; default bind is `127.0.0.1`, default port is `8372`, and default patrol interval is `10s` (`external/gascity/internal/supervisor/config.go:58`, `external/gascity/internal/supervisor/config.go:85`). Runtime lock/socket files use isolated `GC_HOME` or `$XDG_RUNTIME_DIR/gc` (`external/gascity/internal/supervisor/config.go:177`, `external/gascity/internal/supervisor/config.go:192`).

`gc supervisor run` starts the API listener, control socket, registry reconciliation, and per-city runtime loops (`external/gascity/cmd/gc/cmd_supervisor.go:1277`, `external/gascity/cmd/gc/cmd_supervisor.go:1447`). `gc start` normally registers the city with that machine supervisor rather than owning the long-running control loop itself (`external/gascity/cmd/gc/cmd_start.go:472`, `external/gascity/cmd/gc/cmd_start.go:563`).

## Logs And Diagnostics

- Per-city infrastructure events: `<city>/.gc/events.jsonl`, opened by the supervisor city startup (`external/gascity/cmd/gc/cmd_supervisor.go:1876`, `external/gascity/cmd/gc/cmd_supervisor.go:1883`).
- Supervisor events: supervisor runtime event log created during supervisor startup (`external/gascity/cmd/gc/cmd_supervisor.go:1196`, `external/gascity/cmd/gc/cmd_supervisor.go:1207`).
- Event logs are best-effort and infrastructure-only; provider session logs hold agent message/tool/thinking observations (`external/gascity/internal/events/events.go:1`, `external/gascity/internal/events/events.go:9`).
- Optional pprof starts when `GC_PPROF=1` in the supervisor API package (`external/gascity/internal/api/supervisor.go:244`, `external/gascity/internal/api/supervisor.go:272`).
- Session reconciliation traces and lifecycle logs are implemented in `cmd/gc/session_reconciler_trace_*` and lifecycle parallel code; use them when debugging wake/sleep churn rather than guessing from process lists alone.

## Test Strategy

The upstream testing doc defines three tiers:

- Unit tests next to code for internal behavior, edge cases, failure injection, and concurrency (`external/gascity/TESTING.md:5`, `external/gascity/TESTING.md:30`).
- Testscript `.txtar` tests for user-visible CLI behavior with fake defaults (`external/gascity/TESTING.md:128`, `external/gascity/TESTING.md:166`).
- Integration tests with real tmux/filesystem/agent sessions under build tags (`external/gascity/TESTING.md:168`, `external/gascity/TESTING.md:185`).

Default local quality gates:

- `make check`: formatting, lint, vet, routed-test-row guard, and fast tests (`external/gascity/Makefile:111`, `external/gascity/Makefile:119`).
- `make test`: fast unit loop with `GC_FAST_UNIT=1` and scrubbed environment (`external/gascity/Makefile:294`, `external/gascity/Makefile:304`).
- `make test-fast-parallel`: sharded fast suite (`external/gascity/Makefile:307`, `external/gascity/Makefile:310`).
- `make test-cmd-gc-process-parallel`: full `cmd/gc` process shards (`external/gascity/Makefile:338`, `external/gascity/Makefile:350`).
- `make test-integration-huma`: supervisor binary smoke for Huma/OpenAPI/listener/socket wiring (`external/gascity/Makefile:403`, `external/gascity/Makefile:405`; `external/gascity/TESTING.md:186`, `external/gascity/TESTING.md:192`).
- `make test-local-full-parallel`: fast unit, process-backed `cmd/gc`, and integration shards concurrently (`external/gascity/Makefile:414`, `external/gascity/Makefile:416`).

The Makefile strips host environment for tests so live city/session variables do not leak into test binaries. It explicitly excludes `GC_DOLT_PORT` and `BEADS_DOLT_SERVER_PORT` from the allowlist because those can point tests at production Dolt (`external/gascity/Makefile:233`, `external/gascity/Makefile:245`).

## Documentation And Schema Commands

- `make generate`: regenerate JSON schemas and reference docs (`external/gascity/Makefile:98`, `external/gascity/Makefile:100`).
- `make check-schema`: verify generated docs are current (`external/gascity/Makefile:102`, `external/gascity/Makefile:105`).
- `make docs-dev`: run Mintlify docs locally (`external/gascity/Makefile:641`, `external/gascity/Makefile:643`).
- The README points at Mintlify docs rooted in `docs/` and contributor architecture docs in `engdocs/` (`external/gascity/README.md:105`, `external/gascity/README.md:128`).

## Inspecting A Running City

Start with the supervisor and city runtime model:

1. Check registered/running city state through `gc supervisor status`, `gc status`, or the supervisor API. The API is the typed view when the supervisor is active.
2. Inspect `<city>/.gc/events.jsonl` for controller, order, session, bead, and supervisor-city lifecycle facts.
3. Inspect bead stores with `gc beads` or `bd` only after knowing the configured provider and store scope. City and rig stores can both matter.
4. Inspect provider state through `gc session`, `gc runtime`, provider-specific tools, or `worker.Handle` backed commands.
5. For session wake/sleep bugs, trace desired-state inputs, partial-store flags, assigned-work snapshots, provider liveness, and drain-ack/restart markers before changing reconciliation code.

## Parent Repo Caveats

This report was written from the parent `orchestrators` repo. In that repo, `external/gascity` is a submodule. Do not edit submodule internals for parent-level research tasks unless the task is explicitly submodule-local. Parent-level durable artifacts belong under `docs/research/codebases/gascity/`.

Parent repo verification currently focuses on structural checks rather than Gas City tests. Running the upstream Gas City full test suite from the parent repo would be a separate, heavier validation step and may require network/toolchain dependencies not needed for this documentation task.

## Common Failure Modes To Keep In Mind

- Store query partials should hold or defer drains, not trigger destructive cleanup.
- Session provider liveness and process liveness are not always the same; tmux panes and provider wrappers can leave dead artifacts.
- Event logs are not transcripts.
- `bd` provider behavior can use native or fallback implementations.
- Manual reload replies may be sent before expensive later tick phases unless soft reload acceptance needs post-reconcile checks (`external/gascity/cmd/gc/city_runtime.go:993`, `external/gascity/cmd/gc/city_runtime.go:1010`).
- Tests must isolate `GC_HOME`, runtime dir, ports, and process cleanup when booting real supervisors (`external/gascity/TESTING.md:194`, `external/gascity/TESTING.md:235`).
