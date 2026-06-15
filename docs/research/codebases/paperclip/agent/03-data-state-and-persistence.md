# Paperclip Data, State, And Persistence

## Database Foundation

Paperclip uses Postgres through Drizzle. `createDb(url)` creates a `postgres` client and a Drizzle database bound to the shared schema object (`external/paperclip/packages/db/src/client.ts:37-51`). Migration files are discovered and sorted from the migrations directory (`external/paperclip/packages/db/src/client.ts:68-74`), while server startup inspects and applies migrations before creating the running database client (`external/paperclip/server/src/index.ts:151-199`, `external/paperclip/server/src/index.ts:304-488`).

Local development can run against embedded Postgres; production/authenticated public deployment requires explicit external database configuration in key cases (`external/paperclip/server/src/index.ts:215-229`, `external/paperclip/server/src/index.ts:304-488`). The README describes local mode as one Node process with embedded Postgres and local file storage, and production as external Postgres with scheduled heartbeats (`external/paperclip/README.md:330-347`).

## Schema Groups

The schema index exports a broad control-plane schema: companies, users, accounts/sessions, memberships/invites, agents, agent runtime state, agent environment preferences, budgets, projects, goals, issues, issue relations, comments, documents, heartbeat runs/events/watchdogs, costs, approvals, approval policies, activity, secrets, skills, plugins, plugin jobs/logs/webhooks, environments, execution workspaces, runtime services, backups, and more (`external/paperclip/packages/db/src/schema/index.ts:1-85`).

This is a cohesive operational database, not a thin task table. Most runtime entities that matter to an agent run have durable rows: the agent, issue, wakeup request, heartbeat run, execution workspace, environment lease, runtime services, cost events, activity events, logs, and plugin/job state (`external/paperclip/packages/db/src/schema/index.ts:1-85`).

## Agent And Run State

Agents store company ownership, name/role/title/status, hierarchy via `reportsToAgentId`, adapter type/config, runtime config, default environment, budget, permissions, and last-heartbeat time (`external/paperclip/packages/db/src/schema/agents.ts:14-44`). Wakeup requests store company/agent/source/detail/reason/payload, issue, status, coalescing count, actor, idempotency key, run ID, and timestamps (`external/paperclip/packages/db/src/schema/agent_wakeup_requests.ts:5-40`).

Heartbeat runs store company/agent/project/issue, invocation source and reason, status, start/finish times, summary/error/result, token/cost usage, context, adapter runtime metadata, session identifiers, log references, process information, retry state, issue comment/liveness/continuation context, and timestamps (`external/paperclip/packages/db/src/schema/heartbeat_runs.ts:6-59`). The heartbeat service updates runtime state with token/cost aggregates and creates cost events as runs progress (`external/paperclip/server/src/services/heartbeat.ts:7611-7664`).

## Issue State And Concurrency

Issues store company/project/parent/agent fields, title/description/status/type/priority, timestamps, interaction state, execution lock/run fields, execution workspace fields, liveness and recovery metadata, and productivity-review fields (`external/paperclip/packages/db/src/schema/issues.ts:22-72`). Indexes and partial indexes support open routine execution, active liveness recovery, productivity review, and stranded recovery queries (`external/paperclip/packages/db/src/schema/issues.ts:73-144`).

The issue service treats dependency readiness and workspace completion as part of durable state. It checks `blocks` relations, unresolved/cancelled blockers, and whether blocker workspaces have a completed `workspace_finalize` operation (`external/paperclip/server/src/services/issues.ts:622-750`). Checkout updates lock-like fields only after assignability, tree-hold, dependency, and stale-lock checks (`external/paperclip/server/src/services/issues.ts:5480-5688`).

## Workspace And Runtime Service State

Execution workspaces store project/source issue, mode, workspace strategy, status, local path, repo/base ref/branch/provider metadata, and arbitrary metadata (`external/paperclip/packages/db/src/schema/execution_workspaces.ts:15-68`). The heartbeat service creates/reuses execution workspaces, records workspace operations, updates workspace metadata, and patches issue execution workspace fields during run setup (`external/paperclip/server/src/services/heartbeat.ts:8317-8504`).

Runtime services are persisted separately from workspaces. The schema stores company/project/execution workspace/issue, service name/type/status/lifecycle/reuse key, command/cwd/env, port/url, provider metadata, owner run, health, and timestamps (`external/paperclip/packages/db/src/schema/workspace_runtime_services.ts:18-71`). Startup reconciles persisted runtime services before work resumes (`external/paperclip/server/src/index.ts:706-730`), and each run can ensure runtime services before adapter execution (`external/paperclip/server/src/services/heartbeat.ts:8894-8913`).

