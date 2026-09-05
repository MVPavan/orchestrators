# Shared capability fixture and Terra probe protocol

Status: frozen Phase 0B input
Recorded: 2026-07-24
Tracking: `orch-8sk.16.6`

This protocol is the common input for CodeGraph, CBM, and Graphify capability
discovery. It freezes a small mixed TypeScript/Rust subject, reference-only
anchors, one synthetic change, one tool-neutral agent prompt, output and metric
schemas, and the allowed-operation boundary. It does not report any tool result.

## Frozen artifacts

| Artifact | Purpose |
| --- | --- |
| `fixture/` | Canonical source corpus; it is never indexed in place |
| `fixture-manifest.sha256` | SHA-256 and relative path for every copied source file and the synthetic patch |
| `fixture-manifest.digest` | SHA-256 of the manifest itself |
| `synthetic-change.patch` | Applies a required `WorkResult.attempts` field to all constructors |
| `expected-anchors.json` | Curator-only scoring anchors; never passed to a probe agent |
| `probe-prompt.md` | Identical questions and one-turn/24-call budget for all tools |
| `probe-output.schema.json` | Required agent answer shape |
| `probe-output.provider.schema.json` | Generated Codex transport schema; canonical validation still wins |
| `generate-provider-schema.py` | Deterministic provider adapter and semantic-equivalence check |
| `metrics.schema.json` | Runner-measured provider, artifact, operation, time, and contamination fields |
| `operations-policy.md` | Allowed, restricted, identical-run, and exclusion rules |
| `prepare-fixture.sh` | Deterministic generation and verification of three isolated Git repositories |
| `validate-probe-output.py` | Portable semantic check for question order and unique contiguous operation sequences |
| `evaluated-interface.py` | Pre-dispatch 24-call gate for native MCP and allowlisted CLI lanes |
| `run-terra-probe.py` | Clean Terra invocation, JSONL/usage capture, and fail-closed validation |
| `test_runner.py` | Fake-server/command and output-validation self-tests |
| `adapter-policies/` | Materializable CodeGraph, CBM, and Graphify dry policies plus the materialized-policy schema |

## Fixture coverage

The fixture contains TypeScript `core` and `gateway` packages and a Rust policy
crate. It deliberately covers direct and transitive calls, TypeScript
interfaces and a Rust trait with implementations, handler inheritance, engine
composition, callback/event flow, two unrelated `normalize` bindings, dynamic
handler lookup, a concrete Node child-process launcher with a runtime-selected
command, two entry points, and persistence-like transition history. Exact
control, data, trust, and failure anchors are documented only in the
curator-owned `expected-anchors.json`; the indexed Markdown is deliberately
neutral and incomplete so it cannot leak the scoring key. The fixture also
contains the deliberately unknown `.capfixture` input.

The TypeScript gateway spawns the command selected by
`FIXTURE_POLICY_COMMAND`, or the PATH-resolved `fixture-policy` fallback. It
sends `fixture-policy-v1|ACTOR`; the dependency-free Rust entry point parses
that delimiter protocol and replies `fixture-policy-v1|RESULT`. There is no
statically resolvable TypeScript-to-Rust symbol call. A tool must distinguish
source/graph facts, documentation-only statements, and inference. The
synthetic patch affects every `WorkResult` constructor and is used only in a
disposable clone.

## Preparation

From the parent-repository root:

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/capabilities/prepare-fixture.sh prepare
```

The command refuses to replace an existing target. It creates:

```text
scratchpad/code-intelligence/fixtures/codegraph
scratchpad/code-intelligence/fixtures/cbm
scratchpad/code-intelligence/fixtures/graphify
```

Each copy contains identical bytes, its own explicitly SHA-1 `.git`, the frozen
source manifest and manifest digest, a deterministic 40-character initial
commit, and clean status. `verify` checks hashes, the patch, Git cleanliness and
commit identity, and byte equality across copies:

- fixture commit: `e7ddad2c44321f7b50e60c923b8f0733fb757874`;
- manifest digest: `fc12b07aa2219f346ee1e00f52875efae8c52bbb12dc410456e9457ea1b58e24`.

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/capabilities/prepare-fixture.sh verify
```

The tool-specific discovery task may create a fresh copy if its assigned clone
has been changed by an incremental-update probe; it must not silently restore a
fixture and call the contaminated run clean.

## Agent-mediated probe

All three runs use a fresh ephemeral Codex CLI session with:

- model `gpt-5.6-terra`;
- reasoning effort `medium`;
- the same observable Codex runtime version;
- read-only agent sandbox except for evaluated public operations mediated by
  the lane adapter inside its disposable fixture and scratch lane;
- only the evaluated tool's normal public interface;
- the exact `probe-prompt.md`;
- `probe-output.schema.json`;
- one answer turn, no repair turn, and at most 24 evaluated-interface calls.

