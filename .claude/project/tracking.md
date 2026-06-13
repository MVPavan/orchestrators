# Experiment Tracking — Bodha policy

Durable conventions for the `bodha.infrastructure.tracking` toolkit. The triggerable workflow lives in
the **`experiment-tracking`** skill; the full design + Docker deployment in
**[`docs/workstreams/project-ops/experiment-tracking-toolkit-design.md`](../../docs/workstreams/project-ops/experiment-tracking-toolkit-design.md)**.
This file holds only the rules that must not drift.

## What it is

- A generic, MLflow-backed tracker. One API (`track(...)`) for **any** experiment shape — sweeps,
  calibration curves, scoring grids, dataset builds, judge panels, live traced runs.
- **Vendor-neutral adapter** (`ExperimentTracker` Protocol + `MlflowTracker` + `NullTracker`), mirroring
  `infrastructure/observability/langfuse.py`. MLflow is **lazy-imported** and an **optional** dependency.
- **Best-effort, degrade-don't-block:** if MLflow is missing or the server is down, tracking becomes a
  no-op and the experiment still runs — tracking never raises into experiment logic (mirror invariant 34).

## Rules

- **Use `track(...)`** for experiments; never hand-roll MLflow plumbing or treat ad-hoc
  `experiments/`/`eval-results/` folders as the durable source of truth.
- **One experiment per stage** `<component>/<stage>`; **one run per config/variant**. The specific study
  is a **tag** (`study`, `sweep_id`), never a new experiment.
- **Tags = the compare axis** (`study`, `prompt`, `model`, `dataset`, `sweep_id`, `run_level`).
  **Params = reproducibility** — `provenance=True` auto-logs git sha + dirty + diff-hash + `uv.lock` hash;
  add your own config params on top.
- **Flat metric names** (`grounded_f1`, not `grounded/f1`) — they show as plain columns in the UI.
- **`trace=True`** for LLM experiments (autolog `pydantic_ai`/`openai`/`litellm`).
- **Sequential → `track()`** (fluent). **Concurrent → `create_run()`/`open_run()`** (explicit `run_id`) +
  **one OS process per model** (fluent runs aren't concurrency-safe; model selection is a process global).

## Scope fence (hard boundary)

The toolkit owns **component experiments only**. It must **not** own:

- **LLM production tracing** → Langfuse (the declared stack tool).
- **Operational logs/metrics** → Grafana + Alloy + Loki.
- **End-to-end memory benchmark** → Pydantic Evals + Langfuse (`tests/eval/harness/`).
- **Any production hot path** → tracking is a batch/experiment side-effect, never inline in a request.

## Deployment & access

- Server = the dockerised **`mlflow-stack`** (`infra/mlflow-stack/`), Postgres-backed (reuses
  `bodha-postgres`), localhost-only on `:5000`. Bring the dev-stack up first, then
  `docker compose -f infra/mlflow-stack/docker-compose.yml up -d`.
- Code = `src/bodha/infrastructure/tracking/`. Install MLflow for clients via `uv run --with mlflow` or
  `uv sync --extra tracking`. Override the server with `MLFLOW_TRACKING_URI` or an injected
  `TrackingConfig`.
- **PII:** traces and tables can carry raw conversation content — the server stays localhost-only; never
  put raw content or secrets in params/tags.
