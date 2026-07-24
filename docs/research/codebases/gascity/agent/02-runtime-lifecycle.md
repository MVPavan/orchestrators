# Runtime Lifecycle

## Main Entry Points

`cmd/gc/main.go` is the binary entry. `main` passes CLI args to `run`, and `run` initializes telemetry, builds the root command, handles special JSON/schema shortcuts, then executes Cobra (`external/agent-systems/gascity/cmd/gc/main.go:30`, `external/agent-systems/gascity/cmd/gc/main.go:194`). `newRootCmd` wires persistent `--city` and `--rig` flags and registers city lifecycle, supervisor, sessions, sling, orders, formulas, convergence, beads, events, hooks, config, pack, and service commands (`external/agent-systems/gascity/cmd/gc/main.go:207`, `external/agent-systems/gascity/cmd/gc/main.go:299`).

The normal long-running path is `gc start`, which starts a city under the machine-wide supervisor. The command still has foreground/controller compatibility flags, but its primary behavior is supervisor registration and reconciliation (`external/agent-systems/gascity/cmd/gc/cmd_start.go:366`, `external/agent-systems/gascity/cmd/gc/cmd_start.go:413`).

## Startup Sequence

### `gc start` Supervisor-Managed Path

1. Resolve the target city directory and ensure it is bootstrapped (`external/agent-systems/gascity/cmd/gc/cmd_start.go:472`, `external/agent-systems/gascity/cmd/gc/cmd_start.go:506`).
2. Run pre-start checks: scaffold/dependency/Dolt identity checks and bootstrapped-city validation (`external/agent-systems/gascity/cmd/gc/cmd_start.go:506`, `external/agent-systems/gascity/cmd/gc/cmd_start.go:541`).
3. Register the city with the machine supervisor and report that it is supervisor-managed (`external/agent-systems/gascity/cmd/gc/cmd_start.go:541`, `external/agent-systems/gascity/cmd/gc/cmd_start.go:563`).
4. In foreground/controller mode, `doStart` instead loads config, validates rigs/services, opens stores and event recorders, creates the session provider, builds desired-state closures, and calls `runController` (`external/agent-systems/gascity/cmd/gc/cmd_start.go:593`, `external/agent-systems/gascity/cmd/gc/cmd_start.go:831`).

### Machine Supervisor Startup

1. `gc supervisor run` rejects an already-running supervisor, creates the supervisor home/log tee, acquires the instance lock, and classifies the previous exit (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1142`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1194`).
2. It creates supervisor context, shutdown controller, registry, and supervisor-level event recorder (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1196`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1207`).
3. It loads supervisor config, registry entries, service cleanup, and constructs the typed API mux (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1230`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1257`).
4. It starts the TCP API listener and the local supervisor control socket (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1277`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1310`).
5. The main loop runs an initial reconcile, then reacts to patrol ticks, explicit reconcile requests, and shutdown (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1337`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1447`).

### Supervisor City Reconciliation

For each registered city missing from the live map, `reconcileCities`:

1. Applies crash-loop and init-failure backoff (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1620`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1748`).
2. Auto-unregisters repeatedly absent city directories after thresholded retries (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1642`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1678`).
3. Loads city config with provenance, applies the registry name as authoritative runtime identity, and tracks initialization status for the API (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1757`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1784`).
4. Runs critical city preparation, creates the configured session provider, checks agent images, and opens `.gc/events.jsonl` (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1786`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1883`).
5. Builds a `CityRuntime` with config watch targets, config revision, session provider, drain ops, build closures, event recorder/provider, poke/reload/convergence/control channels, stores, and service/runtime state (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1885`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1915`).

## City Runtime Loop