`probe-output.schema.json` remains canonical. The generated transport schema
removes provider-unsupported `allOf` and tuple-array constructs, adds required
types to constants, and preserves the required fields and all status, evidence,
operation, and Q01-Q11 values. The provider accepts a fixed-length homogeneous
answer array; the canonical schema and `validate-probe-output.py` remain the
second gate that enforces exact Q01-Q11 order and unique contiguous sequences.

The runner uses the isolated fixture as cwd with `--ephemeral`,
`--ignore-user-config`, `--ignore-rules`, read-only sandboxing, and unrelated
built-in tool features disabled. Its only configured MCP is the evaluated
interface. Native MCP servers pass through a stdio JSON-RPC counter; CLI-only
lanes expose explicitly configured public operations and argv templates
without a shell. Each materialized lane policy seals one executable
realpath/SHA-256, fixed argv templates, typed arguments, environment/path
roots, safe exposed tools, fixed MCP methods, and exact runtime surface.
Native startup is independently attested with initialize and
tool/resource/resource-template/prompt lists, including canonical digests of
the full returned objects; unexpected or changed tools, resources, resource
templates, prompts, capabilities, or instructions fail closed. The live proxy
filters that same attested server instance down to its safe exposed tools and
rejects arbitrary methods.
Both interfaces persist an
`ATTEMPTED` journal record before dispatch, append the terminal outcome, reject
and audit call 25 before dispatch, and invalidate any attempt that ends as
`FAILED_NO_RESPONSE`. CLI operations additionally have a fixed 120-second
response timeout. Provider MCP-call events must name server `evaluated` and
match the journal's operation names and order. Every real run must first emit
`interface_started`, which captures the policy, executable, roots, methods,
expected/observed/exposed surface, active MCP count, and contamination scan.
Zero calls are valid only when that startup record exists.

The adapter may translate a question to a public tool name but cannot provide
extra source, anchors, hints, questions, calls, turns, or another tool. Missing
capabilities use `NOT_APPLICABLE`, `UNAVAILABLE`, or abstention as defined in
the prompt and policy. This preserves tool differences rather than disguising
them behind private helper operations.

The planned one-off Terra-medium design review was attempted as
`DISCOVERY_SETUP`. The sandboxed Codex process exited before model completion
because its in-process app-server client could not initialize on the read-only
filesystem; the unsandboxed retry was rejected before execution by the approval
reviewer. The exact command, zero-byte JSONL, stderr, rejection, and
`UNKNOWN` usage fields are retained under
`scratchpad/code-intelligence/sessions/capability-fixture/`. That design-review
attempt remains incomplete and must not be represented as a completed model
review or a tool capability result.

The later synthetic no-tool setup smoke is retained separately under
`scratchpad/code-intelligence/sessions/capability-runner/` as
`SMOKE_EXCLUDED`. It reached one Terra-medium completion and passed the
provider schema, canonical schema, and sequence validator without repository
or tool content; its provider usage is recorded in the status artifact. A
smoke still declares one supported `tool_lane` and runs from that lane's frozen
fixture so its required manifest and commit metrics remain truthful, but it
does not configure or expose the evaluated interface.

## Measurement and contamination

The runner, not the agent, populates `metrics.schema.json`. Provider completion
events are authoritative for input, cached-input, output, and reasoning tokens;
an unexposed field is `UNKNOWN`. Local `gpt-tokenizer@3.4.0:o200k_base`
estimates serialized schema and raw-output tokens separately. These quantities
must never be added.

Each run records elapsed time, public operation count, file reads returned
through the tool, fallback searches, output bytes/tokens, fixture manifest,
fixture commit, runtime/model/effort, separate source/graph/status/documentation
evidence counts, and contamination booleans. Documentation-only evidence never
counts as returned source or a graph fact. The one-off Terra session used to
design/review this battery is `DISCOVERY_SETUP` and its provider usage is
retained separately; it is not a tool result.

Contamination is derived from the active command, recursive fixture/config
content and hashes, provider events, MCP identities, and attested runtime
surface. The scan detects anchor/reference content after renaming and rejects
cross-tool, subject-source, private-path, URL, credential, and live-submodule
inputs without loading curator-owned expected anchors.

`run-terra-probe.py` writes `metrics.json` and validates it against
`metrics.schema.json`. Provider usage comes only from completion events;
fixture identity comes from the frozen digest and Git commit; audited calls and
evidence counts are derived mechanically. Artifact-token fields remain
`UNKNOWN` when the pinned tokenizer is unavailable rather than being inferred.

After JSON Schema validation, every runner executes:

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/capabilities/validate-probe-output.py <probe-output.json>
```

This rejects missing, duplicated, or reordered Q01-Q11 answers; more than 24
operations; and operation sequences that are not unique, contiguous, ordered,
and starting at one.

See `operations-policy.md` for the full safe/restricted boundary and exclusion
rules. Any expected-anchor, cross-tool, Pi/Codex, source-only, generic source
access, hidden-surface, credential, network, or live-submodule leakage excludes
the run.
