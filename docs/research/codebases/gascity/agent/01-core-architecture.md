# Core Architecture

## Architectural Thesis

Gas City is a configurable orchestration runtime, not a fixed multi-agent application. Its core is a set of domain primitives in `internal/*`: configuration, beads, sessions, runtime providers, events, formulas/molecules, sling routing, and orders. The CLI, supervisor HTTP/SSE API, and dashboard are projections over those primitives (`external/gascity/specs/architecture.md:20`, `external/gascity/specs/architecture.md:25`).

The upstream architectural guide names five primitives: Session, Task Store/Beads, Event Bus, Config, and Prompt Templates, then derives Messaging, Formulas/Molecules, Dispatch/Sling, and Health Patrol from them (`external/gascity/AGENTS.md:102`, `external/gascity/AGENTS.md:133`). Its layering invariants say lower layers should not import upward, Beads is persistence, Events is observation, Config is activation, and side effects are constrained to the side-effect layers (`external/gascity/AGENTS.md:135`, `external/gascity/AGENTS.md:143`).

## Core Modules

`cmd/gc/`

The CLI is both user command surface and controller wiring. `main.run` initializes telemetry, builds the Cobra root, handles schema/contract shortcuts, and executes the command tree (`external/gascity/cmd/gc/main.go:127`, `external/gascity/cmd/gc/main.go:194`). `newRootCmd` registers the broad command surface: city lifecycle, sessions, mail, events, orders, config, packs, hooks, sling, beads, supervisor, convergence, and formulas (`external/gascity/cmd/gc/main.go:207`, `external/gascity/cmd/gc/main.go:299`).

`internal/config/`

Config owns the declarative model. `config.City` includes workspace identity, providers, imports, defaults, agents, named sessions, rigs, beads, session, mail, events, Dolt, formulas, daemon, orders, API, chat sessions, convergence, services, GitHub, and runtime-only formula/pack state (`external/gascity/internal/config/config.go:163`, `external/gascity/internal/config/config.go:280`). `LoadWithIncludes` loads the root `city.toml`, applies includes and pack expansion, and returns provenance for watch targets (`external/gascity/internal/config/compose.go:106`, `external/gascity/internal/config/compose.go:220`). Pack expansion flattens agents, named sessions, formulas, skills, and orders from packs into the city view (`external/gascity/internal/config/pack.go:37`, `external/gascity/internal/config/pack.go:220`).

`internal/beads/`

Beads is the durable work ledger. The `Bead` model carries ID, title, status, type, priority, assignee, labels, metadata, dependencies, parent/root fields, and storage flags (`external/gascity/internal/beads/beads.go:38`, `external/gascity/internal/beads/beads.go:75`). The `Store` interface covers create/get/update/close/reopen/list/ready/children/metadata/transaction/delete/ping, with implementation-specific IDs and transaction behavior (`external/gascity/internal/beads/beads.go:286`, `external/gascity/internal/beads/beads.go:380`). Store opening selects native/file/exec/bd fallback based on provider config and preflight (`external/gascity/internal/beads/factory.go:76`, `external/gascity/internal/beads/factory.go:156`).

`internal/runtime/`

`runtime.Provider` is the provider contract for live process/session control: start, stop, interrupt, attach, liveness, nudge, metadata, peek, list, activity, copy, raw keys, live reconfiguration, and capabilities (`external/gascity/internal/runtime/runtime.go:99`, `external/gascity/internal/runtime/runtime.go:200`). The tmux provider is the production-style interactive backend (`external/gascity/internal/runtime/tmux/adapter.go:24`, `external/gascity/internal/runtime/tmux/adapter.go:69`), while subprocess, ACP, K8s, Cloudflare, t3bridge, hybrid, auto, exec, fake, and fail variants share the same interface family.

`internal/session/`

Session is the durable conversation layer. The package describes chat sessions as bead-backed conversations that can be started, suspended, resumed, and observed through a `runtime.Provider` (`external/gascity/internal/session/manager.go:1`, `external/gascity/internal/session/manager.go:7`). Session states include active, asleep, suspended, start-pending, creating, failed-create, draining, drained, awake, archived, and quarantined (`external/gascity/internal/session/manager.go:25`, `external/gascity/internal/session/manager.go:60`). Runtime identity is injected through `GC_SESSION_ID`, `GC_SESSION_NAME`, runtime epoch, continuation epoch, and instance token (`external/gascity/internal/session/lifecycle.go:29`, `external/gascity/internal/session/lifecycle.go:40`).

`internal/worker/`

