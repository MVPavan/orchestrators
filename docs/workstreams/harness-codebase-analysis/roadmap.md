# Workstream — Codebase-Analysis Tooling Experiment (paperclip)

**Runbook:** [`docs/research/harness/codebase-analysis-exps.md`](../../research/harness/codebase-analysis-exps.md)
**Isolation contract:** [`docs/research/harness/isolation-contract.md`](../../research/harness/isolation-contract.md)
**Subject:** `external/paperclip` (frozen, read-only copy at `scratchpad/harness/_paperclip_src/`).

## Objective

Use 8 codebase-analysis tools as independent *lenses* to understand paperclip as deeply as possible,
then compare them only where capabilities genuinely overlap (capability-first method, not a uniform
benchmark). All experiments **thoroughly isolated** (filesystem + install + visibility).

## Roles

- **Orchestrator (main thread):** scopes, fans out subagents, reviews, synthesizes, enforces isolation.
- **Executors:** Opus 4.8 subagents via Workflow `agent({model:'opus', effort})`, one tool per worker, parallel.
- **Critic:** Codex `gpt-5.5` via codex-adapter, unbiased prompt, iterate until satisfied.

## Phases & gates

| Phase | What | Effort | Done-when |
| --- | --- | --- | --- |
| 0 Setup | Clone tools, build frozen subject, write isolation contract, seed tracking, smoke one tool | orchestrator | 8 tool dirs + snapshot + contract + tracking exist; one tool runs scoped without error |
| A Capability discovery | 8 parallel Opus-medium workers read each tool, write `capabilities.md` | medium | 8 capability cards, each Codex-reviewed |
| B Exploitation | One worker/tool drives it fully vs paperclip, records `exploitation.md` + telemetry | per §3 | every capability exercised + telemetry; isolation respected |
| C Synthesis | Capability×tool matrix, classify unique/overlap/universal, conclusions | xhigh | matrix complete; every conclusion has evidence + Codex sign-off |

## Status (live)

- **Phase 0:** ✅ done — 8 tools cloned; frozen subject built (52MB, 2961 files, read-only); isolation
  contract written + hardened; tracking seeded; ast-grep smoke passed scoped (no global leak / no mutation).
- **Phase A:** ✅ done — 8 capability cards written + Codex (gpt-5.5) unbiased review
  (`results/_phaseA_codex_review.md`); isolation held (subject read-only, no global bins). 4 tools already
  verified-by-running with local-only installs.
- **Phase B:** ✅ done — 8/8 exploitation reports written; all 8 isolation audits clean
  (home-local + no-global-bin + subject-untouched). Independent orchestrator audit caught + removed two
  Phase-A leaks (codegraph `~/.codegraph` telemetry, graphify `~/.cache/graphify-queries.log`) created
  before the HOME-hardening existed; real `$HOME` now clean. Indexes contained in per-tool sandboxes.
- **Phase C:** ✅ done — `findings.md` written (capability×tool matrix, unique/overlap/universal
  classification, firm `isUuidLike` conclusion). Codex `gpt-5.5` adversarial review iterated high→xhigh:
  REVISE (5 must-fixes) → fixes applied + `_isolation_audit.md` added → **SHIP**.

**EXPERIMENT COMPLETE (2026-06-22).** Deliverables: `findings.md`, `isolation-contract.md`,
`results/<tool>/{capabilities,exploitation}.md` ×8, `results/_phaseA_codex_review.md`,
`results/_isolation_audit.md`. All Beads closed (epic `orch-2zt`). Uncommitted (conservative default —
awaiting commit authorization).

**Follow-up: serena re-test on a `pnpm install`ed workspace (bead `orch-aib`, done).** Refuted the
open-question hypothesis: installing the workspace rescues serena's *forward* go-to-definition
(cross-package, now exact) but NOT *reverse* `find_referencing_symbols` (still 1 ref / 0-of-16) — the
cause is **barrel re-export indirection**, not pruning. Serena's last place on the reference/impact axis
stands. Report: `results/serena/retest-installed-workspace.md`. A third isolation leak (serena's
backgrounded MCP server didn't inherit the tool-local `HOME`) was caught and quarantined; real `$HOME`
re-verified clean.

## Headline result

On the universal anchor (`isUuidLike` cross-package callers, ground truth ~16 files = 11 server + 5 ui):
**codebase-memory-mcp** 100% P/R incl UI · **graphify** 94% offline (1 defect) · **understand-anything**
callGraph 89% by name · **codegraph** strong + blast-radius but missed JSX/UI · **serena** collapsed to
~2% on the pruned (un-pnpm-installed) subject · **ast-grep/repomix** lexical superset (44/20), not
semantic. Every semantic tool surfaced a real hazard grep hides: `isUuidLike` is **defined 3×** (shared
canonical plus 2 cli-local shadows). *Note: serena's ~2% was later re-tested — see Follow-up above; the
cause is barrel re-export indirection, not pruning.*

## Shared anchors (for Phase C head-to-head comparison)

- 9 workspace packages; hubs `@paperclipai/shared` (647 importers), `@paperclipai/db` (310).
- Reference/impact anchor: `isUuidLike` (def `packages/shared/src/agent-url-key.ts`) — lexical ground
  truth **45 refs / 21 files** (server 11, ui 5, packages 2, cli 2, doc 1).
- Type anchor: `Company` (`packages/shared/src/types/company.ts`). CLI entrypoint: `cli/src/index.ts`.

## Tracking

Beads epic + per-tool issues + synthesis issue (IDs in `bd list`). Workstream mirrors this roadmap.
