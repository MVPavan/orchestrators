# Integration And Extension Points

## CLI Surface

The primary integration surface is the `gt` CLI. It is a Cobra command tree rooted at `internal/cmd/root.go`; the root can change its name based on `GT_COMMAND`, which supports wrapper binaries or aliases (`external/gastown/internal/cmd/root.go:25`, `external/gastown/internal/cmd/root.go:33`). Core command groups include:

- `gt install`: create a town/HQ (`external/gastown/internal/cmd/install.go:50`).
- `gt rig`: add/list/start/stop/restart/status project containers (`external/gastown/internal/cmd/rig.go:37`).
- `gt crew`: create and attach to persistent user workspaces (`external/gastown/internal/cmd/crew.go:29`).
- `gt sling`: dispatch work to agents, formulas, dogs, or target rigs (`external/gastown/internal/cmd/sling.go:25`).
- `gt done`: complete polecat work and submit/close merge flow (`external/gastown/internal/cmd/done.go:30`).
- `gt mq submit`: create/refine Beads-backed MRs (`external/gastown/internal/cmd/mq_submit.go:78`).
- `gt doctor`, `gt health`, `gt quota`, `gt estop`, `gt thaw`, `gt seance`, `gt mail`, `gt nudge`, `gt hook`: operational and communication surfaces (`external/gastown/internal/cmd/root.go:43`).

Important caveat: root pre-run side effects mean commands can update liveness and telemetry. External automation should not assume all `gt` invocations are pure reads (`external/gastown/internal/cmd/root.go:117`, `external/gastown/internal/cmd/root.go:144`).

## Agent Runtime Registry

Agent support is registry-driven. `AgentPresetInfo` is the single source of truth for agent command, args, env, process names, session resume behavior, hook support, config dirs, readiness, instruction file, permission warnings, turn-boundary draining, and ACP config (`external/gastown/internal/config/agents.go:55`). Built-ins include Claude, Gemini, Codex, Cursor, Auggie, AMP, OpenCode, Copilot, Pi, OMP, Mistral Vibe, and Groq Compound (`external/gastown/internal/config/agents.go:22`).

Notable presets:

- Claude uses `claude --dangerously-skip-permissions`, supports hooks and fork sessions, uses `CLAUDE.md`, `.claude/settings.json`, and turn-boundary draining (`external/gastown/internal/config/agents.go:229`).
- Gemini uses `gemini --approval-mode yolo`, supports hooks, uses `AGENTS.md`, and marks Escape as request-cancelling (`external/gastown/internal/config/agents.go:255`).
- Codex uses `codex -c <update-check-config> --dangerously-bypass-approvals-and-sandbox`, has `codex resume` subcommand style, non-interactive `exec --json`, no hooks, and uses `AGENTS.md` (`external/gastown/internal/config/agents.go:279`).

Runtime agent resolution happens from town/rig settings and role/worker overrides. The loader has explicit functions for default agent, role agent, worker agent, override resolution, role settings dirs, and startup command generation (`external/gastown/internal/config/loader.go:1128`, `external/gastown/internal/config/loader.go:1351`, `external/gastown/internal/config/loader.go:1383`, `external/gastown/internal/config/loader.go:1544`, `external/gastown/internal/config/loader.go:2620`).

## Hook And Settings Installation

`internal/hooks` is a generic hook/settings installer for all agent runtimes. It embeds templates and chooses a target based on the agent preset's hooks provider, hooks dir, hooks file, role, and whether the agent uses a separate settings dir (`external/gastown/internal/hooks/installer.go:1`, `external/gastown/internal/hooks/installer.go:21`, `external/gastown/internal/hooks/installer.go:24`).

Key behavior:

- `InstallForRole` creates hook/settings files or upgrades stale files, but avoids overwriting current files during session startup (`external/gastown/internal/hooks/installer.go:24`).
- `SyncForRole` is the explicit sync path for `gt hooks sync` and can update stale templates; it avoids the Claude JSON merge path when that would clobber role overrides (`external/gastown/internal/hooks/installer.go:92`).
- Template resolution supports role-aware autonomous/interactive templates and role-agnostic single templates (`external/gastown/internal/hooks/installer.go:203`).
- Writes are atomic to avoid concurrent spawn corruption (`external/gastown/internal/hooks/installer.go:134`).

Template providers exist for Claude, Codex, Copilot, Cursor, Gemini, OMP, OpenCode, and Pi under `internal/hooks/templates`.

## Plugins

Plugins are filesystem directories with `plugin.md`. `internal/plugin/sync.go` copies source plugin directories to runtime plugin directories, optionally removes stale targets in clean mode, hashes directory contents for drift detection, and can locate Gastown source plugins from the current source tree or town runtime paths (`external/gastown/internal/plugin/sync.go:21`, `external/gastown/internal/plugin/sync.go:43`, `external/gastown/internal/plugin/sync.go:91`, `external/gastown/internal/plugin/sync.go:179`).

