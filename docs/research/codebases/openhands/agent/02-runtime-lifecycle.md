# Runtime Lifecycle

## ASGI Startup

Local and Docker workflows still invoke `uvicorn openhands.server.listen:app`, but `openhands/server/listen.py` is a compatibility module that re-exports the app from `openhands.app_server.app` (`external/OpenHands/Makefile:259`, `external/OpenHands/Makefile:262`, `external/OpenHands/containers/app/Dockerfile:104`, `external/OpenHands/containers/app/Dockerfile:105`, `external/OpenHands/openhands/server/listen.py:1`, `external/OpenHands/openhands/server/listen.py:7`).

The real app boot sequence is:

1. Load global app-server configuration from environment-derived injectors (`external/OpenHands/openhands/app_server/config.py:240`, `external/OpenHands/openhands/app_server/config.py:431`).
2. Initialize the Tavily MCP proxy before app construction if configured (`external/OpenHands/openhands/app_server/app.py:30`, `external/OpenHands/openhands/app_server/mcp/mcp_router.py:49`, `external/OpenHands/openhands/app_server/mcp/mcp_router.py:76`).
3. Mount the MCP HTTP app and combine its lifespan with the configured application lifespan (`external/OpenHands/openhands/app_server/app.py:33`, `external/OpenHands/openhands/app_server/app.py:48`, `external/OpenHands/openhands/app_server/app.py:59`).
4. Include the V1 and health routers, optionally mount the built frontend, and install middleware (`external/OpenHands/openhands/app_server/app.py:71`, `external/OpenHands/openhands/app_server/app.py:86`).
5. In OSS mode, the default lifespan runs Alembic migrations on startup (`external/OpenHands/openhands/app_server/app_lifespan/oss_app_lifespan_service.py:12`, `external/OpenHands/openhands/app_server/app_lifespan/oss_app_lifespan_service.py:38`).

## Frontend Conversation Creation

