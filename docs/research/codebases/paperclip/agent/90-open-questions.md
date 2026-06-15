# Paperclip Open Questions

## Tracking And Scope

1. Is `external/paperclip/` intended to become a tracked submodule of the parent orchestrators repo, or is it a local external checkout used only for research? The parent overlay names `external/gascity` and `external/gastown` as submodules, but this research request targeted `external/paperclip/` as an available nested checkout. This should be clarified before staging any parent-repo metadata around Paperclip.
2. Should this report set be linked from `docs/research/codebases/00-index.md` or another top-level docs index? I did not add cross-index links because the user asked specifically for `@external/paperclip/` research and because parent docs indexing conventions should be followed deliberately.

## Runtime Verification Gaps

1. I did not install dependencies, run `pnpm typecheck`, run `pnpm test`, start `pnpm dev`, run migrations, or exercise the UI/API/CLI. Claims here are source-grounded, not runtime-proven.
2. Embedded Postgres behavior was read from startup/config source and README only. A local boot test should verify data-dir selection, port selection, migration application, backup scheduling, and shutdown cleanup.
3. Scheduler/recovery behavior is source-grounded from startup and heartbeat/routine code. It still needs live tests for queue recovery, timer wakeups, stale lock sweeping, routine catch-up, and orphaned run recovery under realistic failure timing.

## Security And Trust Questions

1. Plugin security needs deeper review. Source shows plugin activation can apply plugin database migrations, spawn workers, sync jobs, expose webhooks, register tools, and use host handlers (`external/paperclip/server/src/services/plugin-loader.ts:1785-1960`). A security pass should inspect manifest validation, capability checks, host handler authorization, worker environment contents, plugin database namespace isolation, and restart/crash behavior.
2. Adapter trust boundaries need deeper review. Adapters receive execution context, workspace/transport details, logs/spawn hooks, runtime config, and possibly local agent JWTs (`external/paperclip/server/src/services/heartbeat.ts:8962-9025`). A security pass should inspect token scoping, workspace path safety, command execution, log redaction, and remote execution target handling.
3. Local-trusted mode should be threat-modeled separately from authenticated deployment. Middleware defaults a local board actor in local-trusted mode, while authenticated mode uses sessions, API keys, agent keys, JWTs, and cloud tenant headers (`external/paperclip/server/src/middleware/auth.ts:22-199`, `external/paperclip/server/src/middleware/auth.ts:203-280`).
4. Telemetry defaults need product/privacy confirmation. README and config indicate telemetry is configurable, with docs saying telemetry is enabled by default and can be disabled (`external/paperclip/README.md:404-419`, `external/paperclip/server/src/config.ts:288-336`).

## Data And Migration Questions

1. This pass did not audit migration history. Schema claims cite Drizzle table definitions, but a migration audit is needed to confirm fresh database creation, upgrade paths, downgrade assumptions, and plugin-owned migration interactions.
2. Workspace-finalization barriers are architecturally important. The issue service treats done blockers as not ready if workspace finalization has not completed (`external/paperclip/server/src/services/issues.ts:622-750`). A deeper correctness review should inspect all producers of workspace operation records and all paths that mark finalization success/failure.
3. Runtime services are persisted and reconciled on startup (`external/paperclip/server/src/index.ts:706-730`, `external/paperclip/packages/db/src/schema/workspace_runtime_services.ts:18-71`). A deeper review should verify ownership, health checks, lease cleanup, service reuse keys, and stale provider references.

## Product And Architecture Questions

1. The README explicitly says Paperclip is not an agent framework, prompt manager, chat UI, task queue, or workflow engine (`external/paperclip/README.md:266-275`). The implementation nevertheless contains queueing, routines, plugins, adapters, runtime services, and work orchestration. The distinction appears to be product positioning rather than absence of those mechanisms; future docs should make that boundary precise.
2. The service layer is broad (`external/paperclip/server/src/services/index.ts:1-78`). Before large changes, map the exact cross-service transaction boundaries for the touched domain instead of assuming a clean vertical slice.
3. The adapter registry lets external adapters override built-ins by type (`external/paperclip/server/src/adapters/registry.ts:536-617`). That is powerful, but it raises operational questions around provenance, versioning, downgrade, and conflict resolution.
4. The MCP package is intentionally a REST wrapper with no direct DB or business logic (`external/paperclip/packages/mcp-server/README.md:1-17`). Any future MCP feature should preserve that boundary unless there is an explicit architecture decision to change it.
