# Gas City Codebase Research Index

Analysis date: 2026-06-13
Target path: `external/gascity`
Submodule commit: `ec67043b8c9cd5f763ac699e22c6d9f75be6ebb5`

Gas City is a Go orchestration toolkit for configurable multi-agent coding workflows. Its public README describes it as an "orchestration-builder SDK" with runtime providers, work routing, formulas, orders, health patrol, and declarative `city.toml` configuration (`external/gascity/README.md:15`, `external/gascity/README.md:18`). The important implementation thesis is: domain objects live in `internal/*`, while CLI and HTTP/SSE surfaces project those objects outward rather than reimplementing them (`external/gascity/specs/architecture.md:12`, `external/gascity/specs/architecture.md:25`).

## Report Map

- `01-core-architecture.md`: architectural thesis, core modules, ownership boundaries.
- `02-runtime-lifecycle.md`: CLI/supervisor startup, city runtime tick, session reconciliation, shutdown.
- `03-data-state-and-persistence.md`: durable stores, runtime files, session identity, cache and concurrency assumptions.
- `04-integration-and-extension-points.md`: CLI/API/protocols, providers, packs, formulas, hooks, environment controls.
- `05-operational-model.md`: build/run/test/inspect guidance and parent-repo caveats.
- `90-open-questions.md`: unknowns, inferred claims, drift risks, and follow-up reads.

## Core Architecture In 10 Bullets

- The system is intentionally role-free infrastructure. Upstream guidance says user configuration supplies role behavior and Go code should not hardcode roles (`external/gascity/AGENTS.md:3`, `external/gascity/AGENTS.md:9`).
- `cmd/gc` is the CLI and controller/supervisor edge; the root command registers many operational surfaces including `start`, `session`, `sling`, `order`, `formula`, `supervisor`, and `converge` (`external/gascity/cmd/gc/main.go:207`, `external/gascity/cmd/gc/main.go:299`).
- `internal/config` owns `city.toml`, includes, packs, rigs, providers, agents, beads, sessions, events, formulas, orders, services, convergence, and validation (`external/gascity/internal/config/config.go:163`, `external/gascity/internal/config/config.go:280`).
- `internal/beads` is the universal persistence substrate. A bead can represent tasks, mail, molecules, convoys, sessions, and tracking rows (`external/gascity/internal/beads/beads.go:38`, `external/gascity/internal/beads/beads.go:75`).
- `internal/runtime.Provider` is the live-session abstraction for starting, stopping, attaching, observing, nudging, and interacting with agent processes (`external/gascity/internal/runtime/runtime.go:99`, `external/gascity/internal/runtime/runtime.go:200`).
- `internal/session.Manager` bridges durable session beads and runtime providers. It can start immediately or create a `start-pending` bead for controller-owned reconciliation (`external/gascity/internal/session/manager.go:346`, `external/gascity/internal/session/manager.go:631`).
- `internal/worker.Handle` is the current migration boundary for lifecycle, messaging, transcript, interaction, peeking, and live observation operations (`external/gascity/internal/worker/handle.go:81`, `external/gascity/internal/worker/handle.go:89`).
- `internal/formula` compiles workflow templates through a staged pipeline, and `internal/molecule` instantiates compiled recipes as bead graphs (`external/gascity/internal/formula/compile.go:15`, `external/gascity/internal/molecule/molecule.go:1`).
- `internal/sling` routes work intent: bead routing, formula launch, formula attach, convoy expansion, and optional nudging (`external/gascity/internal/sling/sling.go:1`, `external/gascity/internal/sling/sling.go:270`).
- The supervisor and `CityRuntime` reconcile durable desired state to live sessions, orders, services, convergence loops, and shutdown behavior (`external/gascity/cmd/gc/cmd_supervisor.go:1196`, `external/gascity/cmd/gc/city_runtime.go:888`).

## Read Next

- `external/gascity/README.md`: concise project purpose, prerequisites, and top-level repo map (`external/gascity/README.md:15`, `external/gascity/README.md:141`).
- `external/gascity/specs/architecture.md`: normative object-model and typed-wire invariants (`external/gascity/specs/architecture.md:10`, `external/gascity/specs/architecture.md:18`).
- `external/gascity/cmd/gc/main.go`: CLI entry and command registration (`external/gascity/cmd/gc/main.go:127`, `external/gascity/cmd/gc/main.go:299`).
- `external/gascity/cmd/gc/cmd_supervisor.go`: machine-wide supervisor lifecycle and city runtime construction (`external/gascity/cmd/gc/cmd_supervisor.go:1142`, `external/gascity/cmd/gc/cmd_supervisor.go:1915`).
- `external/gascity/cmd/gc/city_runtime.go`: per-city control loop, reload, order dispatch, session snapshots, reconciliation, and shutdown (`external/gascity/cmd/gc/city_runtime.go:888`, `external/gascity/cmd/gc/city_runtime.go:1238`).
- `external/gascity/cmd/gc/build_desired_state.go`: desired-state computation, scale checks, partial-query flags, and assigned-work snapshots (`external/gascity/cmd/gc/build_desired_state.go:28`, `external/gascity/cmd/gc/build_desired_state.go:430`).
- `external/gascity/cmd/gc/session_reconciler.go`: bead-driven wake/sleep reconciliation (`external/gascity/cmd/gc/session_reconciler.go:1`, `external/gascity/cmd/gc/session_reconciler.go:9`).
- `external/gascity/internal/beads/`, `internal/session/`, `internal/runtime/`, `internal/worker/`: the persistence/runtime/session boundary.

## Scope Limits

- This research documents the checked-out submodule at commit `ec67043b8c9cd5f763ac699e22c6d9f75be6ebb5`. It does not claim upstream `main` or released docs are identical.
- The parent repo tracks `external/gascity` as a submodule. This pass did not modify submodule internals.
- UI styling, release automation, generated OpenAPI/client files, and most test matrix details are intentionally de-prioritized unless they explain core behavior.
- Some upstream local-operation notes in `external/gascity/AGENTS.md` are fork-specific. This report uses its architecture invariants but not its parent-repo workflow instructions.

## Do Not Over-Index On

- The dashboard. It is a projection over the supervisor API, not the core control plane (`external/gascity/specs/architecture.md:121`, `external/gascity/specs/architecture.md:132`).
- Examples and tutorials. They are useful for behavior, but the architecture lives in `cmd/gc` and `internal/*`.
- A single configured provider name. `bd` can route through native, CLI, file, and exec-backed paths depending on config and preflight (`external/gascity/internal/beads/factory.go:76`, `external/gascity/internal/beads/factory.go:156`).
- Legacy foreground controller paths. The normal `gc start` path registers with the machine supervisor unless explicit foreground/controller flags are used (`external/gascity/cmd/gc/cmd_start.go:366`, `external/gascity/cmd/gc/cmd_start.go:563`).
