# Open Questions And Drift Risks

## Confirmed Gaps In This Pass

- I did not deep-trace `internal/extmsg`, `internal/convergence`, `internal/mail`, `internal/convoy`, or `internal/graphroute`. They are core-adjacent, but the dominant runtime path was already large enough to prioritize supervisor, sessions, beads, providers, formulas, sling, orders, and events.
- I did not validate generated OpenAPI or TypeScript dashboard output. The report relies on source architecture and Huma registration claims, not a regenerated spec diff.
- I did not run the upstream Gas City test suite. This was a source-grounded architecture research pass from the parent repo, not an upstream code-change validation pass.
- I did not inspect every runtime provider deeply. Tmux, subprocess, ACP, auto, and hybrid were sampled; K8s, Cloudflare, t3bridge, and exec providers need separate targeted reads before provider-specific changes.

## Claims That Are Inference

- "Bead-backed desired-state engine" is an inference from the combined `DesiredStateResult`, `CityRuntime.tick`, and `session_reconciler.go` paths (`external/gascity/cmd/gc/build_desired_state.go:28`, `external/gascity/cmd/gc/city_runtime.go:1040`, `external/gascity/cmd/gc/session_reconciler.go:1`). It is not a quoted phrase from the codebase.
- "Configured provider is not identical to selected implementation" is inferred from `OpenStoreAtForCity` selecting native/file/exec/bd fallback based on preflight and options (`external/gascity/internal/beads/factory.go:76`, `external/gascity/internal/beads/factory.go:156`).
- "Dashboard is peripheral" is inferred from the architecture spec describing it as a static SPA over the supervisor API, not a control-plane owner (`external/gascity/specs/architecture.md:121`, `external/gascity/specs/architecture.md:132`).

## Architectural Risks

- Worker-boundary migration is still active. Upstream guidance says `worker.Handle` is canonical for session lifecycle, while some direct `session.Manager` construction remains in API paths (`external/gascity/AGENTS.md:201`, `external/gascity/AGENTS.md:218`). Changes near sessions should verify whether the path is expected to use worker handles or an allowed direct manager exception.
- The system has many safety gates around partial store reads, provider liveness, drain ack, pending interactions, and assigned work. Simplifying these paths without characterization tests is likely to cause destructive drains or stuck sessions.
- Config/reload behavior depends on provenance, includes, packs, order scans, store metadata changes, and soft reload acceptance. A change that looks like "only config parsing" can affect runtime watchers and reconciliation (`external/gascity/internal/config/compose.go:106`, `external/gascity/internal/config/compose.go:220`; `external/gascity/cmd/gc/city_runtime.go:1597`, `external/gascity/cmd/gc/city_runtime.go:1695`).
- Event logs are best-effort. Building hard correctness on event presence alone would be risky (`external/gascity/internal/events/events.go:1`, `external/gascity/internal/events/events.go:9`).
- Default `bd` storage introduces external process/service dependencies and multiple implementation paths. Tests should pin provider mode intentionally.

## Follow-Up Reads

- `internal/convergence/handler.go` and related files: needed to explain bounded iterative refinement beyond the tick hooks.
- `internal/extmsg/` and `cmd/gc/cmd_mail.go`: needed for external messaging/mail architecture.
- `internal/runtime/k8s`, `internal/runtime/cloudflare`, `internal/runtime/t3bridge`, `internal/runtime/exec`: provider-specific lifecycle and state differences.
- `internal/api/handler_*.go` plus `internal/api/client.go`: full API mutation fallback semantics and async request result contracts.
- `cmd/gc/session_reconciler_trace_*`: how operators should inspect reconciliation decisions in practice.
- `engdocs/architecture/*`: useful for intended invariants, but always cross-check implementation because upstream `AGENTS.md` explicitly says docs are a reference and should be updated when DX/code wins (`external/gascity/AGENTS.md:86`, `external/gascity/AGENTS.md:87`).

## Suggested Experiments

- Run `make test-integration-huma` in the submodule with isolated `GC_HOME` to confirm the supervisor API path from binary startup through `/health`, `/openapi.json`, and `gc cities` still works (`external/gascity/Makefile:403`, `external/gascity/Makefile:405`; `external/gascity/TESTING.md:186`, `external/gascity/TESTING.md:192`).
- Run a file-store smoke city with `GC_BEADS=file` to observe session bead creation, order tracking, and `.gc/events.jsonl` without Dolt/bd dependencies (`external/gascity/README.md:65`, `external/gascity/README.md:67`).
- For provider work, compare the same session lifecycle under tmux, subprocess, and ACP. Their `runtime.Provider` contract is shared, but attach/readiness/interaction guarantees differ (`external/gascity/internal/runtime/tmux/adapter.go:64`, `external/gascity/internal/runtime/subprocess/subprocess.go:14`, `external/gascity/internal/runtime/acp/acp.go:100`).
- For store work, characterize the same bead operation under file, bd CLI fallback, and native Dolt where available.

## Do Not Assume

- Do not assume `gc start` always owns the long-running control loop. The default path registers a city with the machine supervisor (`external/gascity/cmd/gc/cmd_start.go:472`, `external/gascity/cmd/gc/cmd_start.go:563`).
- Do not assume a live runtime session means the expected agent process is healthy. The reconciler distinguishes running and alive and records zombie crashes (`external/gascity/cmd/gc/session_reconciler.go:1409`, `external/gascity/cmd/gc/session_reconciler.go:1431`).
- Do not assume missing work means no demand if store query partial flags are set (`external/gascity/cmd/gc/build_desired_state.go:58`, `external/gascity/cmd/gc/build_desired_state.go:67`).
- Do not assume order triggers are pure timers. They can be event, condition subprocess, cooldown, cron with catch-up, or manual (`external/gascity/internal/orders/triggers.go:50`, `external/gascity/internal/orders/triggers.go:258`).
- Do not assume submodule-local upstream workflow instructions apply to the parent `orchestrators` repo. Parent repo instructions control parent-level research artifacts.
