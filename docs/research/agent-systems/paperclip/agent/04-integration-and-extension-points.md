# Paperclip Integration And Extension Points

## API And Client Surfaces

The primary integration surface is the server API. `createApp()` mounts a broad REST route tree under `/api`, including companies, LLMs, skills, teams, agents, assets, projects, issues, routines, environments, execution workspaces, goals, approvals, secrets, costs, activity, dashboards, inbox/profile/resource/settings, backups, plugins, and adapters (`external/agent-systems/paperclip/server/src/app.ts:208-322`).

The React UI is a first-party API client. Its API helper uses base path `/api`, includes credentials, sets JSON headers, handles JSON/non-JSON responses, and exposes HTTP verb helpers (`external/agent-systems/paperclip/ui/src/api/client.ts:1-50`). The app route map exposes board pages for dashboards, company settings, environments, cloud/upstream/access/invites/secrets/instance settings/plugins/adapters, org/agents, projects, workspaces, issues, search, routines, execution workspaces, goals, artifacts, approvals, costs, activity, inbox, and plugin routes (`external/agent-systems/paperclip/ui/src/App.tsx:73-177`).

The CLI is another first-party client. It loads data-dir/env/telemetry in a pre-action hook, registers onboarding/doctor/configure/backup/run/heartbeat commands, and then registers command groups for most server domains (`external/agent-systems/paperclip/cli/src/index.ts:50-201`). Its HTTP client stores API base/key/run ID, adds auth and run headers, wraps common verbs, builds URLs, and handles error/auth recovery (`external/agent-systems/paperclip/cli/src/client/http.ts:53-180`).

## MCP Surface

The MCP package documents itself as a thin wrapper over the Paperclip REST API and explicitly says it contains no direct database access or business logic (`external/agent-systems/paperclip/packages/mcp-server/README.md:1-17`). Its runtime creates an MCP server, builds a `PaperclipApiClient`, and registers tool definitions (`external/agent-systems/paperclip/packages/mcp-server/src/index.ts:7-17`). The tool definition file exposes tools such as current-user context, inbox, agent and issue list/get operations, and heartbeat context (`external/agent-systems/paperclip/packages/mcp-server/src/tools.ts:236-294`).

This is a useful boundary: MCP clients should be treated as API consumers, not privileged internal code.

## Adapter Extension Point

Adapters are the execution boundary for concrete AI runtimes. The registry imports built-in local/gateway/process/http adapters, wraps them where needed, registers built-ins, and can load external adapter definitions from plugins (`external/agent-systems/paperclip/server/src/adapters/registry.ts:1-145`, `external/agent-systems/paperclip/server/src/adapters/registry.ts:441-617`). The heartbeat service invokes adapters through a normalized `adapter.execute()` call and passes run, agent, runtime, adapter config, context, execution target/transport, logs, spawn hooks, metadata hooks, and optional local agent JWT (`external/agent-systems/paperclip/server/src/services/heartbeat.ts:8962-9025`).

Built-in adapter metadata shows the intended contract:

- Claude local declares install command, models, config fields, permission skipping default, and workspace strategy notes (`external/agent-systems/paperclip/packages/adapters/claude-local/src/index.ts:3-58`).
- Codex local declares model/profile metadata, stdin usage, skills injection, managed `CODEX_HOME`, and workspace environment injection (`external/agent-systems/paperclip/packages/adapters/codex-local/src/index.ts:3-100`).
- OpenClaw gateway declares WebSocket gateway configuration and forwards session/runtime service metadata (`external/agent-systems/paperclip/packages/adapters/openclaw-gateway/src/index.ts:1-55`).

## Plugin Extension Point

Plugins extend Paperclip through a manifest, host services, and an out-of-process worker. The loader's file header defines discovery from local plugin directories and `node_modules`, installation with manifest/capability validation, runtime activation with host handlers/workers/jobs/events/tools, and shutdown (`external/agent-systems/paperclip/server/src/services/plugin-loader.ts:1-20`). Activation applies plugin DB migrations, starts the worker process, syncs jobs, prepares the event bus, registers webhooks, and registers agent tools (`external/agent-systems/paperclip/server/src/services/plugin-loader.ts:1785-1960`).

The worker manager process boundary is JSON-RPC 2.0 over stdio, one child process per plugin, with timeout/backoff/restart and graceful shutdown behavior (`external/agent-systems/paperclip/server/src/services/plugin-worker-manager.ts:1-19`, `external/agent-systems/paperclip/server/src/services/plugin-worker-manager.ts:61-92`, `external/agent-systems/paperclip/server/src/services/plugin-worker-manager.ts:220-259`). The plugin SDK exposes `definePlugin`, test/bundler/dev-server helpers, worker RPC host, host client handlers, protocol helpers, and context/client types (`external/agent-systems/paperclip/packages/plugins/sdk/src/index.ts:1-86`, `external/agent-systems/paperclip/packages/plugins/sdk/src/index.ts:188-240`).

