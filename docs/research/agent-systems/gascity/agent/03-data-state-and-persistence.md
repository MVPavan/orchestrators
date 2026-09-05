# Data, State, And Persistence

## State Map

Gas City uses several state layers:

- City directory: `city.toml`, prompts, formulas, orders, hooks, scripts, and `.gc` runtime/cache/system files. The canonical layout is defined in `internal/citylayout` (`external/agent-systems/gascity/internal/citylayout/layout.go:10`, `external/agent-systems/gascity/internal/citylayout/layout.go:60`).
- Supervisor durable home: `GC_HOME` or the built-in `.gc` home stores `cities.toml`, `supervisor.toml`, and legacy supervisor publications (`external/agent-systems/gascity/internal/supervisor/config.go:145`, `external/agent-systems/gascity/internal/supervisor/config.go:212`).
- Supervisor runtime dir: lock/socket-style ephemeral files live under `$XDG_RUNTIME_DIR/gc` for default homes, or inside isolated `GC_HOME` overrides (`external/agent-systems/gascity/internal/supervisor/config.go:177`, `external/agent-systems/gascity/internal/supervisor/config.go:192`).
- Bead stores: city and rig stores hold work, sessions, mail, molecules, waits, orders, tracking beads, and metadata through the `beads.Store` interface (`external/agent-systems/gascity/internal/beads/beads.go:286`, `external/agent-systems/gascity/internal/beads/beads.go:380`).
- Runtime providers: tmux, subprocess, ACP, K8s, and composite providers hold live process/session state plus provider metadata (`external/agent-systems/gascity/internal/runtime/runtime.go:99`, `external/agent-systems/gascity/internal/runtime/runtime.go:200`).
- Event logs: per-city `.gc/events.jsonl` and supervisor-level event logs record infrastructure events, not full agent transcript content (`external/agent-systems/gascity/internal/events/events.go:1`, `external/agent-systems/gascity/internal/events/events.go:9`).

## Config State

`config.City` is the main structured config object. It covers workspace identity, provider catalogs, imports, defaults, agents, named sessions, rigs, beads, sessions, mail, events, Dolt, formulas, daemon behavior, orders, API, chat sessions, convergence, services, GitHub, and runtime pack/formula fields (`external/agent-systems/gascity/internal/config/config.go:163`, `external/agent-systems/gascity/internal/config/config.go:280`).

`LoadWithIncludes` loads a root `city.toml`, appends CLI/system includes, parses root metadata, handles default rig imports and sibling `pack.toml`, merges city packs, and returns provenance for watchers (`external/agent-systems/gascity/internal/config/compose.go:106`, `external/agent-systems/gascity/internal/config/compose.go:220`). The compose path later validates named sessions, GitHub monitors, durations, bead policy, Dolt config, provider references, semantic warnings, provider cache, asset dirs, and name pools (`external/agent-systems/gascity/internal/config/compose.go:620`, `external/agent-systems/gascity/internal/config/compose.go:690`).

Pack state is flattened before downstream use. `PackConfig` supports agents under `agents/<name>/agent.toml`, inline list migration compatibility, formulas, orders, and skills (`external/agent-systems/gascity/internal/config/pack.go:37`, `external/agent-systems/gascity/internal/config/pack.go:59`). `ExpandPacks` resolves rig and city pack refs, hoists agents/named sessions/formula dirs/skills, and appends them to the city view (`external/agent-systems/gascity/internal/config/pack.go:85`, `external/agent-systems/gascity/internal/config/pack.go:220`).

## Bead Data Model

The `Bead` model is the common durable record. It includes:

- Identity and lifecycle: `ID`, `Title`, `Description`, `Status`, `Type`, `Priority`, `CreatedAt`, `UpdatedAt`, `ClosedAt`.
- Routing and graph structure: `Assignee`, `Labels`, `Metadata`, `Deps`, `ParentID`, `RootID`, `Children`.
- Storage semantics: `Ephemeral`, `NoHistory`, `Defer`, `Blocked`, `Blockers`.

Source: `external/agent-systems/gascity/internal/beads/beads.go:38` through `external/agent-systems/gascity/internal/beads/beads.go:75`.

The `Store` interface deliberately abstracts several backends and exposes both broad CRUD and domain-specific read paths: list with query, ready work, children, labels, assignees, metadata filters, metadata batches, logical transactions, delete, and ping (`external/agent-systems/gascity/internal/beads/beads.go:286`, `external/agent-systems/gascity/internal/beads/beads.go:380`). The comments note partial application risk for external metadata batches, so callers must make batch contents idempotent (`external/agent-systems/gascity/internal/beads/beads.go:361`, `external/agent-systems/gascity/internal/beads/beads.go:367`).

