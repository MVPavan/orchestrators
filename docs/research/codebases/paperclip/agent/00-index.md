# Paperclip Architecture Research Index

Source target: `external/paperclip/`  
Snapshot: `412a04c964915fd45e15675f064d24332d50f6cc` on branch `master`  
Research date: 2026-06-14  
Primary deliverable: agent-readable architecture notes plus a human HTML overview.

## What Paperclip Is

Paperclip is a TypeScript monorepo for running an "AI company" control plane: a Node/Express server, React UI, CLI, adapters, plugins, and shared packages. Its README frames the product as a server and UI for orchestrating teams of AI agents, with company identity, work, heartbeat execution, governance, workspaces, plugins, budgets, routines, secrets, activity, and portability as first-class server responsibilities (`external/paperclip/README.md:28-36`, `external/paperclip/README.md:157-185`). The root workspace confirms the same shape at the package level: `server`, `ui`, `cli`, and `packages/*` participate in the pnpm workspace (`external/paperclip/pnpm-workspace.yaml:1-14`).

## Report Set

- [01-core-architecture.md](01-core-architecture.md) - module boundaries, control-plane shape, and dependency direction.
- [02-runtime-lifecycle.md](02-runtime-lifecycle.md) - server startup, HTTP lifecycle, heartbeat run execution, routines, plugins, and shutdown.
- [03-data-state-and-persistence.md](03-data-state-and-persistence.md) - Postgres/Drizzle schema model, locks, run records, storage, secrets, and backups.
- [04-integration-and-extension-points.md](04-integration-and-extension-points.md) - adapters, plugins, CLI, UI, MCP, environment runtimes, auth, storage, secrets, and telemetry boundaries.
- [05-operational-model.md](05-operational-model.md) - local/production runtime model, commands, background maintenance, observability, and repo handling.
- [90-open-questions.md](90-open-questions.md) - unresolved questions and recommended deeper audits.
- [../html/index.html](../html/index.html) - single-file human overview.

## Architecture Summary

1. The server is the durable control plane. `startServer()` loads configuration, initializes telemetry, prepares database connectivity, configures auth/storage/backup/plugin services, starts schedulers, reconciles runtime state, and starts HTTP/WebSocket serving (`external/paperclip/server/src/index.ts:102-116`, `external/paperclip/server/src/index.ts:642-704`, `external/paperclip/server/src/index.ts:753-895`, `external/paperclip/server/src/index.ts:934-993`).
2. Persistence is Postgres via Drizzle. The database package exposes `createDb()` around `postgres()` plus the generated schema object, and the schema index exports the domain tables for companies, users, agents, issues, heartbeats, costs, approvals, activity, secrets, skills, plugins, jobs, runtime services, and more (`external/paperclip/packages/db/src/client.ts:37-51`, `external/paperclip/packages/db/src/schema/index.ts:1-85`).
3. The heartbeat service is the execution kernel. It queues wakeup requests, enforces agent invokability and budget/dependency gates, realizes workspaces and environments, resolves skills/secrets/session context, invokes an adapter, persists logs/usage/result state, and emits live events (`external/paperclip/server/src/services/heartbeat.ts:10099-10795`, `external/paperclip/server/src/services/heartbeat.ts:8270-9025`, `external/paperclip/server/src/services/heartbeat.ts:9120-9205`).
4. Issues are both the work item model and a concurrency surface. Issue dependency readiness is derived from `blocks` relations and a workspace-finalization barrier, and checkout updates issue status, assignee, checkout/run lock fields, and stale-lock behavior (`external/paperclip/server/src/services/issues.ts:622-750`, `external/paperclip/server/src/services/issues.ts:5480-5688`).
5. Execution workspaces and environments isolate agent runs. The heartbeat path creates or reuses execution workspace records, patches issues with workspace metadata, acquires environment leases, realizes workspaces through runtime drivers, and resolves adapter execution targets (`external/paperclip/server/src/services/heartbeat.ts:8317-8579`, `external/paperclip/server/src/services/environment-run-orchestrator.ts:202-320`, `external/paperclip/server/src/services/environment-run-orchestrator.ts:337-501`).
6. Adapters abstract concrete agent runtimes. The registry imports built-in adapters for Claude, Codex, Cursor, Gemini, Grok, OpenClaw, OpenCode, and process/HTTP variants, then can load plugin-provided external adapters from the plugin store (`external/paperclip/server/src/adapters/registry.ts:1-145`, `external/paperclip/server/src/adapters/registry.ts:249-435`, `external/paperclip/server/src/adapters/registry.ts:514-617`).
7. Plugins are out-of-process extension modules. The loader discovers, installs, validates, and activates plugins, while the worker manager runs plugin workers as child processes over JSON-RPC 2.0 stdio with restart/shutdown handling (`external/paperclip/server/src/services/plugin-loader.ts:1-20`, `external/paperclip/server/src/services/plugin-loader.ts:1785-1960`, `external/paperclip/server/src/services/plugin-worker-manager.ts:1-19`).
8. UI, CLI, and MCP are client surfaces over the server API rather than alternate business-logic implementations. The Express app mounts the API route tree and static/Vite UI handling (`external/paperclip/server/src/app.ts:208-322`, `external/paperclip/server/src/app.ts:341-437`), the React app routes to board views (`external/paperclip/ui/src/App.tsx:73-177`), the CLI registers command groups over an HTTP client (`external/paperclip/cli/src/index.ts:50-201`, `external/paperclip/cli/src/client/http.ts:53-180`), and the MCP server README says it is a thin REST wrapper with no direct database or business logic (`external/paperclip/packages/mcp-server/README.md:1-17`).
9. Local deployment defaults are self-contained. The README says local runs use a single Node process, embedded Postgres, and local file storage; production can use external Postgres and scheduled heartbeats (`external/paperclip/README.md:330-347`). The config code defaults to port `3100`, embedded Postgres port `54329`, local encrypted secrets, local disk storage, scheduler interval at least 10 seconds with 30 seconds default, and telemetry enabled unless disabled by config/env (`external/paperclip/server/src/config.ts:111-165`, `external/paperclip/server/src/config.ts:288-336`).

## Scope Boundaries

- This pass read source and docs only. It did not run `pnpm install`, start the server, run migrations, or execute tests.
- The parent repo was modified only by adding this report tree and by updating Beads tracking. `external/paperclip/` was treated as read-only.
- The report focuses on runtime architecture. It does not audit every UI page, every migration file, every adapter implementation, release automation, Docker packaging, or documentation accuracy outside the architecture-critical paths.
- Claims about behavior are source-grounded to the cited snapshot. They are not live runtime verification.
