# Operational Model

## Build And Run

The top-level `make build` target checks dependencies, installs Python dependencies, installs frontend dependencies, installs pre-commit hooks, and builds the frontend (`external/OpenHands/Makefile:32`, `external/OpenHands/Makefile:40`). The repository agent guidance says not to run this unless asked or trying to run the full application (`external/OpenHands/AGENTS.md:4`, `external/OpenHands/AGENTS.md:7`).

Development commands:

- Backend: `make start-backend` runs `poetry run uvicorn openhands.server.listen:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload` (`external/OpenHands/Makefile:259`, `external/OpenHands/Makefile:263`).
- Frontend: `make start-frontend` runs the React Router dev script with backend host and frontend port environment (`external/OpenHands/Makefile:264`, `external/OpenHands/Makefile:274`).
- Full local app: `make run` starts the backend, waits for the port with `nc`, then starts the frontend (`external/OpenHands/Makefile:276`, `external/OpenHands/Makefile:294`).
- Docker app: `make docker-run` exports workspace/sandbox/date variables and invokes `docker compose up` (`external/OpenHands/Makefile:296`, `external/OpenHands/Makefile:308`).

I did not run these commands. They install dependencies, start services, or require Docker/network access, which was unnecessary for a source-grounded architecture pass.

## Test And Lint Surface

The OpenHands repository guidance says backend tests live under `tests/unit/test_*.py` and should be run with `poetry run pytest` for relevant modules; frontend tests use Vitest through `npm run test` (`external/OpenHands/AGENTS.md:123`, `external/OpenHands/AGENTS.md:140`). The Makefile's top-level `test` target currently delegates to `test-frontend`, which runs `cd frontend && npm run test` (`external/OpenHands/Makefile:248`, `external/OpenHands/Makefile:253`).

Pre-push guidance is more extensive than the Makefile's top-level test target. It names backend pre-commit, frontend lint/build, and VSCode extension lint/compile commands depending on touched files (`external/OpenHands/AGENTS.md:24`, `external/OpenHands/AGENTS.md:32`).

For this parent-repo research task, I did not run OpenHands tests because the change is documentation in `/data/codes/orchestrators`, not code inside the external submodule.

## Docker And Packaged App

`docker-compose.yml` builds `containers/app/Dockerfile`, exposes port 3000, mounts the Docker socket, maps `~/.openhands` to `/.openhands`, and mounts the workspace base into `/opt/workspace_base` (`external/OpenHands/docker-compose.yml:2`, `external/OpenHands/docker-compose.yml:24`).

The app Dockerfile has a frontend-builder stage using Node, a backend-builder stage using Python and Poetry, and an `openhands-app` stage that sets runtime environment defaults such as `RUN_AS_OPENHANDS`, `SANDBOX_LOCAL_RUNTIME_URL`, `WORKSPACE_BASE`, `FILE_STORE=local`, `FILE_STORE_PATH=/.openhands`, and `INIT_GIT_IN_EMPTY_WORKSPACE=1` (`external/OpenHands/containers/app/Dockerfile:1`, `external/OpenHands/containers/app/Dockerfile:105`).

The entrypoint requires root unless `NO_SETUP=true`, validates `SANDBOX_USER_ID`, optionally unsets workspace base when no mount path is provided, and either runs as root or creates/runs an `enduser` with Docker socket group access (`external/OpenHands/containers/app/entrypoint.sh:1`, `external/OpenHands/containers/app/entrypoint.sh:61`).

The dev Docker compose is separate, privileged, mounts the source at `/app`, maps host git/npm credentials read-only, and sets the agent-server image tag (`external/OpenHands/containers/dev/compose.yml:1`, `external/OpenHands/containers/dev/compose.yml:40`). Its README warns this mode is community-maintained and not officially supported (`external/OpenHands/containers/dev/README.md:1`, `external/OpenHands/containers/dev/README.md:5`).

## Configuration Template

`config.template.toml` is broad, but the operationally important sections are:

