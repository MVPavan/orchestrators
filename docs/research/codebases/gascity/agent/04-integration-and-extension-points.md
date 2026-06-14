# Integration And Extension Points

## CLI Surface

The `gc` binary is the broadest integration point. The root command wires city lifecycle (`start`, `stop`, `reload`, `status`), sessions, agents, runtime events, orders, config, packs, hooks, sling, beads, supervisor, convergence, formulas, services, and diagnostics (`external/gascity/cmd/gc/main.go:207`, `external/gascity/cmd/gc/main.go:299`).

The architecture spec draws a specific boundary: the CLI calls core packages directly unless a local supervisor is running and mutation lock coordination requires routing through the local HTTP API/client (`external/gascity/specs/architecture.md:61`, `external/gascity/specs/architecture.md:81`). This means CLI behavior can be either direct local-store mutation or supervisor-coordinated mutation depending on runtime state.

## HTTP And SSE API

The API is a typed Huma projection. The architecture spec says endpoints are registered through Huma from annotated Go input/output types and the OpenAPI 3.1 spec is generated from those registrations (`external/gascity/specs/architecture.md:83`, `external/gascity/specs/architecture.md:87`; `external/gascity/specs/architecture.md:139`, `external/gascity/specs/architecture.md:154`).

`SupervisorMux` owns a single API with supervisor-scope routes and per-city `/v0/city/{cityName}/...` routes. It explicitly calls out the workspace-service proxy as a non-Huma route under `/v0/city/{cityName}/svc/` (`external/gascity/internal/api/supervisor.go:93`, `external/gascity/internal/api/supervisor.go:106`). Middleware includes logging, recovery, request ID, host/CORS, read-only mode, and CSRF enforcement around mutation paths (`external/gascity/internal/api/supervisor.go:191`, `external/gascity/internal/api/supervisor.go:209`).

The dashboard is a browser projection over the supervisor API, not a proxying API server. The architecture spec says the static TypeScript SPA talks directly to supervisor OpenAPI endpoints, while `/__client-log` is a narrow debug endpoint outside the typed control plane (`external/gascity/specs/architecture.md:121`, `external/gascity/specs/architecture.md:132`).

## Runtime Providers

Runtime provider selection starts from config and environment. `newSessionProviderByName` supports `exec:<script>`, fake, fail, subprocess, ACP, t3bridge, Cloudflare, K8s, hybrid, and default tmux paths (`external/gascity/cmd/gc/providers.go:111`, `external/gascity/cmd/gc/providers.go:162`). The session config default provider is `tmux` unless overridden (`external/gascity/internal/config/config.go:1360`, `external/gascity/internal/config/config.go:1409`).

Provider extension contract:

- Implement `runtime.Provider` for lifecycle, liveness, attach, nudge, metadata, peek, list, activity, file copy, key send, and live command reapply (`external/gascity/internal/runtime/runtime.go:99`, `external/gascity/internal/runtime/runtime.go:200`).
- Implement optional interfaces for pending interactions, idle wait, dialog dismissal, transport support, immediate nudge, interrupted-turn reset, process-table scanning, and server lifecycle as needed (`external/gascity/internal/runtime/runtime.go:221`, `external/gascity/internal/runtime/runtime.go:260`).
- Expose provider-specific config through `[providers]`, agent provider refs, or agent `start_command` escape hatches. Resolution runs through `ResolveProvider` (`external/gascity/internal/config/resolve.go:22`, `external/gascity/internal/config/resolve.go:123`).

## Beads Store Providers

Beads storage is configurable through `[beads]`. Defaults point to `bd`, but `file` and `exec:<script>` are also explicit provider options (`external/gascity/internal/config/config.go:1228`, `external/gascity/internal/config/config.go:1255`). `OpenStoreAtForCity` is the integration seam where a configured store becomes a concrete file/native/bd/exec implementation (`external/gascity/internal/beads/factory.go:52`, `external/gascity/internal/beads/factory.go:174`).

External integration risks:

- `bd` and Dolt are external process/service dependencies in the default path (`external/gascity/README.md:59`, `external/gascity/README.md:67`).
- File store avoids Dolt/bd/flock but changes durability and cross-process characteristics (`external/gascity/internal/beads/filestore.go:55`, `external/gascity/internal/beads/filestore.go:228`).
- Native Dolt and DoltLite hot-read paths are build/preflight dependent, not simply config-string dependent (`external/gascity/internal/beads/native_dolt_store.go:148`, `external/gascity/internal/beads/native_dolt_store.go:200`).

## Config, Packs, Agents, And Rigs

The config model is the main extension mechanism. It supports agents, named sessions, rigs, provider catalogs, packs/imports, patches, hooks/scripts, service definitions, formulas, orders, chat/convergence/doctor/maintenance, and GitHub settings (`external/gascity/internal/config/config.go:163`, `external/gascity/internal/config/config.go:280`).

Agent definitions are rich enough to describe runtime directory, work dir, scope, suspension, pre-start commands, prompt template, nudge, session overrides, provider, start command, lifecycle, args, prompt mode, ready hints, process names, environment, option defaults, and pool bounds (`external/gascity/internal/config/config.go:2813`, `external/gascity/internal/config/config.go:2910`). `ValidateAgents` checks missing/invalid identities, duplicates, enums, pool bounds, and dependency cycles (`external/gascity/internal/config/config.go:4287`, `external/gascity/internal/config/config.go:4373`). Rigs are separately validated for missing fields, duplicate names, and prefix collisions (`external/gascity/internal/config/config.go:4566`, `external/gascity/internal/config/config.go:4601`).

