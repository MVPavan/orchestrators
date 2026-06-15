# Paperclip Operational Model

## Local Runtime Shape

The README's local model is a single Node process with embedded Postgres and local file storage; production can use external Postgres, multiple companies, and scheduled heartbeats (`external/paperclip/README.md:330-347`). The quickstart points to `npx paperclipai onboard --yes`, and manual setup uses `pnpm install` followed by `pnpm dev`; the server is expected at `localhost:3100` with embedded Postgres auto-created (`external/paperclip/README.md:279-323`).

The root package scripts match that model. `dev` runs the server through a dev runner, `build` and `typecheck` perform workspace-link preflight before recursive pnpm commands, `test` delegates to `test:run`, and `paperclipai` invokes the CLI TypeScript entry through tsx (`external/paperclip/package.json:5-54`). The package requires Node `>=20` and pnpm `9.15.4` (`external/paperclip/package.json:62-65`).

## Configuration Defaults

Config loading reads an instance env file and a cwd `.env` file (`external/paperclip/server/src/config.ts:33-44`). Defaults include deployment mode `local_trusted`, local encrypted secrets, local disk storage, bind/host settings, port `3100`, embedded Postgres paths/port, UI serving options, database backup settings, and scheduler settings (`external/paperclip/server/src/config.ts:111-165`, `external/paperclip/server/src/config.ts:181-286`, `external/paperclip/server/src/config.ts:288-336`).

Authenticated public deployments are stricter. Startup requires `DATABASE_URL` for authenticated public deployment in the checked path (`external/paperclip/server/src/index.ts:215-229`). Startup also validates deployment mode and exposure before listening (`external/paperclip/server/src/index.ts:490-513`).

## Background Maintenance

Operationally, Paperclip is not just request/response. Startup runs recovery and maintenance loops for queued heartbeat runs, timer ticks, routine schedules, orphaned runs, scheduled retry promotion, stranded assigned issues, graph liveness, output watchdogs, stale locks, productivity review, database backups, and adapter reconciliation (`external/paperclip/server/src/index.ts:753-932`). This means "server is up" is not enough; schedulers and recovery loops are part of the product's correctness model.

The heartbeat service also exposes explicit recovery methods and `tickTimers()` in its public service API (`external/paperclip/server/src/services/heartbeat.ts:11420-11535`). Routine scheduling has its own due-trigger scan and catch-up loop (`external/paperclip/server/src/services/routines.ts:2382-2453`).

## Observability And Diagnostics

Paperclip records runtime state in several places:

- Heartbeat run rows contain execution status, usage, result/error, session identifiers, log references, process data, retries, and continuation context (`external/paperclip/packages/db/src/schema/heartbeat_runs.ts:6-59`).
- Wakeup request rows capture source/reason/payload/status/coalescing and idempotency details (`external/paperclip/packages/db/src/schema/agent_wakeup_requests.ts:5-40`).
- Heartbeat execution emits live events and persists redacted run logs through a run-log store (`external/paperclip/server/src/services/heartbeat.ts:8764-9025`).
- Cost totals and cost events are updated as runtime state is processed (`external/paperclip/server/src/services/heartbeat.ts:7611-7664`).
- The app exposes health/openapi/activity/dashboard/cost/backups and related routes through the API router (`external/paperclip/server/src/app.ts:208-252`).

OpenTelemetry is documented as available, with telemetry settings controlled by config/env (`external/paperclip/README.md:404-419`, `external/paperclip/server/src/config.ts:288-336`).

## Deployment And Auth Modes

Local trusted mode produces a local board actor in middleware (`external/paperclip/server/src/middleware/auth.ts:22-35`). Authenticated mode uses Better Auth/session handling, trusted origins, board API keys, agent API keys, local agent JWT fallback, and cloud tenant trusted headers (`external/paperclip/server/src/index.ts:521-568`, `external/paperclip/server/src/middleware/auth.ts:37-199`, `external/paperclip/server/src/middleware/auth.ts:203-280`).

For operations, this means local-trusted mode should be treated as a private-loopback development mode, not a generic public deployment posture. The config code also forces or validates exposure/bind choices around deployment mode (`external/paperclip/server/src/config.ts:160-286`, `external/paperclip/server/src/index.ts:490-513`).

## Plugin And Adapter Operations

Plugin operations include discovery/install, database migration application, worker startup, job sync, event-bus scoping, webhook registration, tool registration, crash recovery, and shutdown (`external/paperclip/server/src/services/plugin-loader.ts:1-20`, `external/paperclip/server/src/services/plugin-loader.ts:1785-1960`, `external/paperclip/server/src/services/plugin-worker-manager.ts:1-19`). App startup starts the plugin job scheduler and loads all persisted plugins (`external/paperclip/server/src/app.ts:439-570`).

Adapter operations include built-in adapter registration, external adapter plugin refresh, wait-for-adapters during startup, model/profile discovery, and adapter wrapping for auth-aware Hermes execution (`external/paperclip/server/src/index.ts:916-932`, `external/paperclip/server/src/adapters/registry.ts:441-725`).

## Repository Handling From This Parent Repo

`external/paperclip/` was treated as an external codebase. This research pass did not edit it. The parent repo overlay currently documents external submodules in general terms, but this specific `external/paperclip` checkout should be handled carefully until the parent repo's intended tracking model is clarified.

Safe operational assumptions for this repo:

- Write research outputs under `docs/research/codebases/paperclip/`.
- Do not modify `external/paperclip/` unless the task is explicitly submodule/external-codebase-local.
- If the goal is to run Paperclip, run commands from `external/paperclip/` and expect dependency install, embedded Postgres data directories, local env files, and server-generated state.
- If the goal is to change Paperclip, inspect its own git status and branch first; it is a nested git checkout.

## Verification Performed For This Report

This report is source-inspection based. It did not run Paperclip's build, typecheck, test suite, migrations, or server. The source snapshot and branch were checked with git, and report claims cite files in `external/paperclip/`.

Recommended verification before making runtime claims:

1. From `external/paperclip/`, confirm dependency state with `pnpm install` if needed.
2. Run the repo's own checks: `pnpm typecheck`, `pnpm test`, and targeted server/plugin/adapter tests if available.
3. For local startup claims, run `pnpm dev` and inspect server logs, embedded Postgres startup, health route, UI route, and scheduler startup messages.
4. For database claims, inspect migrations plus actual Drizzle schema state against a fresh migrated database.
5. For security claims, separately audit auth mode, plugin capability enforcement, secrets provider behavior, and adapter token/workspace handling.