- `[core]`: workspace, cache, file store, browser enablement, budgets, max iterations, runtime, JWT, concurrent conversations, and age limits (`external/OpenHands/config.template.toml:12`, `external/OpenHands/config.template.toml:95`).
- `[agent]`: enabled tools, browsing/editor/Jupyter/command/think/finish flags, prompt extensions, disabled microagents, history truncation, and condensation request (`external/OpenHands/config.template.toml:97`, `external/OpenHands/config.template.toml:140`).
- `[sandbox]`: timeout, user id, image, host network, build args, auto lint, plugins, runtime env vars, platform, mounts, GPU/KVM-adjacent settings, and port choices (`external/OpenHands/config.template.toml:146`, `external/OpenHands/config.template.toml:221`).
- `[security]`: confirmation mode and security analyzer for headless/CLI contexts (`external/OpenHands/config.template.toml:223`, `external/OpenHands/config.template.toml:237`).
- `[mcp]`: SSE, streamable HTTP, and stdio MCP server examples (`external/OpenHands/config.template.toml:344`, `external/OpenHands/config.template.toml:383`).
- `[model_routing]`: experimental router selection (`external/OpenHands/config.template.toml:385`, `external/OpenHands/config.template.toml:394`).

## Enterprise Operations

Enterprise setup and run instructions are separate. The repo guidance lists Python 3.12, Poetry, Node.js 22.x, and optional Docker, then instructs developers to build the main project, install enterprise dependencies, and install enterprise pre-commit hooks (`external/OpenHands/AGENTS.md:174`, `external/OpenHands/AGENTS.md:220`). Enterprise tests use `poetry run --project=enterprise pytest` with xdist/forking and enterprise-specific config, and enterprise server startup uses `cd enterprise && make start-backend` or `make run` (`external/OpenHands/AGENTS.md:196`, `external/OpenHands/AGENTS.md:215`).

Enterprise runtime adds SaaS configuration, analytics startup/shutdown through PostHog, additional middleware, and provider-dependent routers (`external/OpenHands/enterprise/server/app_lifespan/saas_app_lifespan_service.py:19`, `external/OpenHands/enterprise/server/app_lifespan/saas_app_lifespan_service.py:44`, `external/OpenHands/enterprise/saas_server.py:81`, `external/OpenHands/enterprise/saas_server.py:189`).

## Operational Risk Signals

- Dependency and runtime commands are heavy. `make build` installs backend and frontend dependencies and hooks; Docker paths require Docker socket access and container pulls/builds (`external/OpenHands/Makefile:32`, `external/OpenHands/Makefile:40`, `external/OpenHands/docker-compose.yml:18`, `external/OpenHands/docker-compose.yml:22`).
- Runtime behavior depends strongly on environment variables. Defaults choose Docker sandbox unless `RUNTIME=remote` or `RUNTIME=local/process`, and storage selection changes event persistence (`external/OpenHands/openhands/app_server/config.py:307`, `external/OpenHands/openhands/app_server/config.py:394`).
- Local GUI packaged mode gives the application Docker socket access to manage sandbox containers (`external/OpenHands/docker-compose.yml:18`, `external/OpenHands/docker-compose.yml:20`).
- Enterprise explicitly warns that stacking middleware and overriding implementations can be brittle (`external/OpenHands/enterprise/README.md:15`, `external/OpenHands/enterprise/README.md:20`, `external/OpenHands/enterprise/README.md:49`, `external/OpenHands/enterprise/README.md:56`).

## Parent Repo Caveats

This research was conducted from `/data/codes/orchestrators`, and `external/OpenHands` was treated as an external source tree. The parent repository should only receive research artifacts under `docs/research/codebases/openhands/`; no OpenHands source, lockfile, generated frontend output, or submodule content should be modified for this task.

Verification for this task should focus on:

- Output file existence under `docs/research/codebases/openhands/`.
- Absence of placeholder or draft-marker artifacts in the generated research files.
- Source-reference sanity: each cited `external/OpenHands/...:line` path exists and line numbers are in range.
- `git -C external/OpenHands status --short --branch` remains clean.
- Parent `git status --short --branch` shows only intended docs/Beads changes.