`CityRuntime` is the per-city in-process controller. Its struct carries city identity, config, provider, desired-state builders, drain/crash/idle/wisp/order dispatch trackers, events, controller stores, service manager, reload/poke/convergence channels, and shutdown controls (`external/agent-systems/gascity/cmd/gc/city_runtime.go:51`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:131`).

`CityRuntime.run` starts config watching, provider tracking, permission checks, store setup, telemetry, drain/provider health gates, startup watchdogs, initial session cleanup/sync/reconcile, convergence startup reconcile, and then marks the city ready (`external/agent-systems/gascity/cmd/gc/city_runtime.go:345`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:619`). After startup, the loop reacts to patrol ticks, pokes, nudges, reload requests, control dispatch, and convergence requests (`external/agent-systems/gascity/cmd/gc/city_runtime.go:623`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:720`).

The central tick performs these phases:

1. Handle dirty config and manual reload state. Failed reload keeps the old config (`external/agent-systems/gascity/cmd/gc/city_runtime.go:952`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1012`; `external/agent-systems/gascity/cmd/gc/city_runtime.go:1597`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1663`).
2. Skip heavy reconciliation under filesystem pressure unless config changed, while still draining convergence requests (`external/agent-systems/gascity/cmd/gc/city_runtime.go:1017`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1024`).
3. Run managed-Dolt preflight, then dispatch due orders before expensive session reconciliation so order-triggered formulas are not starved (`external/agent-systems/gascity/cmd/gc/city_runtime.go:1033`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1046`).
4. Load session snapshots, clean dead runtime corpses, reap runtimes bound to closed beads, sweep process-table orphans, reap stale session beads, and optionally reap closed bead worktrees (`external/agent-systems/gascity/cmd/gc/city_runtime.go:1051`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1094`).
5. Load demand, refresh desired state with session beads, sync beads/index, refresh snapshots, re-point external-message bindings, and refresh desired state again (`external/agent-systems/gascity/cmd/gc/city_runtime.go:1127`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1175`).
6. Run bead-driven session reconciliation (`external/agent-systems/gascity/cmd/gc/city_runtime.go:1187`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1191`).
7. Run wisp GC, workspace service tick, chat auto-suspend, queued convergence requests, and convergence tick (`external/agent-systems/gascity/cmd/gc/city_runtime.go:1194`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:1238`).

## Desired State And Demand

`DesiredStateResult` carries desired session state plus scale-check counts, partial-query flags, assigned-work snapshots, named-session demand, and store/session partial indicators (`external/agent-systems/gascity/cmd/gc/build_desired_state.go:28`, `external/agent-systems/gascity/cmd/gc/build_desired_state.go:69`). This is important because a failed store query must not cause the reconciler to falsely drain live sessions (`external/agent-systems/gascity/cmd/gc/build_desired_state.go:58`, `external/agent-systems/gascity/cmd/gc/build_desired_state.go:67`).

`buildDesiredState` loads session beads if a store exists, then builds desired state from config, runtime provider, stores, rigs, scale checks, assigned work, and session snapshot (`external/agent-systems/gascity/cmd/gc/build_desired_state.go:394`, `external/agent-systems/gascity/cmd/gc/build_desired_state.go:430`). Pool scale checks are concurrency-limited to avoid stampeding shared stores (`external/agent-systems/gascity/cmd/gc/build_desired_state.go:296`, `external/agent-systems/gascity/cmd/gc/build_desired_state.go:368`).

`CityRuntime.loadDemandSnapshot` caches demand on stable patrol ticks when demand sources are event-backed and the session fingerprint has not changed. It recomputes on config changes, non-patrol triggers, fingerprint changes, or max age (`external/agent-systems/gascity/cmd/gc/city_runtime.go:2875`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:2945`).

## Session Lifecycle

Session state is durable first. Creating an active session writes a `type=session` bead with template, state, provider, work dir, command, resume data, generation, continuation epoch, and instance token, then starts the provider (`external/agent-systems/gascity/internal/session/manager.go:417`, `external/agent-systems/gascity/internal/session/manager.go:556`). Deferred creation writes `state=start-pending` with `pending_create_claim` and lets the controller start it later (`external/agent-systems/gascity/internal/session/manager.go:625`, `external/agent-systems/gascity/internal/session/manager.go:724`).

`session.Manager.Start` ensures a session runtime is live without sending a message (`external/agent-systems/gascity/internal/session/chat.go:745`, `external/agent-systems/gascity/internal/session/chat.go:755`). `Submit` handles default, follow-up, and interrupt-now intent, including deferred queueing for start-pending/creating sessions and hard-restart fallback for some interrupt paths (`external/agent-systems/gascity/internal/session/submit.go:83`, `external/agent-systems/gascity/internal/session/submit.go:135`; `external/agent-systems/gascity/internal/session/submit.go:144`, `external/agent-systems/gascity/internal/session/submit.go:194`).

`worker.Handle` wraps that manager and exposes lifecycle/messaging state to CLI/API code. `Start`, `Create`, `Stop`, `Kill`, `CloseDetailed`, `Message`, `Interrupt`, and `Nudge` all route through the handle rather than direct session-manager calls (`external/agent-systems/gascity/internal/worker/handle_lifecycle.go:12`, `external/agent-systems/gascity/internal/worker/handle_lifecycle.go:179`; `external/agent-systems/gascity/internal/worker/handle_lifecycle.go:254`, `external/agent-systems/gascity/internal/worker/handle_lifecycle.go:310`).

## Session Reconciliation

`session_reconciler.go` describes itself as a bead-driven wake/sleep loop with no dependency on hardcoded agent types (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:1`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:9`). The reconciler:

