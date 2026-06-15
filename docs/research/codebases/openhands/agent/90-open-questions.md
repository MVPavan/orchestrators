# Open Questions And Follow-Up Work

## High-Signal Open Questions

| Question | Status | Why It Matters | Suggested Follow-Up |
| --- | --- | --- | --- |
| What exactly lives inside the pinned `openhands-sdk`, `openhands-agent-server`, and `openhands-tools` packages? | Open | This repo builds requests and calls the agent-server, but agent execution semantics live behind the package boundary. | Inspect the matching SDK/agent-server source at version `1.28.0` or vendor package contents. |
| How do deployed environment values differ from defaults? | Open | Runtime choice, DB backend, storage provider, CORS, web URL, provider base URL, and sandbox mode are all env-sensitive. | Collect a representative OSS local config and SaaS/Enterprise config with secrets redacted. |
| Is OSS conversation metadata intentionally unscoped by user? | Partially answered | The OSS SQL service filters V1 but does not appear to user-filter; Enterprise adds explicit user/org filtering. This may be acceptable for single-user OSS, but it is an important boundary. | Confirm threat model and intended OSS deployment assumptions with maintainers or tests. |
| What is the full remote runtime API contract? | Open | `RemoteSandboxService` adapts a legacy runtime HTTP protocol, but this pass only traced the app-server adapter. | Read remote runtime service docs/source and exercise start/list/pause/resume/delete with a test server. |
| Which frontend workflows still rely on direct runtime URLs rather than app-server proxies? | Partially answered | Direct runtime calls require correct `conversation_url`, session API key handling, and browser reachability. | Search all `buildRuntimeUrl`, direct `axios`, and `conversation_url` uses in the frontend. |
| Are all enterprise provider callbacks tenant-scoped consistently? | Open | Enterprise adds user/org scoping for conversations and pending messages, but each provider integration can add callback paths. | Review provider-specific callback processors and tests under `enterprise/integrations/*` and `enterprise/tests/unit`. |
| How stable is V1 versus V0 terminology and compatibility? | Open | The skills README says V1 skills are not yet released while code is clearly V1-heavy, and compatibility wrappers still exist. | Check current release notes/docs and decide which terms should be used in downstream docs. |

## Claims That Are Inferences

- OpenHands Local GUI is an orchestration shell around SDK/agent-server packages. This is inferred from README product boundaries, pyproject pins, and code paths that build SDK requests and POST to sandbox agent-server endpoints (`external/OpenHands/README.md:34`, `external/OpenHands/pyproject.toml:248`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:342`).
- OSS mode appears single-user or weakly multi-tenant compared with SaaS. This is inferred from the default `DefaultUserAuth`/file stores and the absence of user filtering in the OSS SQL metadata service, contrasted with Enterprise SaaS filtering. It is not a full security verdict (`external/OpenHands/openhands/app_server/server_config/server_config.py:17`, `external/OpenHands/openhands/app_server/server_config/server_config.py:27`, `external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py:51`, `external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py:116`).
- The app-server is intended to stay mostly thin around running-agent actions. This is inferred from the send-message endpoint's own design note and frontend direct runtime URL helpers (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:461`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:467`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:29`, `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts:35`).

## Areas Deliberately Not Audited

- Full component-by-component frontend behavior and visual design.
- Full provider implementation internals across GitHub, GitLab, Bitbucket, Jira, Linear, Slack, Azure DevOps, and Enterprise SSO.
- Every Alembic migration. I sampled V1 and tenant-related migrations only.
- Real Docker/runtime execution, dependency installation, browser workflows, and network calls.
- Security review of token encryption, JWT details, provider token refresh, callback auth, or API key storage.
- Performance/capacity analysis of polling, DB indexes, sandbox limits, and event storage.

## Recommended Next Reads

- `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py`
- `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py`
- `external/OpenHands/openhands/app_server/config.py`
- `external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py`
- `external/OpenHands/openhands/app_server/sandbox/remote_sandbox_service.py`
- `external/OpenHands/openhands/app_server/event_callback/sql_event_callback_service.py`
- `external/OpenHands/openhands/app_server/integrations/provider.py`
- `external/OpenHands/openhands/app_server/mcp/mcp_router.py`
- `external/OpenHands/frontend/src/api/conversation-service/v1-conversation-service.api.ts`
- `external/OpenHands/frontend/src/hooks/query/use-task-polling.ts`
- `external/OpenHands/enterprise/saas_server.py`
- `external/OpenHands/enterprise/server/config.py`
- `external/OpenHands/enterprise/server/auth/saas_user_auth.py`
- `external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py`