## Bead Store Implementations

`OpenStoreAtForCity` chooses the concrete backend. It supports file stores, exec stores, native Dolt stores after preflight, and `bd` CLI fallback when native is ineligible or failed (`external/agent-systems/gascity/internal/beads/factory.go:52`, `external/agent-systems/gascity/internal/beads/factory.go:174`).

Important implementations:

- `FileStore`: JSON file store with flock, reload-on-lock for cross-process correctness, temp-file/rename writes, write-through mutation, and rollback on save failure (`external/agent-systems/gascity/internal/beads/filestore.go:55`, `external/agent-systems/gascity/internal/beads/filestore.go:228`).
- `BdStore`: shell-based `bd create/show/update/list` path for CLI-compatible storage (`external/agent-systems/gascity/internal/beads/bdstore.go:813`, `external/agent-systems/gascity/internal/beads/bdstore.go:990`; `external/agent-systems/gascity/internal/beads/bdstore.go:1980`, `external/agent-systems/gascity/internal/beads/bdstore.go:2045`).
- `NativeDoltStore`: upstream beads library over Dolt after preflight, implementing store, conditional release, and graph apply (`external/agent-systems/gascity/internal/beads/native_dolt_store.go:148`, `external/agent-systems/gascity/internal/beads/native_dolt_store.go:200`).
- `CachingStore`: live in-memory reads with write-through updates, event-bus-driven external write invalidation, and a watchdog fallback (`external/agent-systems/gascity/internal/beads/caching_store.go:16`, `external/agent-systems/gascity/internal/beads/caching_store.go:154`).

Inference: configured provider is not identical to selected implementation. For example, a `bd` provider may end up using native Dolt or `bd` CLI fallback depending on preflight and options.

## Session Beads And Identity

Sessions are stored as beads of type `session` with `gc:session` label (`external/agent-systems/gascity/internal/session/manager.go:62`, `external/agent-systems/gascity/internal/session/manager.go:67`). Session info is derived from bead metadata plus runtime observation (`external/agent-systems/gascity/internal/session/manager.go:72`, `external/agent-systems/gascity/internal/session/manager.go:109`).

Immediate creation writes active state and starts the provider. The metadata includes template, state, provider, work dir, command, resume fields, generation, continuation epoch, and instance token (`external/agent-systems/gascity/internal/session/manager.go:417`, `external/agent-systems/gascity/internal/session/manager.go:460`). Deferred creation writes `state=start-pending`, `pending_create_claim=true`, and `pending_create_started_at`, then returns for controller reconciliation (`external/agent-systems/gascity/internal/session/manager.go:625`, `external/agent-systems/gascity/internal/session/manager.go:724`).

Live runtime environment is a separate identity projection. `RuntimeEnv` injects `GC_SESSION_ID`, `GC_SESSION_NAME`, `GC_RUNTIME_EPOCH`, `GC_CONTINUATION_EPOCH`, and `GC_INSTANCE_TOKEN`; alias/session context variants add `GC_ALIAS`, `GC_TEMPLATE`, `GC_SESSION_ORIGIN`, and `GC_AGENT` (`external/agent-systems/gascity/internal/session/lifecycle.go:29`, `external/agent-systems/gascity/internal/session/lifecycle.go:67`).

This matters for correctness: runtime processes are matched back to beads through provider metadata such as `GC_SESSION_ID` and instance token (`external/agent-systems/gascity/internal/session/manager.go:604`, `external/agent-systems/gascity/internal/session/manager.go:623`).

## Events

Events are a best-effort infrastructure log. The package comment says JSONL events record agent lifecycle, bead operations, and controller state, while agent observation data is read from provider session logs (`external/agent-systems/gascity/internal/events/events.go:1`, `external/agent-systems/gascity/internal/events/events.go:9`). Event constants include sessions, beads, mail, convoys, controller/supervisor, city lifecycle, orders, worker operations, external messaging, rotations, store maintenance, Postgres credential resolution, and provider health (`external/agent-systems/gascity/internal/events/events.go:18`, `external/agent-systems/gascity/internal/events/events.go:168`).

