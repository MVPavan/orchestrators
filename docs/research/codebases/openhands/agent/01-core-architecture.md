# Core Architecture

## Architectural Thesis

OpenHands local GUI is best understood as an orchestration application around the OpenHands SDK and agent-server, not as a monolith that executes every agent operation inside the web process. The app-server owns user/session configuration, metadata, persistence, routing, sandbox lifecycle, extension loading, and provider integration. The actual running conversation is started in a sandbox-hosted agent-server through HTTP calls that include a fully built SDK `StartConversationRequest` (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:319`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:369`).

The local repository explicitly pins the SDK, agent-server, and tools packages at `1.28.0`, while the README points the SDK and CLI source to separate repositories (`external/OpenHands/pyproject.toml:248`, `external/OpenHands/pyproject.toml:251`, `external/OpenHands/README.md:34`, `external/OpenHands/README.md:45`). That makes the app-server/runtime boundary the main architecture boundary for this codebase.

## Source Layout

- `openhands/app_server/`: current V1 app-server implementation. It contains the real ASGI app, routers, service interfaces, injectors, conversation lifecycle, sandbox adapters, stores, and integration glue.
- `openhands/server/`: compatibility wrappers. `listen.py` re-exports `openhands.app_server.app:app` (`external/OpenHands/openhands/server/listen.py:1`, `external/OpenHands/openhands/server/listen.py:7`).
- `frontend/`: React SPA. Package metadata shows React 19, React Router 7, TanStack Query, Axios, Monaco, xterm, Zustand, HeroUI, i18n, and Vite/React Router build tooling (`external/OpenHands/frontend/package.json:1`, `external/OpenHands/frontend/package.json:46`, `external/OpenHands/frontend/package.json:54`, `external/OpenHands/frontend/package.json:65`).
- `skills/`: shareable Markdown skills/microagents. The README states this directory backs V1 "skills" and V0 "microagents" terminology (`external/OpenHands/skills/README.md:1`, `external/OpenHands/skills/README.md:14`, `external/OpenHands/skills/README.md:31`).
- `enterprise/`: source-available SaaS/Enterprise overlay. Its README says enterprise stacks middleware on top of OpenHands in SaaS mode and overrides implementations through dynamic imports (`external/OpenHands/enterprise/README.md:13`, `external/OpenHands/enterprise/README.md:20`).
- `containers/`, `docker-compose.yml`, `config.template.toml`, `Makefile`: operational entry points for local, Docker, and packaged app workflows.

## Backend Composition

The app entry point performs four high-value actions:

1. Initialize the Tavily MCP proxy before app creation (`external/OpenHands/openhands/app_server/app.py:30`, `external/OpenHands/openhands/app_server/app.py:31`).
2. Build a FastMCP HTTP app at `/mcp` and combine its lifespan with the configured app lifespan (`external/OpenHands/openhands/app_server/app.py:33`, `external/OpenHands/openhands/app_server/app.py:36`, `external/OpenHands/openhands/app_server/app.py:51`).
3. Create a FastAPI app, mount `/mcp`, and include V1 plus health routers (`external/OpenHands/openhands/app_server/app.py:54`, `external/OpenHands/openhands/app_server/app.py:59`, `external/OpenHands/openhands/app_server/app.py:71`, `external/OpenHands/openhands/app_server/app.py:72`).
4. Optionally mount `frontend/build` and add middleware (`external/OpenHands/openhands/app_server/app.py:75`, `external/OpenHands/openhands/app_server/app.py:86`).

The V1 router then delegates to feature routers instead of embedding behavior directly. That is an important architectural property: API shape is centralized, but ownership remains in module-specific routers and services (`external/OpenHands/openhands/app_server/v1_router.py:23`, `external/OpenHands/openhands/app_server/v1_router.py:37`).

## Dependency Direction

The dominant dependency direction is:

`routers -> injected service interfaces -> configured implementations -> sandbox/agent-server/storage/provider clients`.

`AppServerConfig` is the registry for this direction. It contains typed injector fields and defaults them from environment in `config_from_env()` (`external/OpenHands/openhands/app_server/config.py:191`, `external/OpenHands/openhands/app_server/config.py:240`, `external/OpenHands/openhands/app_server/config.py:285`, `external/OpenHands/openhands/app_server/config.py:420`). The global config singleton then exposes dependency functions such as `get_sandbox_service`, `get_app_conversation_service`, `get_pending_message_service`, and `get_user_context` (`external/OpenHands/openhands/app_server/config.py:426`, `external/OpenHands/openhands/app_server/config.py:489`, `external/OpenHands/openhands/app_server/config.py:497`, `external/OpenHands/openhands/app_server/config.py:505`).

This means extension and deployment behavior is usually achieved by replacing injectors or store classes, not by changing routers. Enterprise uses the same pattern: `SaaSServerConfig` overrides settings store, secrets store, auth class, and analytics user provider (`external/OpenHands/enterprise/server/config.py:55`, `external/OpenHands/enterprise/server/config.py:68`).

## Conversation Service As The Core Domain

The `AppConversationService` is the domain center. The models show the separation:

- `AppConversationInfo` is persisted metadata: conversation id, owner, sandbox id, repository/branch/provider, title, trigger, PRs, LLM model, agent kind, metrics, parent/subconversation links, public flag, tags, and timestamps (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:106`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:134`).
- `AppConversation` enriches metadata with live sandbox status, execution status, conversation URL, and session API key (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:151`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:165`).
- `AppConversationStartTask` captures slow startup progress and links the eventual conversation id after readiness (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:240`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:280`).

The router is deliberately thin around this service. `POST /app-conversations` starts the async generator, returns the first task immediately, and background-consumes the remaining startup steps while keeping DB and HTTP clients open (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:360`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:403`).

## Runtime Boundary

A running conversation is only usable if a sandbox can expose an `AGENT_SERVER` URL. `_get_agent_server_context()` loads app metadata, gets the sandbox, rejects paused/non-running states, retrieves a sandbox spec, finds the `AGENT_SERVER` exposed URL, rewrites localhost for Docker, and returns the session API key (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:130`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:213`).

That boundary appears again in the follow-up message endpoint: the app-server validates metadata and sandbox state, then posts to the agent-server's `/api/conversations/{id}/events` with the sandbox session API key (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:426`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:587`).

## Core Versus Peripheral

Core for architecture:

- `openhands/app_server/app.py`, `v1_router.py`, `config.py`, `shared.py`, and `server_config/server_config.py`.
- `app_conversation/*`, especially `live_status_app_conversation_service.py`, `app_conversation_router.py`, `app_conversation_service_base.py`, and SQL services.
- `sandbox/*`, especially the shared model/service interface and Docker/remote/process injectors.
- `event/*`, `event_callback/*`, `pending_messages/*`, settings/secrets stores, and DB session injectors.
- `integrations/*`, `mcp/*`, and user/auth context modules because they mediate external systems into conversation startup and callbacks.
- `frontend/src/api`, `frontend/src/hooks/query`, `frontend/src/hooks/mutation`, `frontend/src/routes.ts`, and state stores because they define the browser-to-app-server contract.
- `enterprise/server/config.py`, `enterprise/saas_server.py`, SaaS auth/store/injector modules, and migrations because they change the deployment model.

Lower priority for this architecture pass:

- Visual components and styling except where route/API ownership is clarified.
- Release workflows, translation details, generated frontend artifacts, and documentation-only marketing pages.
- Individual provider implementation internals unless they define a common interface or cross-cutting callback path.

