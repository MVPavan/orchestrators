# OpenHands Codebase Architecture Research

Analysis date: 2026-06-14
Target path: `external/OpenHands`
Source commit: `2d34bb7ce650b633a2f970bc076c1a5fae2f84a9`
Source branch status at read time: `main...origin/main`, clean

## System Purpose

OpenHands is an AI software-engineering platform with several distribution surfaces. The local source tree studied here contains the Local GUI, which the README describes as a laptop-oriented REST API plus single-page React application (`external/OpenHands/README.md:47`, `external/OpenHands/README.md:48`, `external/OpenHands/README.md:51`). The same README names the SDK and CLI as separate source locations, so this pass treats the local repository as an app-server, frontend, runtime-orchestration, integrations, and enterprise overlay codebase around pinned SDK and agent-server packages, not as the full implementation of every OpenHands product surface (`external/OpenHands/README.md:34`, `external/OpenHands/README.md:39`, `external/OpenHands/README.md:41`, `external/OpenHands/README.md:45`, `external/OpenHands/pyproject.toml:248`, `external/OpenHands/pyproject.toml:251`).

Cloud and Enterprise are represented by source-available code in `enterprise/`; the README calls out Slack, Jira, Linear, multi-user support, RBAC, permissions, and conversation sharing for Cloud, and warns that `enterprise/` is licensed separately from the MIT core (`external/OpenHands/README.md:53`, `external/OpenHands/README.md:63`, `external/OpenHands/README.md:64`, `external/OpenHands/README.md:69`, `external/OpenHands/README.md:82`).

## Reading Map

- `01-core-architecture.md`: architectural thesis, module map, dependency direction, and what is core versus peripheral.
- `02-runtime-lifecycle.md`: ASGI startup, frontend-to-backend conversation startup, sandbox lifecycle, agent-server calls, and follow-up message/runtime flows.
- `03-data-state-and-persistence.md`: configuration, database/session model, metadata tables, events, settings, secrets, sandbox records, and enterprise tenant state.
- `04-integration-and-extension-points.md`: API, MCP, git providers, LLM profiles, sandboxes, skills, hooks, plugins, frontend, and enterprise integration surfaces.
- `05-operational-model.md`: build, run, test, Docker, configuration, enterprise operations, and parent-repo/submodule caveats.
- `90-open-questions.md`: unresolved questions, inferred areas, and follow-up work.
- `../html/index.html`: human review summary derived from this Markdown set.

## Core Architecture In 12 Points

1. The backend is Python and the frontend is React; the repository guidance names those roots directly (`external/OpenHands/AGENTS.md:1`, `external/OpenHands/AGENTS.md:2`).
2. The command still launched by local and container workflows is `openhands.server.listen:app`, but that module is now a deprecated compatibility wrapper that re-exports the real app from `openhands.app_server.app` (`external/OpenHands/Makefile:259`, `external/OpenHands/Makefile:262`, `external/OpenHands/openhands/server/listen.py:1`, `external/OpenHands/openhands/server/listen.py:7`).
3. The ASGI app mounts a FastMCP HTTP app at `/mcp`, includes the V1 router and health router, optionally serves `frontend/build`, and adds localhost CORS, cache-control, and in-memory rate-limit middleware (`external/OpenHands/openhands/app_server/app.py:30`, `external/OpenHands/openhands/app_server/app.py:59`, `external/OpenHands/openhands/app_server/app.py:71`, `external/OpenHands/openhands/app_server/app.py:86`).
4. `/api/v1` is a router aggregate over events, app conversations, pending messages, sandbox and sandbox specs, settings, secrets, user, skills, webhooks, web client config, git, and server config (`external/OpenHands/openhands/app_server/v1_router.py:23`, `external/OpenHands/openhands/app_server/v1_router.py:37`).
5. Configuration is environment-derived and dependency-injected. `AppServerConfig` declares injectors for LLM model service, event storage, callbacks, sandbox, sandbox specs, conversation metadata, start tasks, live conversation service, pending messages, user context, JWT, HTTP, DB session, lifespan, and web client config (`external/OpenHands/openhands/app_server/config.py:191`, `external/OpenHands/openhands/app_server/config.py:237`).
6. The app-server is an orchestration layer around an agent-server. V1 conversation startup yields a durable start task, waits for or starts a sandbox, runs repository setup, builds a `StartConversationRequest`, posts it to the sandbox's agent-server, stores conversation metadata, registers callbacks, then drains queued pending messages (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:235`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:242`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:276`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:435`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:437`).
7. Conversation metadata and start-task models are first-class app-server state, distinct from live sandbox/agent-server state (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:106`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:165`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:240`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:280`).
8. Sandboxes abstract runtime placement. The shared model exposes statuses, named service URLs, session API keys, and timestamps; Docker and remote implementations both adapt external runtime facts into that model (`external/OpenHands/openhands/app_server/sandbox/sandbox_models.py:9`, `external/OpenHands/openhands/app_server/sandbox/sandbox_models.py:30`, `external/OpenHands/openhands/app_server/sandbox/sandbox_models.py:48`, `external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:381`, `external/OpenHands/openhands/app_server/sandbox/remote_sandbox_service.py:98`).
9. State is deliberately split: SQL stores conversation metadata/start tasks/callbacks/pending messages, event bodies can live in filesystem/S3/GCS style event services, and local settings/secrets default to JSON files behind a `FileStore` (`external/OpenHands/openhands/app_server/services/db_session_injector.py:166`, `external/OpenHands/openhands/app_server/event/event_service_base.py:47`, `external/OpenHands/openhands/app_server/settings/file_settings_store.py:17`, `external/OpenHands/openhands/app_server/secrets/file_secrets_store.py:17`).
10. The frontend uses React Router routes for login, launch, settings, conversation, shared conversation, and related screens, with TanStack Query hooks wrapping API clients as a stated architecture rule (`external/OpenHands/frontend/src/routes.ts:8`, `external/OpenHands/frontend/src/routes.ts:49`, `external/OpenHands/AGENTS.md:148`, `external/OpenHands/AGENTS.md:154`).
11. Skills, hooks, and plugins are extension points. The app-server calls the agent-server to load skills and hooks, while conversation requests can include SDK plugin sources and user-provided plugin parameters (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:97`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:147`, `external/OpenHands/openhands/app_server/app_conversation/hook_loader.py:1`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:62`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:72`).
12. Enterprise is an overlay, not a forked app. `enterprise/saas_server.py` imports the base app, sets SaaS config defaults, registers additional routes/middleware, overrides `/api/v1/users/me`, and mounts the SPA last (`external/OpenHands/enterprise/saas_server.py:7`, `external/OpenHands/enterprise/saas_server.py:13`, `external/OpenHands/enterprise/saas_server.py:67`, `external/OpenHands/enterprise/saas_server.py:145`, `external/OpenHands/enterprise/saas_server.py:186`).

## Scope Limits

- This pass did not run OpenHands, install dependencies, pull containers, or call network services.
- The SDK, CLI, and agent-server internals were treated as external packages except where this repo imports, pins, configures, or calls them.
- Frontend behavior was sampled at routing/API/query boundaries, not exhaustively traced component by component.
- Enterprise was mapped as an overlay and tenant/auth/integration surface, not audited line-by-line across all migrations or providers.
- `external/OpenHands` was treated as a read-only external submodule/source tree and was not modified.