1. Loads a per-tick provider-health snapshot, builds dependency maps, heals expired timers, and retires duplicate configured named-session beads (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:920`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:1005`).
2. Topologically orders sessions by template dependencies (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:1009`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:1014`).
3. Restores and updates session circuit-breaker state using reset generation and progress signatures (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:1016`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:1067`).
4. Rolls back stale pending-create beads with a per-tick cap so rollback storms do not starve new starts (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:1078`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:1111`).
5. Handles undesired sessions by preserving configured named sessions, closing failed creates, draining live orphans only when store queries are complete, or closing non-running orphans (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:1142`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:1405`).
6. Observes desired-session liveness, records zombie crash output, handles pending-create mismatch/expiry, processes drain-ack and restart-requested paths, and avoids destructive actions when attachment, assigned-work, or provider-health checks are uncertain (`external/agent-systems/gascity/cmd/gc/session_reconciler.go:1409`, `external/agent-systems/gascity/cmd/gc/session_reconciler.go:1749`).

Starts are prepared and executed with bounded parallelism. `executePreparedStartWaveForCity` runs prepared starts with a semaphore, startup timeout, panic recovery, stale session-key detection, and explicit outcomes such as `deadline_exceeded`, `session_initializing`, `session_exists`, and `provider_error` (`external/agent-systems/gascity/cmd/gc/session_lifecycle_parallel.go:1030`, `external/agent-systems/gascity/cmd/gc/session_lifecycle_parallel.go:1212`).

## Provider Startup

The tmux provider stages overlays/files, injects runtime hints, creates a fresh tmux session, handles stale sessions, accepts startup dialogs, waits for readiness hints, verifies liveness, runs setup commands, sends startup nudges, and runs live commands (`external/agent-systems/gascity/internal/runtime/tmux/adapter.go:64`, `external/agent-systems/gascity/internal/runtime/tmux/adapter.go:95`; `external/agent-systems/gascity/internal/runtime/tmux/adapter.go:979`, `external/agent-systems/gascity/internal/runtime/tmux/adapter.go:1105`). `pre_start` failures are fatal because they can leave agents in the wrong work directory or bootstrap state, while setup/live command failures are warnings (`external/agent-systems/gascity/internal/runtime/tmux/adapter.go:1107`, `external/agent-systems/gascity/internal/runtime/tmux/adapter.go:1175`).

Other providers preserve the same interface with different guarantees. Subprocess sessions are detached child processes with socket-based control and no interactive attach or startup hints (`external/agent-systems/gascity/internal/runtime/subprocess/subprocess.go:1`, `external/agent-systems/gascity/internal/runtime/subprocess/subprocess.go:17`). ACP sessions spawn an Agent Client Protocol process and complete JSON-RPC handshake (`external/agent-systems/gascity/internal/runtime/acp/acp.go:59`, `external/agent-systems/gascity/internal/runtime/acp/acp.go:109`). Composite providers route by transport or session name (`external/agent-systems/gascity/internal/runtime/auto/auto.go:1`, `external/agent-systems/gascity/internal/runtime/auto/auto.go:99`; `external/agent-systems/gascity/internal/runtime/hybrid/hybrid.go:1`, `external/agent-systems/gascity/internal/runtime/hybrid/hybrid.go:43`).

## Orders Lifecycle

Orders are scanned from flat `orders/<name>.toml` files and validated after layering (`external/agent-systems/gascity/internal/orders/discovery.go:13`, `external/agent-systems/gascity/internal/orders/discovery.go:61`). An order dispatches either a formula or an exec command, with trigger types cooldown, cron, condition, event, or manual (`external/agent-systems/gascity/internal/orders/order.go:15`, `external/agent-systems/gascity/internal/orders/order.go:68`).

`buildOrderDispatcher` scans city and rig orders, filters disabled/manual entries, extracts an event provider from the recorder, and returns a memory dispatcher (`external/agent-systems/gascity/cmd/gc/order_dispatch.go:309`, `external/agent-systems/gascity/cmd/gc/order_dispatch.go:415`). Each dispatch tick skips suspended cities/rigs, opens scoped stores, gates on open tracking/work, evaluates triggers, creates a tracking bead before launching dispatch, and launches bounded goroutines whose tracking outcomes are drained during reload/shutdown (`external/agent-systems/gascity/cmd/gc/order_dispatch.go:417`, `external/agent-systems/gascity/cmd/gc/order_dispatch.go:633`; `external/agent-systems/gascity/cmd/gc/order_dispatch.go:636`, `external/agent-systems/gascity/cmd/gc/order_dispatch.go:721`).

## Shutdown

Supervisor shutdown cancels managed city contexts, stops all managed cities, optionally preserves sessions, and writes shutdown markers (`external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1367`, `external/agent-systems/gascity/cmd/gc/cmd_supervisor.go:1447`). A city runtime shutdown waits for async starts/stops, closes trace/service state, optionally preserves sessions for supervisor re-adoption, drains order dispatchers, lists running sessions, marks sleep reasons, and performs graceful or forced stop (`external/agent-systems/gascity/cmd/gc/city_runtime.go:3097`, `external/agent-systems/gascity/cmd/gc/city_runtime.go:3168`).