## Environment Runtime Extension Point

Environments determine where a run executes. The environment run orchestrator resolves the selected environment, acquires a lease through an environment runtime service, resolves transport, logs lease acquisition, realizes the workspace through local/ssh/sandbox drivers, optionally provisions remote workspaces, persists realization metadata, resolves the adapter execution target, and releases leases after runs (`external/agent-systems/paperclip/server/src/services/environment-run-orchestrator.ts:157-320`, `external/agent-systems/paperclip/server/src/services/environment-run-orchestrator.ts:337-573`).

The heartbeat service consumes this boundary after it has selected or created the execution workspace (`external/agent-systems/paperclip/server/src/services/heartbeat.ts:8317-8579`). Adapter authors should not infer workspace paths or remote transport directly; that information is passed through the execution target and context resolved by the server.

## Auth And Identity Integrations

Paperclip supports local-trusted and authenticated modes. Startup creates either a local trusted board principal or Better Auth-backed authenticated mode with trusted origins and board claim challenge (`external/agent-systems/paperclip/server/src/index.ts:521-568`). The auth middleware sets a local-board actor in local-trusted mode, handles Better Auth/session/cloud tenant context, accepts board API keys, and validates agent API keys or local agent JWTs (`external/agent-systems/paperclip/server/src/middleware/auth.ts:22-199`, `external/agent-systems/paperclip/server/src/middleware/auth.ts:203-280`).

Local agent JWTs are derived from configured secrets, scoped with per-company signing keys, and include verification logic with optional legacy fallback (`external/agent-systems/paperclip/server/src/agent-auth-jwt.ts:34-187`). The adapter registry includes a Hermes wrapper that injects auth guard environment when an auth token is available (`external/agent-systems/paperclip/server/src/adapters/registry.ts:441-500`).

## Storage And Secrets Providers

Storage is provider-configured and company-prefixed (`external/agent-systems/paperclip/server/src/storage/index.ts:21-33`, `external/agent-systems/paperclip/server/src/storage/service.ts:46-130`). Secrets default to the configured provider, with local encrypted as the default, redaction rules for sensitive environment variables, runtime secret manifest entries, and explicit binding canonicalization (`external/agent-systems/paperclip/server/src/secrets/configured-provider.ts:3-8`, `external/agent-systems/paperclip/server/src/services/secrets.ts:58-249`).

These providers are extension points but also policy surfaces. Any new provider has to preserve company isolation, traversal protection, redaction semantics, and runtime binding behavior.

## Telemetry And Operational Integrations

The README documents OpenTelemetry as opt-in and describes telemetry defaults and disable switches (`external/agent-systems/paperclip/README.md:404-419`). Server startup waits for instrumentation readiness and initializes telemetry before other runtime setup (`external/agent-systems/paperclip/server/src/index.ts:102-116`). Config includes telemetry enablement in the returned runtime configuration (`external/agent-systems/paperclip/server/src/config.ts:288-336`).

Live events are also a first-party integration surface. Startup creates a live-events WebSocket server after the HTTP server is created (`external/agent-systems/paperclip/server/src/index.ts:701-704`), and the heartbeat path emits live queued/log/run events around execution (`external/agent-systems/paperclip/server/src/services/heartbeat.ts:8764-9025`, `external/agent-systems/paperclip/server/src/services/heartbeat.ts:10775-10795`).

## Extension Risk Notes

- Adapter extensions affect the execution boundary and receive high-value run context. Review adapter config, execution target handling, auth token flow, logs, and workspace safety before trusting a new adapter (`external/agent-systems/paperclip/server/src/services/heartbeat.ts:8962-9025`, `external/agent-systems/paperclip/server/src/adapters/registry.ts:536-617`).
- Plugin extensions can add database migrations, workers, jobs, webhooks, tools, and event subscriptions. Treat plugin manifest validation, capability gating, host handlers, and worker isolation as security-critical (`external/agent-systems/paperclip/server/src/services/plugin-loader.ts:1785-1960`, `external/agent-systems/paperclip/server/src/services/plugin-worker-manager.ts:1-19`).
- MCP and CLI should be kept as API clients. Their docs and code point to REST wrappers, so business-rule changes belong in server services and routes, not in separate client logic (`external/agent-systems/paperclip/packages/mcp-server/README.md:1-17`, `external/agent-systems/paperclip/cli/src/client/http.ts:53-180`).