The architecture implication: plugins are runtime-distributed content, not Go packages linked into the binary. Install and rig add provision plugin directories, while `make install` also syncs plugins from the source repo to runtime dirs (`external/gastown/internal/cmd/install.go:315`, `external/gastown/internal/rig/manager.go:899`, `external/gastown/Makefile:125`).

## ACP / Provider Protocol Surface

Gas Town has an Agent Communication Protocol layer:

- `internal/agent/provider` defines provider state, status, tool callbacks, session start callbacks, and an `ACPProvider` interface with initialize, list tools, call tool, create message, status, and close (`external/gastown/internal/agent/provider/provider.go:10`, `external/gastown/internal/agent/provider/provider.go:31`).
- `internal/agent/provider/acp.go` defines JSON-RPC messages, ACP roles, content blocks, tool schema, initialize/list/call/create-message types, and helpers (`external/gastown/internal/agent/provider/acp.go:36`, `external/gastown/internal/agent/provider/acp.go:76`, `external/gastown/internal/agent/provider/acp.go:141`, `external/gastown/internal/agent/provider/acp.go:193`).
- `internal/acp/proxy.go` launches an agent process, wires stdin/stdout/stderr, tracks handshake/startup prompt/heartbeat/propulsion state, forwards JSON-RPC, and handles keepalive/shutdown (`external/gastown/internal/acp/proxy.go:42`, `external/gastown/internal/acp/proxy.go:181`, `external/gastown/internal/acp/proxy.go:303`).

This looks like a lower-level integration path for agents that support ACP natively or through a subcommand/flag, configured via `AgentPresetInfo.ACP` (`external/gastown/internal/config/agents.go:169`).

## External Services And Subprocesses

Important subprocess/service boundaries:

- `bd` CLI plus Beads Go SDK for issue storage (`external/gastown/internal/beads/beads.go:1`, `external/gastown/go.mod:18`).
- Dolt SQL server for Beads persistence (`external/gastown/docs/design/architecture.md:148`, `external/gastown/go.mod:113`).
- Git and git worktree operations through `internal/git` and subprocess calls from rig/polecat/refinery flows (`external/gastown/docs/design/architecture.md:135`, `external/gastown/internal/rig/manager.go:420`).
- tmux session creation, readiness, nudges, theming, process killing, and auto-respawn (`external/gastown/internal/deacon/manager.go:23`, `external/gastown/internal/witness/manager.go:239`).
- PR providers for GitHub/Bitbucket in refinery PR merge mode (`external/gastown/internal/refinery/pr_provider.go`, `external/gastown/internal/refinery/pr_provider_github.go`, `external/gastown/internal/refinery/pr_provider_bitbucket.go`).
- Optional OpenTelemetry export for daemon metrics/logs (`external/gastown/internal/daemon/daemon.go:96`).

## Environment Variables And Runtime Contracts

Material env contracts include:

- `GT_TOWN_ROOT` and `GT_ROOT` for town discovery and child session context (`external/gastown/internal/cmd/root.go:120`, `external/gastown/internal/daemon/daemon.go:248`).
- Dolt env: `GT_DOLT_PORT`, `BEADS_DOLT_PORT`, `GT_DOLT_HOST`, `BEADS_DOLT_SERVER_HOST` (`external/gastown/internal/daemon/daemon.go:303`).
- Agent identity env from `config.AgentEnv`, including role/rig/worker/session and runtime provider variables (`external/gastown/internal/config/env.go:79`).
- Runtime config dirs such as `CLAUDE_CONFIG_DIR`, derived from accounts configuration for role sessions (`external/gastown/internal/witness/manager.go:164`).
- `GT_SESSION` and role env used by root pre-run heartbeat updates (`external/gastown/internal/cmd/root.go:201`).
- ACP debug/runtime env through proxy paths, including `GT_ACP_DEBUG` as indicated by stderr capture comments (`external/gastown/internal/acp/proxy.go:212`).

## Compatibility Risks

- Agent CLIs change command flags, resume behavior, process names, and readiness prompts. Gas Town centralizes this in presets, but each preset is still a compatibility contract with an external CLI (`external/gastown/internal/config/agents.go:55`).
- Hooks differ by provider. Some support executable lifecycle hooks, some are informational only, and Codex currently has `SupportsHooks: false` in the built-in preset (`external/gastown/internal/config/agents.go:98`, `external/gastown/internal/config/agents.go:131`, `external/gastown/internal/config/agents.go:287`).
- Beads CLI output/version compatibility is handled through shims but remains an external dependency (`external/gastown/internal/beads/beads.go:54`, `external/gastown/internal/beads/beads.go:123`).
- Dolt server mode is mandatory for daemon operation; embedded fallback should not be assumed (`external/gastown/docs/design/architecture.md:150`, `external/gastown/internal/daemon/daemon.go:1057`).