`FileRecorder` appends JSONL with `O_APPEND`, mutex serialization, and bounded flock so dead writers do not block indefinitely (`external/agent-systems/gascity/internal/events/recorder.go:39`, `external/agent-systems/gascity/internal/events/recorder.go:42`; `external/agent-systems/gascity/internal/events/recorder.go:212`, `external/agent-systems/gascity/internal/events/recorder.go:240`). It reads the latest sequence on open and sweeps orphaned rotation files (`external/agent-systems/gascity/internal/events/recorder.go:147`, `external/agent-systems/gascity/internal/events/recorder.go:192`). `Multiplexer` merges event providers from multiple cities and tags events with their source city (`external/agent-systems/gascity/internal/events/multiplexer.go:22`, `external/agent-systems/gascity/internal/events/multiplexer.go:34`).

## Supervisor Registry

The supervisor registry is TOML-backed and cross-process safe. `Registry.Register` resolves absolute city paths, enforces valid/unique effective names, and uses a file lock before read-modify-write (`external/agent-systems/gascity/internal/supervisor/registry.go:96`, `external/agent-systems/gascity/internal/supervisor/registry.go:151`). Save uses a temp file, fsync, close, and rename (`external/agent-systems/gascity/internal/supervisor/registry.go:320`, `external/agent-systems/gascity/internal/supervisor/registry.go:349`).

Runtime path functions place:

- Registry: `DefaultHome()/cities.toml` (`external/agent-systems/gascity/internal/supervisor/config.go:194`, `external/agent-systems/gascity/internal/supervisor/config.go:197`).
- Supervisor config: `DefaultHome()/supervisor.toml` (`external/agent-systems/gascity/internal/supervisor/config.go:199`, `external/agent-systems/gascity/internal/supervisor/config.go:202`).
- Runtime dir: isolated `GC_HOME` or `$XDG_RUNTIME_DIR/gc` (`external/agent-systems/gascity/internal/supervisor/config.go:177`, `external/agent-systems/gascity/internal/supervisor/config.go:192`).

## Formula, Molecule, And Order State

Formulas are parsed workflow templates with variables, steps, inheritance, composition, advice, aspects, phase, pour mode, source, and content hash (`external/agent-systems/gascity/internal/formula/types.go:63`, `external/agent-systems/gascity/internal/formula/types.go:132`). The compiler returns a `Recipe` after staged transforms and graph validation (`external/agent-systems/gascity/internal/formula/compile.go:15`, `external/agent-systems/gascity/internal/formula/compile.go:208`).

Molecules write recipes into the bead store. `Cook` compiles by name, validates runtime vars, and instantiates (`external/agent-systems/gascity/internal/molecule/molecule.go:131`, `external/agent-systems/gascity/internal/molecule/molecule.go:145`). `Attach` grafts a compiled recipe as a sub-DAG onto an existing workflow bead, with idempotency and expected-epoch fencing (`external/agent-systems/gascity/internal/molecule/molecule.go:204`, `external/agent-systems/gascity/internal/molecule/molecule.go:224`).

Orders are persistent TOML definitions discovered from formula/order layers. Each runtime dispatch creates an `order-tracking` bead before launching work so triggers do not refire immediately (`external/agent-systems/gascity/cmd/gc/order_dispatch.go:611`, `external/agent-systems/gascity/cmd/gc/order_dispatch.go:633`). Tracking beads also drive last-run and open-work gates (`external/agent-systems/gascity/cmd/gc/order_dispatch.go:506`, `external/agent-systems/gascity/cmd/gc/order_dispatch.go:622`).

## Consistency And Failure Notes

- Store query partials are first-class. `DesiredStateResult.StoreQueryPartial` and `SessionQueryPartial` prevent drain decisions from incomplete evidence (`external/agent-systems/gascity/cmd/gc/build_desired_state.go:58`, `external/agent-systems/gascity/cmd/gc/build_desired_state.go:67`).
- File and registry stores use file locks plus atomic rename patterns. Native/bd stores add their own transactional or CLI-level semantics.
- Session start is fenced by pending-create metadata, startup timeout, instance token, generation, and runtime metadata matching.
- Event recording is best-effort and should not be treated as authoritative for agent transcript content.
- Cache invalidation depends on event propagation when external writes occur; the caching store has a watchdog fallback (`external/agent-systems/gascity/internal/beads/caching_store.go:16`, `external/agent-systems/gascity/internal/beads/caching_store.go:27`).

## Data Ownership Summary

- Durable domain truth: Beads stores and `city.toml` plus pack/includes.
- Durable machine truth: supervisor registry/config under `GC_HOME`.
- Live truth: provider process/session state and controller in-memory maps.
- Observation truth: infrastructure events for lifecycle and control facts; provider transcripts for agent conversation facts.
- Derived truth: desired-state snapshots, API response shapes, dashboard views, generated OpenAPI/client files.
