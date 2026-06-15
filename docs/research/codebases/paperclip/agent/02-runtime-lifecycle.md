# Paperclip Runtime Lifecycle

## Server Startup

Startup begins in `startServer()`. The server waits for instrumentation readiness, initializes telemetry, loads configuration, and sets secret-provider environment variables (`external/paperclip/server/src/index.ts:102-116`). It then inspects and applies database migrations, choosing either an external Postgres URL path or an embedded Postgres path (`external/paperclip/server/src/index.ts:151-199`, `external/paperclip/server/src/index.ts:304-323`, `external/paperclip/server/src/index.ts:324-488`).

After database setup, startup validates deployment/exposure, configures local-trusted or Better Auth mode, builds storage/feedback/settings/plugin services, creates the Express app, creates the HTTP server, derives runtime API URL candidates, and attaches live events over WebSocket (`external/paperclip/server/src/index.ts:490-568`, `external/paperclip/server/src/index.ts:577-704`).

The next startup phase is recovery and scheduling. The server reconciles persisted runtime services and cloud upstreams, optionally applies a forced execution policy from environment, resumes queued heartbeats, starts timer/routine/retry/recovery loops, checks graph liveness and output watchdogs, sweeps stale locks, runs productivity review maintenance, starts automatic backups, reconciles configured adapters, then listens (`external/paperclip/server/src/index.ts:706-895`, `external/paperclip/server/src/index.ts:898-993`).

## HTTP Request Lifecycle

`createApp(db, opts)` constructs the HTTP application. It sets trust-proxy behavior, JSON body limits, logger middleware, private hostname guard, actor middleware, and auth routes before mounting the API router (`external/paperclip/server/src/app.ts:129-203`). The router exposes health, OpenAPI, companies, LLMs, skills, teams, agents, assets, projects, issues, issue tree control, file resources, routines, environments, execution workspaces, goals, board chat, approvals, secrets, costs, activity, dashboards, profile/sidebar/resource/inbox/instance settings, and database backups (`external/paperclip/server/src/app.ts:208-252`).

Plugins and adapters are mounted as part of the same API layer. `createApp()` creates plugin registry/event/job/tool/lifecycle/loader services, installs plugin and adapter routes, and mounts `/api` (`external/paperclip/server/src/app.ts:253-322`). UI serving is then layered on top: plugin UI static assets, built UI candidates with SPA fallback, and optional Vite middleware for development (`external/paperclip/server/src/app.ts:336-437`).

## Heartbeat Wakeup Lifecycle

The wakeup path begins in `enqueueWakeup()`. It builds execution context, checks whether the company is active, resolves issue/project context when present, and blocks on budget state (`external/paperclip/server/src/services/heartbeat.ts:10099-10226`). It then checks agent invokability and heartbeat policy, including `wakeOnDemand` behavior (`external/paperclip/server/src/services/heartbeat.ts:10228-10252`). For issue-specific runs, it also enforces tree holds, locks the issue row, cancels stale scheduled retries and stale execution locks, evaluates dependency readiness, handles blocked interactions, coalesces or defers duplicate wakeups, inserts `agent_wakeup_requests` and `heartbeat_runs`, emits a queued event, and starts the next queued run (`external/paperclip/server/src/services/heartbeat.ts:10254-10795`).

The public heartbeat service exposes `wakeup`, `resumeQueuedRuns`, recovery helpers, `tickTimers`, and cancellation functions (`external/paperclip/server/src/services/heartbeat.ts:11420-11535`). `tickTimers` scans active companies and agents to enqueue timer wakeups, which means timers reuse the same durable wakeup/run machinery rather than a separate execution path (`external/paperclip/server/src/services/heartbeat.ts:11420-11535`).

## Run Claim And Execution Lifecycle

Queued run execution is serialized per agent by `startNextQueuedRunForAgent()`. It uses an agent-start lock, checks invokability and maximum concurrent runs, sorts queued work by priority/status/time, claims a run, and calls `executeRun()` (`external/paperclip/server/src/services/heartbeat.ts:7666-7755`). `resumeQueuedRuns()` is the startup recovery companion that scans active companies and starts the next queued run for each agent (`external/paperclip/server/src/services/heartbeat.ts:7544-7558`).

`executeRun()` resolves adapter config, secrets, and run-scoped mentioned skills before preparing workspace and environment context (`external/paperclip/server/src/services/heartbeat.ts:8270-8311`). It records or reuses execution workspace state, persists workspace metadata, and patches the issue with execution workspace fields (`external/paperclip/server/src/services/heartbeat.ts:8317-8504`). It then acquires an environment lease, realizes the workspace in the environment, resolves execution target and remote execution, and updates run context with environment/lease metadata (`external/paperclip/server/src/services/heartbeat.ts:8522-8611`).