Packs extend city config by resolving pack references, stamping pack metadata, and appending agents, named sessions, formulas, skills, and order layers (`external/gascity/internal/config/pack.go:85`, `external/gascity/internal/config/pack.go:220`).

## Formulas, Molecules, And Sling

Formula files are workflow templates with vars, steps, inheritance, composition, advice, aspects, phase, pour, source, and content hashes (`external/gascity/internal/formula/types.go:63`, `external/gascity/internal/formula/types.go:132`). The compiler is a staged extension engine: load by name, resolve inheritance, apply control flow, advice, inline expansions, compose expansions, aspects, condition filters, standalone expansion handling, retries, Ralph, graph controls, and recipe flattening (`external/gascity/internal/formula/compile.go:15`, `external/gascity/internal/formula/compile.go:208`).

Molecules instantiate formulas as durable bead graphs. `Cook` compiles and instantiates; `Attach` can graft a compiled sub-DAG under an existing workflow bead with idempotency and epoch fencing (`external/gascity/internal/molecule/molecule.go:131`, `external/gascity/internal/molecule/molecule.go:145`; `external/gascity/internal/molecule/molecule.go:204`, `external/gascity/internal/molecule/molecule.go:224`).

Sling is the work-routing intent API. Its dependencies are narrow interfaces: agent resolver, branch resolver, notifier, bead router, source workflow stores, and direct-session resolver (`external/gascity/internal/sling/sling.go:71`, `external/gascity/internal/sling/sling.go:137`). It exposes intent-style methods for route bead, launch formula, attach formula, and expand convoy (`external/gascity/internal/sling/sling.go:239`, `external/gascity/internal/sling/sling.go:305`).

## Orders

Orders extend orchestration by mapping triggers to formula or exec dispatch. The order model supports formula or exec, scope, trigger, interval, cron schedule, condition check, event selector, pool, timeout, enabled flag, idempotence, environment, source, formula layer, and rig (`external/gascity/internal/orders/order.go:15`, `external/gascity/internal/orders/order.go:77`). Trigger evaluation supports cooldown, cron with catch-up, condition subprocess, event cursor, and manual-only routes (`external/gascity/internal/orders/triggers.go:50`, `external/gascity/internal/orders/triggers.go:258`).

The runtime dispatcher creates tracking beads and launches dispatch goroutines. This makes orders durable enough to avoid immediate refires and to recover from reload/shutdown races (`external/gascity/cmd/gc/order_dispatch.go:611`, `external/gascity/cmd/gc/order_dispatch.go:721`).

## Events And External Messaging

Events integrate with logs, CLI/API event streams, order event triggers, and supervisor aggregation. The `KnownEventTypes` registry is intended to be payload-complete for SSE projection; one provider-health event is explicitly omitted pending full SSE payload registration (`external/gascity/internal/events/events.go:170`, `external/gascity/internal/events/events.go:209`). `Multiplexer` merges city event providers with per-city tags for supervisor-wide reads/streams (`external/gascity/internal/events/multiplexer.go:22`, `external/gascity/internal/events/multiplexer.go:34`).

External messaging appears as an event and bead-backed domain under `internal/extmsg`; the city runtime reaps stale extmsg bindings after session sync (`external/gascity/cmd/gc/city_runtime.go:1159`, `external/gascity/cmd/gc/city_runtime.go:1163`). This was not deeply traced in this pass.

## Environment Variables That Matter

- `GC_SESSION`: overrides or selects session provider at process startup (`external/gascity/cmd/gc/providers.go:38`, `external/gascity/cmd/gc/providers.go:77`).
- `GC_EVENTS`: overrides the event provider, including `exec:<script>`, fake, fail, or file JSONL (`external/gascity/cmd/gc/providers.go:747`, `external/gascity/cmd/gc/providers.go:808`).
- `GC_BEADS`: selects file-based stores in quickstart/docs, avoiding Dolt/bd/flock (`external/gascity/README.md:65`, `external/gascity/README.md:67`).
- `GC_HOME`: relocates supervisor home and can isolate registry/config/runtime paths (`external/gascity/internal/supervisor/config.go:145`, `external/gascity/internal/supervisor/config.go:192`).
- `XDG_RUNTIME_DIR`: controls default supervisor runtime dir when `GC_HOME` is not isolated (`external/gascity/internal/supervisor/config.go:177`, `external/gascity/internal/supervisor/config.go:192`).
- `GC_ISOLATED=1`: allows non-test sandboxes to seed private supervisor config with an isolated port (`external/gascity/internal/supervisor/config.go:243`, `external/gascity/internal/supervisor/config.go:253`).

## Compatibility And Contract Risks

- API routes should stay typed and Huma-registered. Hand-built JSON or path rewrites are architectural drift (`external/gascity/specs/architecture.md:134`, `external/gascity/specs/architecture.md:170`).
- The worker boundary is active migration work. Upstream guidance says production `cmd/gc` session lifecycle should route through `worker.Handle`, while some API internals still construct `session.Manager` directly (`external/gascity/AGENTS.md:201`, `external/gascity/AGENTS.md:218`).
- Store provider behavior is multi-path. Tests or operators that assume "bd provider" means "always bd CLI" may miss native/fallback paths.
- Config and pack expansion are layered. Changes to pack schema, include order, or provenance can change watcher/reload behavior as well as agent definitions.
- Event logs are not agent transcripts. Consumers that need conversation/tool data must use provider transcript discovery, not only `.gc/events.jsonl`.
