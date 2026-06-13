# Verification Commands

Status: adopted for v2.7 on 2026-04-07 · refreshed 2026-06-08 (repo now has runnable `src/bodha/` + tests)

Bodha is a runnable Python project managed with `uv`. These are the trusted commands that prove a
change is complete — the source of truth the `verification-before-completion` gate reads to pick the
command that proves a claim. Run the tier that matches the work, and read the **exit status**, not just
the output. Do not invent a weaker substitute (e.g. a doc-existence check) when a code check applies.

Scope notes (non-obvious — do not drift from these):

- Everything runs under `uv run`.
- `ruff` targets `src tests` only. `experiments/`, `viewer/`, and `scripts/` are scratch and are
  intentionally **not** lint-clean — `ruff check .` (whole tree) is not the gate.
- `mypy` targets `src` only. Tests are not strict-typed (`mypy src tests` is expected to be noisy).
- `pytest` defaults to `-m "not integration"`. Integration tests require the dev-stack (see below).

## Code checks (the default "is it done?")

- Quick (inner loop):
  - `uv run ruff check src tests`
  - `uv run pytest -m "not integration" -q`
- Full (before a commit / phase exit / PR):
  - `uv run ruff check src tests`
  - `uv run ruff format --check src tests`
  - `uv run mypy src`
  - `uv run pytest -m "not integration"`
- Invariants:
  - `uv run pytest tests/invariant`
  - `/check-invariants`  (runs the mechanized registry in `.claude/project/invariants.md`)
- Integration (only with the dev-stack up):
  - `docker compose -f infra/dev-stack/docker-compose.yml up -d`  (if not already running)
  - `uv run pytest -m integration`

Every code-check command must **exit 0**. A non-zero exit is a failed verification — report the actual
output; do not claim completion. There is no CI yet, so these commands are the gate.

## Design-doc / roadmap consistency (only for docs/design, roadmap, or overlay edits)

Use these when the change is to design docs, a roadmap, or the `.claude/project/` overlay — never as a
substitute for the code checks above:

- `find docs/design/v_2_7/core -maxdepth 1 -name '*.md' | sort`
- `rg -n "^## \[INV-" .claude/project/invariants.md`
- Workstream status is **bd-generated** — verify it reflects reality via `bd epic status --json` (or re-run `BD_RENDER=1 bash scripts/bd-render-tracking.sh`), not by reading `docs/workstreams/status.md` for hand-edited markers.
- Human review of `.claude/project/brief.md` and `.claude/project/docs-index.md` against the latest
  authoritative design docs.

Run the repo's own scripts or CI-equivalent commands when they exist. Do not invent a weaker substitute.