## Routine State

Routines, routine revisions, routine triggers, and routine runs have separate schema tables (`external/paperclip/packages/db/src/schema/routines.ts:22-154`). The service dispatch path inserts routine-run rows, creates or coalesces issues, queues assignment wakeups, and finalizes routine-run state (`external/paperclip/server/src/services/routines.ts:1213-1393`). This keeps recurring automation visible as both routine state and normal work/heartbeat state.

## Plugin State

The plugin schema stores plugin key/package/version/API version, categories, manifest JSON, status, package path, and timestamps (`external/paperclip/packages/db/src/schema/plugins.ts:13-45`). Activation can apply plugin-owned schema migrations before worker startup (`external/paperclip/server/src/services/plugin-loader.ts:1785-1847`). Job declarations, logs, webhooks, event subscriptions, and tools are synchronized through plugin services during app and plugin startup (`external/paperclip/server/src/app.ts:253-322`, `external/paperclip/server/src/services/plugin-loader.ts:1848-1960`).

## Object Storage

The storage layer is provider-configured. `createStorageService()` builds a storage service for the configured provider (`external/paperclip/server/src/storage/index.ts:21-33`). The storage service prefixes object keys by company, rejects path traversal and cross-company key access, stores objects under `companyId/namespace/YYYY/MM/DD/uuid-stem.ext`, and exposes put/get/head/delete operations with hash metadata (`external/paperclip/server/src/storage/service.ts:46-70`, `external/paperclip/server/src/storage/service.ts:90-130`).

This means binary/file artifacts are not modeled as arbitrary filesystem paths in business services. They flow through storage keys and provider boundaries.

## Secrets

The configured secrets provider defaults to `local_encrypted` (`external/paperclip/server/src/secrets/configured-provider.ts:3-8`). The secrets service defines redaction behavior for sensitive environment keys, runtime secret manifest entries, secret resolution, and canonical binding forms for plain values versus secret references (`external/paperclip/server/src/services/secrets.ts:58-61`, `external/paperclip/server/src/services/secrets.ts:187-202`, `external/paperclip/server/src/services/secrets.ts:237-249`).

Agent-local JWTs are separate from general secrets. JWT config is derived from `PAPERCLIP_AGENT_JWT_SECRET` or `BETTER_AUTH_SECRET`, per-company signing keys are derived to prevent cross-tenant token reuse, tokens can be created for local agents, and verification includes a legacy-fallback toggle (`external/paperclip/server/src/agent-auth-jwt.ts:34-61`, `external/paperclip/server/src/agent-auth-jwt.ts:91-187`).

## Configuration And Backups

Config loading reads instance environment files and local `.env` files (`external/paperclip/server/src/config.ts:33-44`). Defaults include deployment mode `local_trusted`, local encrypted secrets, local disk storage, port `3100`, embedded Postgres directory/port, UI serving options, scheduler enablement with minimum interval enforcement, telemetry enablement, and database backup settings (`external/paperclip/server/src/config.ts:111-165`, `external/paperclip/server/src/config.ts:247-336`). Startup starts automatic backup scheduling when configured (`external/paperclip/server/src/index.ts:898-914`).

## State Model Implications

- Most important runtime events are durable: wakeups, runs, issues, locks, workspace state, runtime services, routine runs, plugin jobs, costs, and activity are database-backed (`external/paperclip/packages/db/src/schema/index.ts:1-85`).
- Concurrency is distributed across service transactions, row locks, agent-start locks, issue execution lock fields, dependency state, workspace-finalize barriers, and recovery sweeps (`external/paperclip/server/src/services/heartbeat.ts:7666-7755`, `external/paperclip/server/src/services/heartbeat.ts:10301-10772`, `external/paperclip/server/src/services/issues.ts:5480-5688`, `external/paperclip/server/src/index.ts:753-895`).
- File/object durability and secret durability are provider abstractions; database rows point at structured metadata and storage/secret references rather than holding all raw content inline (`external/paperclip/server/src/storage/service.ts:60-70`, `external/paperclip/server/src/services/secrets.ts:187-249`).
- Embedded local Postgres makes onboarding easy, but operational correctness still depends on the same migration, backup, lock, and recovery logic used by larger deployments (`external/paperclip/server/src/index.ts:151-199`, `external/paperclip/server/src/index.ts:324-488`, `external/paperclip/server/src/index.ts:898-914`).
