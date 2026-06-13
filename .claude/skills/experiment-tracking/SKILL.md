---
name: experiment-tracking
description: Use when running, tracking, benchmarking, sweeping, comparing, or evaluating any Bodha component or end-to-end experiment — e.g. "run an extraction sweep", "benchmark these models/prompts", "compare v14c vs v15", "track this calibration", "register this eval run". Triggers whenever an experiment produces params/metrics/output files that should be recorded and compared instead of dumped into ad-hoc folders. Covers MLflow setup, the `track()` toolkit, conventions, and how to view/compare runs.
---

# Experiment Tracking

Track every experiment with the **`bodha.infrastructure.tracking`** toolkit (MLflow-backed). Do **not**
hand-write MLflow plumbing or dump results into ad-hoc `experiments/`/`eval-results/` folders as the
source of truth — the toolkit gives one generic API for any experiment shape.

Policy & conventions: **[`.claude/project/tracking.md`](../../project/tracking.md)**.
Full design + deployment: **[`docs/workstreams/project-ops/experiment-tracking-toolkit-design.md`](../../../docs/workstreams/project-ops/experiment-tracking-toolkit-design.md)**.

## The one API (sequential / local)

```python
from bodha.infrastructure.tracking import track

with track(
    stage="dhriti/signal-extraction",          # MLflow experiment = one per component/stage
    name="v15 | sub-gpt-5.4-mini",             # run name = the comparison grid
    tags={"study": "v14c_vs_v15", "prompt": "v15", "model": "sub-gpt-5.4-mini"},
    params={"prompt_version": "v15", "n_scenarios": 5},
    trace=True,        # autolog LLM calls (pydantic_ai/openai/litellm) for LLM experiments
    provenance=True,   # auto-log git sha/dirty/diff-hash/uv.lock-hash
) as run:
    ...                # your experiment
    run.log_metrics({"grounded_f1": 0.56})     # FLAT metric names (no "/")
    run.log_params({"threshold": 0.5})
    run.set_tag("dataset", "gold_5scenario")
    run.log_table(rows, "per_scenario.json")   # list[dict] per-row results
    run.log_json(summary, "summary.json")      # any JSON-able object
    run.log_file("report.html")                # any file artifact (renders inline)
    run.log_reference("eval-results/.../big.jsonl")  # zero-copy pointer + hash for large in-place files
    with run.span("scenario:X", inputs={...}): # manual trace span; autolog spans nest inside
        ...
```

Tracking is **best-effort**: if MLflow is absent or the server is down, it degrades to a no-op and the
experiment still runs (it never raises). So always wrap real experiment work in `track(...)`.

## Parallel / Temporal (concurrent runs)

Fluent `track()` is **not** concurrency-safe, and model selection in Bodha is a process-global. For
concurrent model sweeps use **one OS process per model** and the explicit-`run_id` form:

```python
from bodha.infrastructure.tracking import get_tracker
tracker = get_tracker()                              # MlflowTracker (or NullTracker if disabled)
run = tracker.create_run(stage, name, tags=..., params=..., parent_run_id=...)
run.log_metrics({...}); run.finish()                 # explicit run_id, no fluent global state
```

## Setup

- Server: the dockerised **`mlflow-stack`** (Postgres-backed) — `docker compose -f infra/mlflow-stack/docker-compose.yml up -d` (bring the dev-stack up first). UI at http://127.0.0.1:5000.
- `mlflow` is an **optional** dependency: run with `uv run --with mlflow ...` or `uv sync --extra tracking`.
- Override the server via `MLFLOW_TRACKING_URI` (or pass `config=TrackingConfig(...)` to `track`).

## Conventions (enforce)

- **One experiment per stage** `<component>/<stage>` (`dhriti/signal-extraction`, `dhriti/matcher-calibration`, …); **one run per config/variant**; the specific study goes in **tags**, not a new experiment.
- **Tags = the compare axis** (`study`, `prompt`, `model`, `dataset`, `sweep_id`, `run_level`). **Params = reproducibility** (handled automatically by `provenance=True`, plus your config).
- **Flat metric names** (`grounded_f1`, not `grounded/f1`).
- **`trace=True`** for LLM experiments; **provenance always on**.

## Scope fence (do NOT overreach)

This toolkit is for **component experiments only**. It must not own: LLM **production tracing** (Langfuse),
operational logs/metrics (Grafana/Alloy/Loki), the **end-to-end memory benchmark** (Pydantic Evals +
Langfuse), or anything on the production hot path.

## View / compare

Open http://127.0.0.1:5000 → the `<component>/<stage>` experiment → add `prompt`/`model` tag columns or
tick runs → **Compare** / Chart view; the **Traces** tab holds the per-scenario LLM-call spans.
