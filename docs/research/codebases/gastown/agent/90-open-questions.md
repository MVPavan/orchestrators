# Open Questions And Follow-Up

## Remaining Unknowns

1. Exact production path for batch-then-bisect adoption across all refinery commands.
   - Confirmed: `batch.go` implements batch assembly, stack building, retry, bisection, and fast-forward flow (`external/gastown/internal/refinery/batch.go:190`).
   - Still worth checking: which patrol/formula path chooses batch mode versus single-MR mode under current config, and how widely it is enabled in real towns.

2. Full `gt prime` content generation path.
   - Confirmed: docs say only town-root identity anchors exist and full context is injected by `gt prime` via SessionStart hook (`external/gastown/docs/design/architecture.md:131`).
   - Follow-up: trace `internal/cmd/prime*`, role directives, PRIME templates, and hook templates together.

3. Formula/molecule/wisp execution semantics.
   - Confirmed: dispatch cooks formulas and instantiates formula/wisp state (`external/gastown/internal/cmd/sling_dispatch.go:274`), and README describes formulas/molecules as workflow templates (`external/gastown/README.md:82`).
   - Follow-up: read `internal/formula`, `internal/wisp`, and molecule docs to map step state, gate handling, and retry/skip semantics.

4. Deacon patrol internals.
   - Confirmed: daemon starts Deacon with a prompt to run `gt deacon heartbeat` and then patrol through hooks (`external/gastown/internal/deacon/manager.go:109`).
   - Follow-up: read `internal/cmd/deacon*`, `internal/deacon/heartbeat.go`, `stuck.go`, `redispatch.go`, and patrol molecule definitions.

5. Wasteland/federation readiness.
   - Confirmed: README describes Wasteland as a federated work coordination network through DoltHub (`external/gastown/README.md:115`).
   - Follow-up: read `internal/wasteland` and docs before relying on it as implemented runtime capability.

6. ACP compatibility with each built-in agent.
   - Confirmed: ACP provider/proxy structures exist and `AgentPresetInfo` has an `ACP` config field (`external/gastown/internal/agent/provider/provider.go:31`, `external/gastown/internal/acp/proxy.go:42`, `external/gastown/internal/config/agents.go:169`).
   - Follow-up: inspect which presets actually define ACP config and run ACP tests if this integration matters.

7. Hook behavior per agent provider.
   - Confirmed: templates exist for several providers and installer logic is generic (`external/gastown/internal/hooks/installer.go:21`, `external/gastown/internal/hooks/installer.go:203`).
   - Follow-up: inspect each provider template and tests, especially Codex because the built-in Codex preset says `SupportsHooks: false` while Codex hook templates exist in the repo (`external/gastown/internal/config/agents.go:287`).

8. Beads schema/custom type drift.
   - Confirmed: constants define custom types and statuses, but Beads itself is an external dependency (`external/gastown/internal/constants/constants.go:167`, `external/gastown/go.mod:18`).
   - Follow-up: run `bd` compatibility checks in a real town and compare current Beads version behavior with wrapper assumptions.

## Inferred Claims

- Gas Town's durable "source of truth" is distributed across Beads/Dolt, git, filesystem config, and tmux, rather than a single application database. This is an inference from architecture docs plus code paths that initialize/write each store.
- Daemon is not intended to dispatch every normal wake. This is supported by comments that normal wake is handled by feed subscription while daemon is a recovery safety net (`external/gastown/internal/daemon/daemon.go:48`, `external/gastown/internal/daemon/daemon.go:485`).
- Agent runtime support is meant to be added through preset metadata plus optional hook installer templates, rather than ad hoc provider switches. This follows comments in `AgentPresetInfo` (`external/gastown/internal/config/agents.go:55`), but a full grep for provider-specific switches would be useful before enforcing this as a hard invariant.

## Suggested Next Reads

- `external/gastown/internal/cmd/prime*.go` and `internal/templates`: context generation.
- `external/gastown/internal/formula`, `internal/wisp`, `docs/concepts/molecules.md`: workflow templates and molecule state.
- `external/gastown/internal/deacon/*`, `internal/cmd/deacon*.go`: patrol implementation.
- `external/gastown/internal/hooks/templates/*`: provider-specific hook behavior.
- `external/gastown/internal/wasteland/*`: federated coordination.
- `external/gastown/internal/web`, `internal/tui`: observation surfaces if UI review becomes necessary.
- `external/gastown/internal/refinery/engineer.go` around batch selection and patrol loops: production merge mode selection.

