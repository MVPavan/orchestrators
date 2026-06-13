# Repo Map — structure & how to orient

Physical layout + navigation. Design-doc authority is mapped in `docs-index.md`; this file maps the tree.

## Top level

| Path | What |
|---|---|
| `src/bodha/` | The application (component packages below) |
| `tests/` | `unit/` · `integration/` (needs dev-stack) · `invariant/` · `eval/` (harness + component suites) |
| `alembic/` | DB migrations (Postgres) |
| `config/` | YAML config (pydantic-settings) |
| `prompts/` | Versioned LLM prompts (e.g. `prompts/dhriti/extraction/v*.md`) |
| `infra/` | Docker stacks: `dev-stack/` (Postgres, Redis, Neo4j, Qdrant, Oxigraph, LiteLLM) · `embed-stack/` · `mlflow-stack/` · `proxy-setup/` (cli-proxy-api; independent — do not modify) |
| `datasets/` | Benchmark data (docs tracked; raw/normalized gitignored) |
| `experiments/` | Exploratory work, pre-graduation (e.g. `dhriti/ner_rel_grounding/`) |
| `eval-results/` | Eval run outputs (gitignored) |
| `scripts/` | Repo tooling (e.g. `bd-render-tracking.sh`) |
| `viewer/` | Side-by-side signal-extraction viewer (scratch quality, not lint-clean) |
| `docs/` | See below |
| `scratchpad/` | Throwaway work — gitignored, never commit |
| `repos/` | Local reference checkouts — gitignored, not part of the build |

## `src/bodha/` components

| Package | Owns |
|---|---|
| `contracts/` | Shared Pydantic models + enums — the dependency sink; if a dependency feels backwards, the shared type moves here |
| `buddhi/` | Turn orchestration, tool gating, model tiers, Gateway routing |
| `manas/` | Context packing, compression, repacking |
| `dhriti/` | Extraction pipeline: signal capture → grounding guard → claim support → promotion gate → commit |
| `chitta/` | Store authority: schemas, adapters (Postgres/Neo4j/Qdrant/Oxigraph/Redis), projections, overlay |
| `retrieval/` | Dhī intent classification + Smṛti retrieval stages |
| `dharana/` | Background integrity, consolidation, enrichment, revalidation jobs |
| `resolution/` | Entity + vocabulary resolution |
| `agents/` | pydantic-ai agent definitions |
| `capabilities/` | Agent capability middleware (e.g. context_repack) |
| `tools/`, `skills/` | Capability registries (identity infrastructure — bypass Dhṛti) |
| `infrastructure/` | Temporal, gateway, observability, virtual keys |
| `api.py`, `config.py` | Top-level API surface; settings |

Dependency flow (no circular imports): `api.py` → component packages → shared `contracts/`.

## `docs/`

| Path | What |
|---|---|
| `design/` | Versioned architecture specs (`v_2_7/core/` authoritative) + `memory-design-tests/` (DS eval datasets, golden-100) + `component-eval/` (per-component eval design) |
| `workstreams/` | Per-initiative execution: `<name>/{README,roadmap,plans/,tracking/}`; root = bd-generated board (`status/ideas/backlog.md`, read-only) |
| `brainstorms/` | Exploration inbox (dated; `done/` + `rejected/` lifecycle) |
| `plans/` | Cross-cutting plans (e.g. `beads-phase-integration.md`) |
| `reviews/`, `architecture-trace/` | Review + code↔design trace outputs |
| `guides/` | Operational how-tos (proxy-setup) |
| `_archive/` | Frozen history (pre-bd roadmaps/trio, archived to-dos) |

## How to orient on a task

1. `brief.md` — what Bodha is, stack, constraints.
2. `docs-index.md` — which design doc owns the component you're touching.
3. This map → `src/bodha/<component>/` + its tests under `tests/`.
4. Current work: the workstream's `roadmap.md` + bd (`bd ready`); proof commands: `verification.md`.
