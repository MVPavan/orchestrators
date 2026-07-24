# Capability-fixture operation policy

## Allowed without additional approval

- Read the frozen public CLI help, version, configuration help, MCP
  initialization, tool/resource/prompt lists, and schemas.
- Index and query only the assigned disposable fixture copy.
- Write indexes, caches, state, logs, and outputs only below its assigned
  `scratchpad/code-intelligence/` lane.
- Use offline public status, health, export, visualization, graph query, source
  evidence, and failure-reporting capabilities.
- Apply `synthetic-change.patch`, run public change analysis or incremental
  update, and restore/recreate state only inside the disposable fixture copy.
- Invoke the fixed probe through one fresh ephemeral `gpt-5.6-terra` session at
  `medium` reasoning effort, with the evaluated public interface as its only
  code-intelligence access.

## Restricted unless separately approved

- Network access, remote APIs, paid model backends, provider credentials,
  GitHub writes, external databases, telemetry, or cloud synchronization.
- Global installation, system-package changes, or writes to a real home,
  global cache/configuration, or live MCP configuration.
- Deletes or mutations outside the assigned disposable clone and lane.
- Indexing or changing a live submodule, parent-repository source, Pi, Codex, or
  a tool implementation checkout.
- Credential-bearing, destructive, remote, or unbounded optional capabilities.

Restricted capabilities are inventoried with prerequisites and the reason they
were not executed. `NOT_APPLICABLE` means the public capability does not apply
to this question. `UNAVAILABLE` means it applies and is exposed but its declared
runtime prerequisite is absent. Neither status is a failure when justified.

## Identical-run contract

Each tool receives a fresh byte-identical fixture repository, the same fixed
prompt, `probe-output.schema.json`, model `gpt-5.6-terra`, effort `medium`,
Codex CLI runtime version, one answer turn, no repair turn, and a maximum of 24
evaluated-interface calls. Tool-specific adapter instructions may map an
operation to that tool's public name, but may not add facts, questions, hints,
anchors, source access, or extra turns. If the public tool cannot represent a
question, the agent uses the capability-specific status instead of receiving a
replacement private operation.

The runner validates the JSON Schema and then runs
`validate-probe-output.py`. A response with duplicated/reordered question IDs,
more than 24 operations, or non-contiguous/duplicate operation sequence values
is invalid rather than silently normalized.

The evaluated interface independently enforces the limit before dispatch:
requests one through 24 may reach the configured public server or command;
request 25 is logged as `CALL_LIMIT_REJECTED` and returned as an error without
execution. Native lanes use a stdio JSON-RPC proxy. CLI lanes use only an
explicit public-operation allowlist and argv templates, executed without a
shell. Configured executables and cwd must be absolute, the cwd must be the
isolated fixture, and credential-like environment fields are rejected.

The generated provider schema is only a transport adapter. Passing requires
provider-schema validation, canonical-schema validation, and the canonical
sequence validator. Provider JSONL, usage, interface audit, final validation,
and a fail-closed contamination/status artifact are retained for every run.

## Contamination and exclusions

A capability probe is contaminated and excluded if the agent sees another
tool's output, `expected-anchors.json`, Pi/Codex source or reports, tool
implementation source, a source-only reference answer, generic shell/search/
file-read results, or a non-public/hidden tool surface. Unexpected network or
credential access and any live-submodule mutation also invalidate the run.

Fixture-preparation, index/build, schema enumeration, this one-off probe-design
session, tool smokes, failed runner setup, and repair sessions are
`DISCOVERY_SETUP` or `SMOKE_EXCLUDED`; they are never included in the later
controlled source-only-versus-assisted measurements. Provider usage and local
artifact token estimates remain separate and are never summed.