After workspace and environment setup, the heartbeat service resolves runtime session parameters, workspace context, runtime service intents, and compaction behavior (`external/paperclip/server/src/services/heartbeat.ts:8612-8727`). It marks the run started, marks the agent running, begins run-log storage, redacts/persists logs, emits live log events, validates git-sensitive workspace state, ensures runtime services, emits adapter metadata, and finally calls `adapter.execute()` with run, agent, runtime, config, context, execution target/transport, log callbacks, spawn callbacks, and optional local agent JWT (`external/paperclip/server/src/services/heartbeat.ts:8764-9025`).

When the adapter returns or fails, the service normalizes usage/session data, final status, error/result JSON, and run metadata (`external/paperclip/server/src/services/heartbeat.ts:9120-9205`). Runtime state updates also aggregate token and cost totals and create cost events (`external/paperclip/server/src/services/heartbeat.ts:7611-7664`).

## Issue Dependency And Lock Lifecycle

Dependency readiness comes from `issueRelations` of type `blocks`. Done blockers still block if their latest workspace operation has not completed `workspace_finalize`; cancelled blockers are unresolved rather than silently ready (`external/paperclip/server/src/services/issues.ts:622-750`). Dependents become wakeable only when all blockers are done and workspace finalize barriers are satisfied (`external/paperclip/server/src/services/issues.ts:4396-4448`).

Checkout is another state transition path. It validates assignee, tree hold, dependency readiness, and stale locks, then updates issue assignee/status/checkout run/execution run fields with conflict and stale-adoption handling (`external/paperclip/server/src/services/issues.ts:5480-5688`).

## Routine Lifecycle

Routines are stored with revisions, triggers, and run rows in the database schema (`external/paperclip/packages/db/src/schema/routines.ts:22-154`). The routine service builds on issues and heartbeat: it creates a routine service with issue and heartbeat dependencies (`external/paperclip/server/src/services/routines.ts:491-500`). Dispatch computes a fingerprint, inserts a routine run, creates or coalesces an issue, queues assignment wakeup, and finalizes routine-run state (`external/paperclip/server/src/services/routines.ts:1213-1393`). Scheduled triggers are advanced by `tickScheduledTriggers()`, which queries due triggers, catches up with a bounded loop, updates `nextRunAt`, and triggers runs (`external/paperclip/server/src/services/routines.ts:2382-2453`).

## Plugin Lifecycle

The plugin loader defines four phases: discovery, installation, runtime activation, and shutdown (`external/paperclip/server/src/services/plugin-loader.ts:1-20`). `createApp()` initializes the registry, event bus, job scheduler/store, tool dispatcher, lifecycle manager, loader, and host services before mounting plugin routes (`external/paperclip/server/src/app.ts:253-322`). During app startup, the plugin job scheduler starts, the tool dispatcher initializes, the optional dev watcher starts, a bundled Kubernetes sandbox plugin can be auto-installed, and `loader.loadAll()` activates persisted plugins (`external/paperclip/server/src/app.ts:439-570`).

Activation resolves the worker entrypoint, applies plugin database migrations, builds host handlers, loads plugin config, starts a child-process worker, syncs job declarations, prepares the event bus, records webhook declarations, and registers agent tools (`external/paperclip/server/src/services/plugin-loader.ts:1785-1960`). The worker manager process model is explicit: workers are child processes speaking JSON-RPC 2.0 over stdio, with restart and graceful shutdown behavior (`external/paperclip/server/src/services/plugin-worker-manager.ts:1-19`, `external/paperclip/server/src/services/plugin-worker-manager.ts:220-259`).

## Shutdown Lifecycle

The server installs SIGINT and SIGTERM handlers. Shutdown stops telemetry/app services, closes the HTTP server, stops embedded Postgres when used, shuts down OpenTelemetry, and returns server info (`external/paperclip/server/src/index.ts:995-1036`). `createApp()` also returns service shutdown hooks for plugin jobs, feedback flushing, tool dispatcher, plugin dev watcher, bundled plugin setup, loader lifecycle, and other app-owned services (`external/paperclip/server/src/app.ts:439-570`).

## Lifecycle Takeaways

- Paperclip has one main execution path for agent work: durable wakeup request -> queued heartbeat run -> claim -> environment/workspace realization -> adapter execution -> durable result.
- Startup recovery is not optional decoration. Queued runs, runtime services, retries, stranded issue assignments, graph liveness, stale locks, output watchdogs, and productivity review are reconciled at server boot (`external/paperclip/server/src/index.ts:706-895`).
- Routines and timers reuse issue/heartbeat machinery rather than bypassing the control plane (`external/paperclip/server/src/services/routines.ts:1213-1393`, `external/paperclip/server/src/services/heartbeat.ts:11420-11535`).
- Plugins and adapters are separate extension planes: adapters execute agents; plugins can register jobs/tools/webhooks/UI and can contribute external adapters through the registry (`external/paperclip/server/src/adapters/registry.ts:536-617`, `external/paperclip/server/src/services/plugin-loader.ts:1785-1960`).
