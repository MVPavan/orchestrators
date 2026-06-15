# Paperclip Core Architecture

## System Thesis

Paperclip is a server-centered orchestration system for persistent agent work. The server owns durable state, execution policy, queueing, workspace/environment setup, auth, plugin lifecycle, background maintenance, and API surfaces. The UI, CLI, MCP server, adapters, and plugins are important boundaries, but the control plane is concentrated in `server/src/index.ts`, `server/src/app.ts`, `server/src/services/*`, and `packages/db` (`external/paperclip/server/src/index.ts:102-116`, `external/paperclip/server/src/app.ts:129-158`, `external/paperclip/server/src/services/index.ts:1-78`, `external/paperclip/packages/db/src/client.ts:37-51`).

## Package And Process Map

| Area | Architectural role | Source evidence |
| --- | --- | --- |
| Root workspace | Declares a pnpm monorepo over `packages/*`, `server`, `ui`, and `cli`. | `external/paperclip/pnpm-workspace.yaml:1-14` |
| `server/` | Node/Express control plane, startup lifecycle, REST routes, background services, schedulers, plugins, and WebSocket events. | `external/paperclip/server/src/index.ts:642-704`, `external/paperclip/server/src/app.ts:208-322` |
| `packages/db/` | Drizzle/Postgres schema and database client. | `external/paperclip/packages/db/src/client.ts:37-51`, `external/paperclip/packages/db/src/schema/index.ts:1-85` |
| `ui/` | React board and admin surface over `/api`. | `external/paperclip/ui/src/App.tsx:73-177`, `external/paperclip/ui/src/api/client.ts:1-50` |
| `cli/` | Command surface for onboard, run, heartbeat, work, agents, projects, costs, plugins, secrets, routines, and more. | `external/paperclip/cli/src/index.ts:50-201` |
| `packages/adapters/*` | Adapter packages that implement concrete agent runtimes. | `external/paperclip/server/src/adapters/registry.ts:249-435` |
| `packages/plugins/sdk` | SDK and worker protocol exports for plugin authors. | `external/paperclip/packages/plugins/sdk/src/index.ts:1-86` |
| `packages/mcp-server` | MCP facade over REST API, explicitly not a direct DB/business-logic layer. | `external/paperclip/packages/mcp-server/README.md:1-17` |

## Control Plane Boundary

`startServer()` is the primary composition root. It waits for telemetry instrumentation, loads runtime config, sets secret-related environment variables, chooses an external or embedded Postgres path, creates the database client, configures auth, initializes storage/feedback/backup/plugin services, creates the Express app, attaches live-event WebSockets, starts schedulers and recovery loops, then listens for traffic (`external/paperclip/server/src/index.ts:102-116`, `external/paperclip/server/src/index.ts:304-323`, `external/paperclip/server/src/index.ts:324-488`, `external/paperclip/server/src/index.ts:521-568`, `external/paperclip/server/src/index.ts:577-668`, `external/paperclip/server/src/index.ts:701-704`, `external/paperclip/server/src/index.ts:753-895`, `external/paperclip/server/src/index.ts:934-993`).

`createApp()` is the HTTP composition root. It accepts `db` plus runtime options and then wires middleware, auth, typed API routers, plugin services/routes, adapter routes, static plugin UI, built UI assets, and optional Vite dev middleware (`external/paperclip/server/src/app.ts:129-158`, `external/paperclip/server/src/app.ts:164-203`, `external/paperclip/server/src/app.ts:208-322`, `external/paperclip/server/src/app.ts:336-437`). This keeps most business capabilities behind server-side services rather than duplicating them in client code.

## Domain Service Layer

The service barrel exports the major bounded domains: companies, artifacts, skills, agents, instructions, documents, issues, thread interactions, tree control, approvals, references, recovery, goals, activity, budgets, secrets, routines, costs, finance, heartbeat, productivity, dashboards, access, auth, settings, cloud upstreams, company portability, teams, environments, execution workspaces, workspace operations, work products, live events, runtime services, and storage (`external/paperclip/server/src/services/index.ts:1-78`).

The important implication is that Paperclip's service layer is broad but still mostly server-local. External runtime systems enter through explicit adapters, plugins, environment runtimes, storage providers, secrets providers, or HTTP/MCP clients instead of by bypassing the server state model.

## Core Runtime Loop

The central loop is:

1. A user, routine, timer, dependency release, or external call asks the heartbeat service to wake an agent.
2. The heartbeat service validates company/agent state, budget policy, issue status, dependency readiness, and tree holds.
3. It records a wakeup request and queued heartbeat run.
4. It claims the next queued run for an agent under an agent-start lock.
5. It constructs execution context: issue/project/goal context, runtime skills, secrets, workspace, environment lease, runtime services, session parameters, and adapter config.
6. It calls the selected adapter and persists run logs, usage, costs, session state, and final status.

The queue and gate checks are concentrated in `enqueueWakeup()` and `startNextQueuedRunForAgent()` (`external/paperclip/server/src/services/heartbeat.ts:7666-7755`, `external/paperclip/server/src/services/heartbeat.ts:10099-10795`). Context construction and adapter execution happen in `executeRun()` (`external/paperclip/server/src/services/heartbeat.ts:8270-9025`, `external/paperclip/server/src/services/heartbeat.ts:9120-9205`).

