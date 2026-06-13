# Docs Index

Status: adopted for v2.7 on 2026-04-07 · refreshed 2026-06-08 (repo now has runnable `src/bodha/` + tests)

## Core Design Documents

| Path | Component | Responsibility | Risk | Authority | Read When |
|------|-----------|----------------|------|-----------|-----------|
| `docs/design/v_2_7/core/bodha-design-v2_7.md` | Common architecture | System-level architecture, contracts, principles, v2.7 extraction hardening, Claude-Mem adoption | high | authoritative | Always first for system-level decisions |
| `docs/design/v_2_7/core/bodha-buddhi-v2_7.md` | Buddhi | Turn orchestration, tool gating, model tiers, Gateway, extraction model routing | high | authoritative | Changing orchestration or model-access behavior |
| `docs/design/v_2_7/core/bodha-manas-v2_7.md` | Manas | Context packing, compression, cache breakpoints, repacking | high | authoritative | Changing prompt packing, context budgets, or repacking |
| `docs/design/v_2_7/core/bodha-retrieval-v2_7.md` | Retrieval | Dhī intent classification and Smṛti retrieval stages | high | authoritative | Changing recall behavior, caching, or retrieval plans |
| `docs/design/v_2_7/core/bodha-dhriti-v2_7.md` | Dhṛti | Extraction, Phase 1.5 grounding verification, evaluation, HOLD, provenance, write-gate | high | authoritative | Changing what gets stored or how memory writes are judged |
| `docs/design/v_2_7/core/bodha-chitta-v2_7.md` | Chitta | Store authority, schemas, adapter boundaries, projections | high | authoritative | Changing schemas, stores, or write/read boundaries |
| `docs/design/v_2_7/core/bodha-dharana-v2_7.md` | Dhāraṇā | Background integrity, consolidation, enrichment, revalidation jobs | high | authoritative | Changing async maintenance or recovery behavior |
| `docs/design/v_2_7/core/bodha-infrastructure-v2_7.md` | Infrastructure | ProjectionEngine, overlay, adapters, Temporal, observability, config, packaging | high | authoritative | Changing infrastructure or deployment surfaces |
| `docs/design/v_2_7/core/bodha-tools-skills-v2_7.md` | Tools and skills | Capability registries, logging, loading, graduation pipeline | high | authoritative | Changing capability discovery or skill lifecycle |
| `docs/design/v_2_7/core/bodha-rag-v2_7.md` | Document RAG | Bookshelf model, multi-RAG routing, document provenance, `sources` behavior | high | authoritative | Changing document retrieval or document-memory interaction |
| `docs/design/v_2_7/core/bodha-job-plan-v2_7.md` | Job plan | Job inventory, ownership, triggers, sequencing, Phase 1.5 verification flow | medium | authoritative | Mapping work to jobs, workers, or failure domains |
| `docs/design/v_2_7/core/memory-benchmarks-v2_7.md` | Benchmarks | Benchmark selection and evaluation coverage | medium | authoritative | Defining memory-quality evaluation strategy |

## Supporting Documents

| Path | Purpose | Authority | Read When |
|------|---------|-----------|-----------|
| `docs/design/v_2_6/core/new_discussions/dhriti-extraction-discussions.md` | Pre-v2.7 extraction tradeoff analysis that informed the hardened extraction pipeline | supporting | Understanding why Phase 1.5 and escalation were introduced |
| `docs/design/v_2_6/core/bodha_subscription_proxy_architecture.md` | Recommended local model-routing topology for subscription-backed access | supporting | Wiring local gateway and provider auth topology |
| `docs/design/v_2_6/core/new_discussions/claude-mem-adoption-log.md` | Claude-Mem adoption decisions partially absorbed into v2.7 common design | supporting | Evaluating sidecar, shadow-log, and progressive-disclosure proposals |
| `infra/dev-stack/litellm_config.yaml` | LiteLLM proxy configuration for local model routing (moved from `infra/proxy-setup/` on 2026-04-10) | supporting | Configuring or debugging model proxy setup |

## Development Planning Documents

| Path | Purpose | Authority | Read When |
|------|---------|-----------|-----------|
| `docs/brainstorms/done/2026-04-07-development-roadmap-requirements.md` | Approved brainstorm (shipped → `done/`): build order, test strategy, scope, Codex-informed decisions | approved | Understanding why the roadmap is structured the way it is |
| `docs/design/v_2_7/core/new_discussions/bodha-pydanticai-temporal-litellm-integration.md` | Source brainstorm for the PydanticAI + TemporalAgent + LiteLLM integration (P0 §0 corrections, C1–C8 facts, §12 hot-path cost-benefit, §12.6 reversibility) | approved | Working on hot-path agents, capability middleware, provider factory, virtual-key flow, or the hot-path deviation |
| `docs/workstreams/dhriti-extraction/README.md` | Dhṛti extraction **arc** — the eval spine + lineage of extraction approaches (Gen 1 **schema-v2 PARKED**; Gen 2 **NER+REL** active in `experiments/`) | canonical | Working on Dhṛti extraction quality, the eval, or any extraction approach |
| `docs/design/component-eval/` | Per-component functional-eval **design** specs (Chitta, Resolution, Retrieval, Manas, Buddhi, Dhāraṇā, Tools) + harness plan — design reference, not bd-tracked | supporting | Designing a component's eval suite |
| `docs/workstreams/<name>/README.md` + `plans/` | Per-workstream charter + per-stage implementation plans | canonical / supporting | Orienting in a workstream; finding a stage's plan |
| `docs/workstreams/status.md` | Global cross-workstream status — **bd-generated, read-only** (do not hand-edit; regenerate via `scripts/bd-render-tracking.sh`) | generated | Checking current state across all workstreams; what's ready next |
| `docs/workstreams/<name>/tracking/{status,checklist,progress}.md` | Per-workstream tracking trio — **bd-generated, read-only** | generated | During implementation |
| `docs/workstreams/{ideas,backlog}.md` | Parked idea/backlog board — **bd-generated** from bd labels | generated | Triaging parked work |
| `docs/plans/beads-phase-integration.md` | The active bd↔phase-workflow integration plan (how roadmaps/phases map into beads) | canonical | Working on the bd integration itself |
| `docs/_archive/2026-06-09-pre-bd/` | Completed pre-bd roadmaps (core 9-phase, pydanticai integration, eval-harness, reviews) + their plans + the old hand-maintained status/checklist/progress trio | frozen | Historical reference only |
| `docs/design/memory-design-tests/v_2/` | Golden evaluation datasets: DS-20, DS-40, DS-80 | authoritative | Validating extraction/retrieval/system quality at phase exits |

Use this file to point agents at the right docs before they guess.

- List only durable docs that materially improve decisions.
- Mark one doc as authoritative when multiple docs overlap.
- Use repo-relative paths only.

Current repo reality: the table above maps the authoritative v2.7 design specs; the implementation lives under `src/bodha/` with tests under `tests/` (unit / integration / invariant / eval), run via `uv` — see `.claude/project/verification.md` for the trusted commands. Infrastructure setup is under `infra/`.
