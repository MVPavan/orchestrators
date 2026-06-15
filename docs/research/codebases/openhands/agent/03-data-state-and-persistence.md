# Data, State, And Persistence

## Configuration State

The app-server reads configuration from environment using SDK `from_env(AppServerConfig, 'OH')`, with explicit fallback support for legacy variables such as `OH_PERSISTENCE_DIR`, `FILE_STORE_PATH`, `WEB_HOST`, `PERMITTED_CORS_ORIGINS`, `OPENHANDS_PROVIDER_BASE_URL`, `LLM_BASE_URL`, `TAVILY_API_KEY`, and `SEARCH_API_KEY` (`external/OpenHands/openhands/app_server/config.py:75`, `external/OpenHands/openhands/app_server/config.py:129`, `external/OpenHands/openhands/app_server/config.py:240`, `external/OpenHands/openhands/app_server/config.py:285`).

When no persistence path is provided, the default is `~/.openhands`, and the directory is created as part of config defaulting (`external/OpenHands/openhands/app_server/config.py:75`, `external/OpenHands/openhands/app_server/config.py:89`). This is a source fact; the actual runtime path in a given deployment depends on environment and was not observed in this pass.

## SQL Session Model

The DB injector chooses:

- GCP Cloud SQL when GCP instance settings are present.
- PostgreSQL via `asyncpg`/`pg8000` when `host` is configured.
- SQLite under `{persistence_dir}/openhands.db` when no database host is configured (`external/OpenHands/openhands/app_server/services/db_session_injector.py:166`, `external/OpenHands/openhands/app_server/services/db_session_injector.py:210`, `external/OpenHands/openhands/app_server/services/db_session_injector.py:212`, `external/OpenHands/openhands/app_server/services/db_session_injector.py:248`).

Sessions are reused through request state where possible and are committed or rolled back at dependency teardown unless a caller marks the session as keep-open for background work (`external/OpenHands/openhands/app_server/services/db_session_injector.py:285`, `external/OpenHands/openhands/app_server/services/db_session_injector.py:328`). `POST /app-conversations` uses that keep-open mechanism because conversation startup continues after the initial HTTP response (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:371`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_router.py:373`).

## Conversation Metadata

OSS V1 conversation metadata lives in `conversation_metadata`, represented by `StoredConversationMetadata` in the SQL app conversation info service. It includes conversation id, sandbox id, repository/branch/provider, title, trigger, PR numbers, LLM model, agent kind, token/cost metrics, parent id, public flag, tags, timestamps, and `conversation_version` (`external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_info_service.py:65`, `external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_info_service.py:118`). Save operations write `conversation_version='V1'` (`external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_info_service.py:347`, `external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_info_service.py:388`).

A notable source fact: the OSS `_secure_select()` filters only `conversation_version == 'V1'`; the conversion method explicitly returns `created_by_user_id=None` with a comment that user id now lives in SaaS metadata (`external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_info_service.py:514`, `external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_info_service.py:552`). That does not prove an OSS security bug by itself because OSS default auth is not multi-tenant; it is an architecture difference to track.

Start-task state is its own table/service. The model stores task status, detail, eventual conversation id, sandbox id, agent-server URL, original request, and timestamps (`external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:259`, `external/OpenHands/openhands/app_server/app_conversation/app_conversation_models.py:283`). The SQL start-task service persists these fields in `app_conversation_start_task` (`external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_start_task_service.py:54`, `external/OpenHands/openhands/app_server/app_conversation/sql_app_conversation_start_task_service.py:75`).

## Events And Callbacks

Event bodies are stored by an `EventService` abstraction. The base service computes a per-conversation path under the configured prefix, optionally under a user id, then under the V1 conversations directory and conversation id (`external/OpenHands/openhands/app_server/event/event_service_base.py:47`, `external/OpenHands/openhands/app_server/event/event_service_base.py:65`). The filesystem implementation reads and writes JSON files at those paths (`external/OpenHands/openhands/app_server/event/filesystem_event_service.py:17`, `external/OpenHands/openhands/app_server/event/filesystem_event_service.py:42`).

Provider selection for event storage is done in `config_from_env()`: AWS uses an S3-backed event injector, GCP uses a Google Cloud injector, and the default is filesystem (`external/OpenHands/openhands/app_server/config.py:307`, `external/OpenHands/openhands/app_server/config.py:328`). The local file store itself performs atomic writes through temp-file plus `os.replace` (`external/OpenHands/openhands/app_server/file_store/local.py:26`, `external/OpenHands/openhands/app_server/file_store/local.py:43`).

Event callbacks are SQL-backed. Callback execution loads active callbacks matching conversation and event kind, runs processors concurrently, and persists results; callback exceptions become error results instead of escaping only as uncaptured exceptions (`external/OpenHands/openhands/app_server/event_callback/sql_event_callback_service.py:48`, `external/OpenHands/openhands/app_server/event_callback/sql_event_callback_service.py:90`, `external/OpenHands/openhands/app_server/event_callback/sql_event_callback_service.py:208`, `external/OpenHands/openhands/app_server/event_callback/sql_event_callback_service.py:250`).