## Work Model

Issues are not just tickets. They are the coordination object for agent work, locks, dependency gates, execution workspace inheritance, and wakeable dependents. The issue service computes dependency readiness from `blocks` relations and treats done blockers with unfinalized workspace operations as still blocking (`external/paperclip/server/src/services/issues.ts:622-750`). Issue creation can inherit or validate execution workspace references (`external/paperclip/server/src/services/issues.ts:4860-4938`). Checkout checks assignability, tree holds, dependency readiness, stale execution locks, and then updates assignee/status/run lock fields (`external/paperclip/server/src/services/issues.ts:5480-5688`).

## Workspace And Environment Boundary

Execution workspaces are persistent records for where and how work should happen. The schema stores project/source issue, mode, strategy, path, repo/ref/branch, provider references, status, and metadata (`external/paperclip/packages/db/src/schema/execution_workspaces.ts:15-68`). During a run, the heartbeat service reuses or realizes a workspace and patches the issue with execution workspace metadata (`external/paperclip/server/src/services/heartbeat.ts:8317-8504`). The environment run orchestrator then resolves an environment, acquires a lease, realizes the workspace through a local/ssh/sandbox driver, persists realization metadata, and resolves the adapter execution target (`external/paperclip/server/src/services/environment-run-orchestrator.ts:202-320`, `external/paperclip/server/src/services/environment-run-orchestrator.ts:337-501`).

This boundary is important because it prevents adapter packages from needing to know how to provision or lease environments. They receive an execution target and context produced by the server.

## Adapter Boundary

Built-in adapters are registered by the server adapter registry. The registry imports concrete modules for Claude, Codex, Cursor, Gemini, Grok, OpenClaw, OpenCode, Pi, HTTP, and process execution (`external/paperclip/server/src/adapters/registry.ts:1-145`, `external/paperclip/server/src/adapters/registry.ts:249-435`). It registers built-ins and can asynchronously load external adapter plugins from the plugin store, with external plugins overriding built-ins by type (`external/paperclip/server/src/adapters/registry.ts:514-617`).

Concrete adapter metadata confirms that adapters are runtime-specific wrappers. The Claude local adapter declares install commands, models, config fields, permission behavior, and workspace strategy (`external/paperclip/packages/adapters/claude-local/src/index.ts:3-58`). The Codex local adapter declares Codex-specific stdin, skill injection, managed `CODEX_HOME`, workspace env injection, and model/profile metadata (`external/paperclip/packages/adapters/codex-local/src/index.ts:3-100`). The OpenClaw gateway adapter declares WebSocket gateway configuration and payload/session/runtime-service metadata (`external/paperclip/packages/adapters/openclaw-gateway/src/index.ts:1-55`).

## Plugin Boundary

Plugins are a separate extension plane from adapters, though plugins can contribute adapters and tools. The plugin loader describes discovery, installation, runtime activation, and shutdown as its lifecycle (`external/paperclip/server/src/services/plugin-loader.ts:1-20`). Activation resolves the worker entrypoint, applies restricted plugin database migrations, builds host handlers, loads config, starts a worker, syncs jobs, creates an event-bus scope, counts webhooks, and registers tools (`external/paperclip/server/src/services/plugin-loader.ts:1785-1960`). The worker manager states the process model directly: plugin workers are child processes that communicate with the host over JSON-RPC 2.0 on stdio, with crash recovery, one worker per plugin, and graceful shutdown (`external/paperclip/server/src/services/plugin-worker-manager.ts:1-19`).

## Client Surfaces

The React UI uses a small API client with base path `/api`, credentials included, JSON defaults, and typed HTTP helpers (`external/paperclip/ui/src/api/client.ts:1-50`). The CLI bootstraps environment/config in a pre-action hook, exposes onboarding/doctor/run/heartbeat commands, and registers many client command groups (`external/paperclip/cli/src/index.ts:50-201`). The CLI HTTP client injects auth headers and `x-paperclip-run-id` when present (`external/paperclip/cli/src/client/http.ts:53-180`). The MCP server registers tools over an API client and documents itself as a REST wrapper (`external/paperclip/packages/mcp-server/src/index.ts:7-17`, `external/paperclip/packages/mcp-server/README.md:1-17`).

## Architectural Risks To Watch

- The service layer is wide. That is not automatically bad, but it means cross-domain changes need source-level tracing through heartbeat, issues, budgets, environments, plugins, and runtime services rather than a single subsystem read (`external/paperclip/server/src/services/index.ts:1-78`).
- The heartbeat path is the highest-risk integration point because it composes locks, budgets, skills, secrets, workspaces, environments, adapters, runtime services, logs, costs, and session state in one execution path (`external/paperclip/server/src/services/heartbeat.ts:8270-9025`, `external/paperclip/server/src/services/heartbeat.ts:9120-9205`).
- The plugin boundary is powerful and therefore security-sensitive: activation can apply plugin-owned database migrations, spawn workers, register jobs/tools/webhooks, and receive host handlers (`external/paperclip/server/src/services/plugin-loader.ts:1785-1960`).