The frontend `useCreateConversation()` mutation calls `V1ConversationService.createConversation()` and receives a start task rather than a final conversation id (`external/OpenHands/frontend/src/hooks/mutation/use-create-conversation.ts:30`, `external/OpenHands/frontend/src/hooks/mutation/use-create-conversation.ts:71`). The API wrapper posts to `/api/v1/app-conversations` and documents the expected polling contract: poll `getStartTask()` until the task becomes `READY` to obtain the conversation id (`external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:55`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:108`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:111`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:126`).

The route-level task polling hook recognizes URLs of the form `/conversations/task-{uuid}`, polls every three seconds until `READY` or `ERROR`, and navigates to `/conversations/{conversation-id}` on readiness (`external/OpenHands/frontend/src/hooks/query/use-task-polling.ts:7`, `external/OpenHands/frontend/src/hooks/query/use-task-polling.ts:21`, `external/OpenHands/frontend/src/hooks/query/use-task-polling.ts:31`, `external/OpenHands/frontend/src/hooks/query/use-task-polling.ts:59`).

## Backend Conversation Startup

`POST /api/v1/app-conversations` starts an async generator, stores enough request state to keep DB and HTTP resources open, returns the first start task, and consumes the rest in the background (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:360`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:407`).

The generator then performs the main lifecycle:

1. Resolve user id/email and inherit parent conversation configuration if requested (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:247`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:267`).
2. Create and yield an `AppConversationStartTask` (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:270`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:274`).
3. Wait for an existing or new sandbox (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:276`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:285`).
4. Seed user LLM profiles into the sandbox profile store before conversation creation (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:287`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:291`).
5. Compute working directory, optionally group by conversation id, and run setup scripts through a remote workspace (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:299`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:317`).
6. Build the SDK start request using user settings, secrets, LLM, MCP config, tools, hooks, plugins, conversation settings, and skills (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:319`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:335`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:1312`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:1561`).
7. Post the request JSON to the sandbox agent-server at `/api/conversations` using the sandbox session key if present (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:342`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:371`).
8. Persist `AppConversationInfo`, save default and requested event callback processors, mark the start task `READY`, and process pending messages (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:391`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:444`).

Failures during startup are caught, redacted, and written onto the start task as `ERROR` detail rather than escaping only through logs (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:446`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:450`).

## Repository And Workspace Setup

Setup runs inside the sandbox through `AsyncRemoteWorkspace`. The service computes a project root: selected repositories resolve to `{working_dir}/{repo_name}`, while empty workspaces use `working_dir` directly (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:53`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:84`).

`run_setup_scripts()` then advances the task through these stages:

- `PREPARING_REPOSITORY`: create the workspace and either initialize git or clone the selected repository with authenticated credentials (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:247`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:281`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:319`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:405`).
- `RUNNING_SETUP_SCRIPT`: execute `.openhands/setup.sh` from the project root if available (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:502`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:519`).
- `SETTING_UP_GIT_HOOKS`: install OpenHands' pre-commit hook while preserving an existing hook as `.git/hooks/pre-commit.local` when needed (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:521`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:576`).
- `SETTING_UP_SKILLS`: ask the agent-server to load public, user, project, org, and sandbox skills (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:273`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:280`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:97`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_service_base.py:159`).

## Sandbox Lifecycle

The shared `SandboxService` interface defines search, get, session-key lookup, start, resume, pause, delete, and batch-get operations (`external/OpenHands/openhands/app_server/sandbox/sandbox_service.py:30`, `external/OpenHands/openhands/app_server/sandbox/sandbox_service.py:91`, `external/OpenHands/openhands/app_server/sandbox/sandbox_service.py:201`). Its `wait_for_sandbox_running()` helper polls until the sandbox is `RUNNING` and optionally verifies the agent-server `/alive` endpoint (`external/OpenHands/openhands/app_server/sandbox/sandbox_service.py:93`, `external/OpenHands/openhands/app_server/sandbox/sandbox_service.py:140`).

Docker mode creates containers from sandbox specs, injects session key/webhook/CORS environment, maps exposed ports, mounts configured volumes, and returns `SandboxInfo` from Docker state (`external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:381`, `external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:512`). The default Docker injector exposes `AGENT_SERVER` on 8000, VSCode on 8001, and worker ports on 8011/8012 (`external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:578`, `external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:714`).

Remote mode stores a local record for runtime facts the remote API does not provide or preserve for stopped runtimes, then maps runtime API responses into the same `SandboxInfo` shape (`external/OpenHands/openhands/app_server/sandbox/remote_sandbox_service.py:73`, `external/OpenHands/openhands/app_server/sandbox/remote_sandbox_service.py:186`). Configuration selects remote, process/local, or Docker sandbox services from `RUNTIME` when explicit injectors are not provided (`external/OpenHands/openhands/app_server/config.py:332`, `external/OpenHands/openhands/app_server/config.py:394`).

## Follow-Up Runtime Operations

Once a conversation is running, app-server endpoints are mostly proxies and metadata guards:

- `send-message` requires a running sandbox and forwards the message to the agent-server events endpoint (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:426`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:587`).
- Runtime endpoints such as VSCode URL, pause/resume, ask-agent, upload-file, and runtime conversation info are called directly from frontend client methods using `conversation_url` and the session API key (`external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:165`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:235`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:272`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:353`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:520`).
- The frontend stores the active conversation in `ConversationService` so runtime-specific endpoints can include the current session API key (`external/OpenHands/frontend/src/api/conversation-service/conversation-service.api.ts:10`, `external/OpenHands/frontend/src/api/conversation-service/conversation-service.api.ts:50`, `external/OpenHands/frontend/src/hooks/query/use-active-conversation.ts:26`, `external/OpenHands/frontend/src/hooks/query/use-active-conversation.ts:35`).