## Settings And Secrets

`Settings` is the main persisted user/session configuration model. It contains product settings, `agent_settings`, `conversation_settings`, sandbox grouping, `disabled_skills`, search/sandbox keys, LLM profiles, and the V1 enable flag (`external/OpenHands/openhands/app_server/settings/settings_models.py:114`, `external/OpenHands/openhands/app_server/settings/settings_models.py:155`). Updates are constrained: raw `agent_settings` and `conversation_settings` replacement is rejected in favor of diff payloads, and `llm_profiles` is intentionally ignored by generic settings updates (`external/OpenHands/openhands/app_server/settings/settings_models.py:104`, `external/OpenHands/openhands/app_server/settings/settings_models.py:111`, `external/OpenHands/openhands/app_server/settings/settings_models.py:195`, `external/OpenHands/openhands/app_server/settings/settings_models.py:277`).

OSS `FileSettingsStore` reads and writes `settings.json` through the configured file store, seeds a default LLM profile from legacy settings, and forces V1 enabled on load (`external/OpenHands/openhands/app_server/settings/file_settings_store.py:12`, `external/OpenHands/openhands/app_server/settings/file_settings_store.py:56`). OSS `FileSecretsStore` similarly reads and writes `secrets.json`, dropping provider-token entries that lack a token (`external/OpenHands/openhands/app_server/secrets/file_secrets_store.py:12`, `external/OpenHands/openhands/app_server/secrets/file_secrets_store.py:45`).

Enterprise replaces these with SaaS stores through config. `SaaSSettingsStore` resolves effective organization context, merges organization defaults with member diffs, handles private agent settings separately, resolves effective LLM API keys, and surfaces organization LLM profiles through `Settings.llm_profiles` (`external/OpenHands/enterprise/storage/saas_settings_store.py:68`, `external/OpenHands/enterprise/storage/saas_settings_store.py:278`). `SaaSSecretsStore` stores custom secrets per `(user_id, org_id)`, encrypts/decrypts values through JWT service, and deletes/reinserts secrets for the effective org on store (`external/OpenHands/enterprise/storage/saas_secrets_store.py:17`, `external/OpenHands/enterprise/storage/saas_secrets_store.py:151`).

## Pending Messages

Pending messages are SQL-backed queue items keyed by conversation id. They are used when the frontend sends messages before a start task has resolved to a real conversation. After conversation creation, `_process_pending_messages()` rewrites queued `task-{uuid}` messages to the real conversation id, posts them sequentially to the agent-server events endpoint, and deletes them regardless of per-message success (`external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:1719`, `external/OpenHands/openhands/app_server/app_conversation/live_status_app_conversation_service.py:1800`).

Enterprise wraps this with user and organization ownership checks against `conversation_metadata_saas` before adding/counting/getting pending messages (`external/OpenHands/enterprise/server/utils/saas_pending_message_injector.py:26`, `external/OpenHands/enterprise/server/utils/saas_pending_message_injector.py:188`).

## Sandbox State

`SandboxInfo` contains live runtime status, exposed URLs, and session API key; `SandboxRecord` contains only persisted identity fields for authentication/ownership paths (`external/OpenHands/openhands/app_server/sandbox/sandbox_models.py:33`, `external/OpenHands/openhands/app_server/sandbox/sandbox_models.py:71`). Docker mode derives most sandbox state from Docker container status, environment, image tag, and exposed ports (`external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:115`, `external/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py:232`).

Remote mode adds a local SQL table `v1_remote_sandbox` because the remote runtime API does not return all needed variables and does not list stopped runtimes; the remote API remains the source of truth for what is currently running (`external/OpenHands/openhands/app_server/sandbox/remote_sandbox_service.py:73`, `external/OpenHands/openhands/app_server/sandbox/remote_sandbox_service.py:96`).

## Enterprise Tenant State

Enterprise adds an explicit `conversation_metadata_saas` table containing conversation id, user id, and org id, with indexes for user/org lookup (`external/OpenHands/enterprise/storage/stored_conversation_metadata_saas.py:20`, `external/OpenHands/enterprise/storage/stored_conversation_metadata_saas.py:48`). Migrations show V1 tables added in migration 076 and org/tenant conversation metadata added in migration 089 (`external/OpenHands/enterprise/migrations/versions/076_add_v1_tables.py:28`, `external/OpenHands/enterprise/migrations/versions/076_add_v1_tables.py:201`, `external/OpenHands/enterprise/migrations/versions/089_create_org_tables.py:167`, `external/OpenHands/enterprise/migrations/versions/089_create_org_tables.py:180`).

`SaasSQLAppConversationInfoService` joins base conversation metadata with SaaS metadata, filters by user id and effective org id, and writes SaaS metadata on save (`external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py:30`, `external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py:116`, `external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py:353`, `external/OpenHands/enterprise/server/utils/saas_app_conversation_info_injector.py:430`).