`worker.Handle` is the current migration boundary for session-like workers. It combines lifecycle, messaging, transcript, interaction, peeking, and live observation (`external/gascity/internal/worker/handle.go:81`, `external/gascity/internal/worker/handle.go:89`). The factory wraps a `session.Manager` and resolves persisted session beads to session-backed handles or runtime-only handles for legacy live sessions (`external/gascity/internal/worker/factory.go:41`, `external/gascity/internal/worker/factory.go:193`).

`internal/events/`

Events are append-only infrastructure records. The package explicitly distinguishes infrastructure events from provider transcript logs, which remain the source for agent messages/tool calls/thinking (`external/gascity/internal/events/events.go:1`, `external/gascity/internal/events/events.go:9`). `FileRecorder` appends JSONL with mutex, append mode, and bounded flock for cross-process serialization (`external/gascity/internal/events/recorder.go:39`, `external/gascity/internal/events/recorder.go:42`).

`internal/formula/`, `internal/molecule/`, `internal/sling/`, `internal/orders/`

Formulas compile workflow templates through a staged pipeline that loads, resolves inheritance, applies control flow/advice/expansions/aspects/conditions/retries/Ralph/graph controls, then flattens to a recipe (`external/gascity/internal/formula/compile.go:15`, `external/gascity/internal/formula/compile.go:208`). Molecules instantiate compiled recipes into bead graphs and support late-bound DAG attach with idempotency and epoch fencing (`external/gascity/internal/molecule/molecule.go:131`, `external/gascity/internal/molecule/molecule.go:224`). Sling routes beads and formula launches to agents with typed dependencies (`external/gascity/internal/sling/sling.go:42`, `external/gascity/internal/sling/sling.go:137`). Orders define formula or exec dispatch with cooldown/cron/condition/event/manual triggers (`external/gascity/internal/orders/order.go:15`, `external/gascity/internal/orders/order.go:68`).

`internal/api/`

The API is a typed projection over the same object model. The architecture spec says every HTTP/SSE endpoint is Huma-registered from annotated Go types and OpenAPI is generated from the live registration (`external/gascity/specs/architecture.md:83`, `external/gascity/specs/architecture.md:87`). `SupervisorMux` owns one Huma API for supervisor routes plus per-city `/v0/city/{cityName}/...` routes; the workspace service proxy is the notable non-Huma proxy exception (`external/gascity/internal/api/supervisor.go:93`, `external/gascity/internal/api/supervisor.go:106`).

## Ownership Boundaries

- Domain ownership: `internal/{beads, formula, molecule, session, worker, runtime, sling, events, orders}` owns business objects and state transitions (`external/gascity/specs/architecture.md:20`, `external/gascity/specs/architecture.md:25`).
- CLI ownership: `cmd/gc/cmd_*.go` owns argument parsing, text output, exit codes, and local coordination with the supervisor (`external/gascity/specs/architecture.md:61`, `external/gascity/specs/architecture.md:81`).
- API ownership: `internal/api/handler_*.go` owns typed HTTP/SSE inputs/outputs and Huma registration, not independent domain logic (`external/gascity/specs/architecture.md:83`, `external/gascity/specs/architecture.md:87`).
- Config ownership: `internal/config` owns validation and provider/agent resolution. Provider resolution proceeds from agent `start_command`, agent/workspace provider, provider catalog, overrides, and defaults (`external/gascity/internal/config/resolve.go:22`, `external/gascity/internal/config/resolve.go:123`).
- Runtime ownership: provider packages own live process mechanics; session/worker/city runtime code owns when those mechanics are invoked.

## Central Versus Peripheral

Central:

- `cmd/gc/cmd_supervisor.go`, `cmd/gc/city_runtime.go`, `cmd/gc/session_reconciler.go`, `cmd/gc/build_desired_state.go`.
- `internal/config`, `internal/beads`, `internal/session`, `internal/worker`, `internal/runtime`.
- `internal/formula`, `internal/molecule`, `internal/sling`, `internal/orders`, `internal/events`.

Peripheral but architecturally relevant:

- `cmd/gc/dashboard/`: important as a projection and smoke surface, not as core logic (`external/gascity/specs/architecture.md:121`, `external/gascity/specs/architecture.md:132`).
- `docs/`, `engdocs/`, `specs/`: useful for intent and invariants, but implementation wins when docs drift.
- `examples/`, `contrib/`, release scripts, generated API clients: useful operationally, not the control-plane center.

## Key Inference

The current checked-out code has moved beyond a simple "CLI launches tmux sessions" architecture. The more accurate mental model is a bead-backed desired-state engine: config and work demand produce desired session state; `CityRuntime` reconciles that state to runtime providers; Beads carries both work and session lifecycle; events observe infrastructure changes; CLI/API are typed control surfaces over those same objects.
