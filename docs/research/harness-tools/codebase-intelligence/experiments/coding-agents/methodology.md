# Coding-agent graph-tool experiment methodology

Status: Phase 0A runtime and isolation readiness
Recorded: 2026-07-24
Tracking: `orch-8sk.2`

This document freezes the local inputs and runtime contract for the Pi-first
study. It is setup evidence, not a capability result or a claim that any tool
has indexed Pi. Capability enumeration and measured study runs begin only in
later phases.

## Frozen inputs

No fetch or submodule update was run. Full revisions and worktree state were
checked before and after the bounded smokes.

| Input | Live submodule revision | Disposable clone(s) | Branch | State |
| --- | --- | --- | --- | --- |
| Pi | `24bace27cf308c89707cf8005b4795d873e23f17` | `reference`, `source-only`, `codegraph`, `cbm`, `graphify` | `main` | live and all five clones clean |
| Codex | `f61b51ddd924643514b33234816a8a2772b1aec7` | deliberately absent in Phase 0A | `main` | live clean |
| CodeGraph | `03666584ed9836d7954cbb19e2252081b96fcad9` | `scratchpad/code-intelligence/tools/codegraph` | `main` | live and clone clean |
| CBM | `53ebeb4cf1fca0f4b2384e7ab085e529a2d2750b` | `scratchpad/code-intelligence/tools/cbm`, fresh detached rebuild clone under `runtime/rebuild-cbm/source` | `main`; rebuild detached | live and both clones clean outside declared ignored build output |
| Graphify | `2fa6cd3d5548577f8c5f591b713f0bf80c1af183` | `scratchpad/code-intelligence/tools/graphify` | `v8` | live and clone clean |

Each disposable repository has its own `.git`. The eight pre-run source-tree
snapshots under `scratchpad/code-intelligence/runtime/manifests/` were compared
with a fresh `git ls-files -s`; all eight matched after the smokes. Ignored build
and lane artifacts are not part of those manifests.

The live-submodule proof used:

```bash
git submodule status --recursive
for path in \
  external/coding-agents/pi \
  external/coding-agents/codex \
  external/harness-tools/codebase-intelligence/codegraph \
  external/harness-tools/codebase-intelligence/codebase-memory-mcp \
  external/harness-tools/codebase-intelligence/graphify
do
  git -C "$path" rev-parse HEAD
  git -C "$path" status --porcelain=v1 --untracked-files=all
done
git diff --submodule=log -- \
  external/coding-agents/pi \
  external/coding-agents/codex \
  external/harness-tools/codebase-intelligence/codegraph \
  external/harness-tools/codebase-intelligence/codebase-memory-mcp \
  external/harness-tools/codebase-intelligence/graphify
```

Before and after results were the five SHAs above, empty porcelain output, and
an empty parent-repository submodule diff. Therefore the bounded checks did not
change a live checkout or pointer.

## Runtime and toolchain

| Component | Verified local value |
| --- | --- |
| Codex CLI | `0.144.4` |
| Git | `2.43.0` |
| Node.js / npm | `22.22.0` / `11.9.0` |
| Python | `3.12.3` |
| uv | `0.9.8` |
| C compiler | GCC `13.3.0` |
| GNU Make | `4.3` |
| jq | `1.7` |
| CodeGraph runtime | `tools/codegraph/dist/bin/codegraph.js`, `1.0.1` |
| CBM runtime | `build/c/codebase-memory-mcp`, `0.9.0+53ebeb4cf1fc` |
| Graphify runtime | isolated editable virtual environment, distribution `graphifyy 0.9.25` |

The CBM executable is an x86-64 dynamically linked ELF; `ldd` resolved its
`libm`, `libstdc++`, `libz`, `libgcc_s`, and `libc` dependencies. The original
`cbm-build.log` records an initial failed link caused by incorrectly quoted
`CBM_VERSION`. That provenance gap was closed with a fresh local clone from the
frozen revision and this successful isolated command:

```bash
set -euo pipefail

frozen_cbm=53ebeb4cf1fca0f4b2384e7ab085e529a2d2750b
rebuild_root=scratchpad/code-intelligence/runtime/rebuild-cbm/source
evidence=scratchpad/code-intelligence/runtime/rebuild-cbm/evidence
wrapper=docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh
binary="$rebuild_root/build/c/codebase-memory-mcp"

test ! -e "$rebuild_root"
git clone --no-hardlinks --no-checkout \
  scratchpad/code-intelligence/tools/cbm \
  "$rebuild_root"
git -C "$rebuild_root" checkout --detach "$frozen_cbm"
test "$(git -C "$rebuild_root" rev-parse HEAD)" = "$frozen_cbm"

mkdir -p "$evidence"
{
  printf 'HEAD='
  git -C "$rebuild_root" rev-parse HEAD
  printf 'branch='
  git -C "$rebuild_root" symbolic-ref -q --short HEAD ||
    printf 'DETACHED\n'
} | tee "$evidence/clone-head.txt"

git -C "$rebuild_root" status --porcelain=v1 --untracked-files=all |
  tee "$evidence/clone-status-before.txt"

"$wrapper" cbm-rebuild env |
  LC_ALL=C sort |
  tee "$evidence/environment.txt"

"$wrapper" cbm-rebuild \
  bash "$rebuild_root/scripts/build.sh" \
  --version 0.9.0+53ebeb4cf1fc 2>&1 |
  tee "$evidence/build.log"

"$wrapper" cbm-rebuild "$binary" --version 2>&1 |
  tee "$evidence/version.txt"

"$wrapper" cbm-rebuild "$binary" cli list_projects '{}' 2>&1 |
  tee "$evidence/list-projects.txt"

git -C "$rebuild_root" status --porcelain=v1 --untracked-files=all |
  tee "$evidence/clone-status-after.txt"

file "$binary" |
  tee "$evidence/binary-file.txt"

ldd "$binary" |
  tee "$evidence/binary-ldd.txt"
```

The clone resolved to `53ebeb4cf1fca0f4b2384e7ab085e529a2d2750b`
before the build and had empty tracked/untracked porcelain before and after
because `build/` is declared ignored by the upstream repository. The command
used only the frozen clone's vendored sources plus system GCC/Make; it invoked
no package manager, downloader, global installer, or live submodule. The
retained environment is the exact `env -i` output produced by the intended
parent-repo wrapper artifact. The 266,071,720-byte result has SHA-256
`905c5860211b26969e77c0c866c953d41952a6bb8530c4115bbae50d3406e58c`
and reports `codebase-memory-mcp 0.9.0+53ebeb4cf1fc`. The linker emitted one
warning about the vendored `unixcoder_blob.o` lacking a GNU-stack note; the
build nevertheless exited `0`.

The earlier `graphify-version.log` says `0.8.44`; it is stale. Fresh
`importlib.metadata.version("graphifyy")`, the checked-out `pyproject.toml`, and
the editable environment all report `0.9.25`, so `0.9.25` is the frozen runtime
value.

The proposed `tools/codegraph/dist/cli/index.js` path does not exist in the
frozen CodeGraph clone. Its `package.json` bin entry, build script, CLI script,
and CLI tests all identify `dist/bin/codegraph.js`; that existing built entry
point produced the retained `1.0.1` smoke result.

## Model catalog, routing, and pricing

The setup retained these redacted/local artifacts:

- `runtime/model-catalog/live.json`: eight models, SHA-256
  `91ca405dfbed34e2d45c116a45b2b9eb1ff054096e2499c337597556d84174ab`
- `runtime/model-catalog/bundled.json`: eight models, SHA-256
  `1119d9d8c006a83294109acadc5517bf205a5aa0a33262dd93f921c6c9fb7509`
- `runtime/model-catalog/doctor-redacted.json`: Codex `0.144.4` diagnostic
  snapshot

| Model | Live default | Live efforts | Live context | Bundled context |
| --- | --- | --- | ---: | ---: |
| `gpt-5.6-sol` | low | low, medium, high, xhigh, max, ultra | 272,000 | 372,000 |
| `gpt-5.6-terra` | medium | low, medium, high, xhigh, max, ultra | 272,000 | 372,000 |
| `gpt-5.6-luna` | medium | low, medium, high, xhigh, max | 272,000 | 372,000 |

The catalogs agree on model availability and effort levels but disagree on the
advertised context window. Experimental runs will use the live catalog value
and record the observable model/runtime again per run; the bundled value is
provenance only. `none` is not advertised. `ultra` remains excluded because it
changes the delegation structure.

The approved routing remains:

- no model for enumeration, indexing, manifests, token counting, and mechanical
  transforms;
- Luna low only for bounded, mechanically checked normalization;
- Terra low for scan-only orientation;
- Terra medium for capability probes, every controlled source-only and
  graph-assisted arm, routine investigation, lesson drafting, and first-pass
  scoring;
- Sol medium for reference architecture and final systems synthesis;
- Sol low/medium for disputed evidence, escalating to high or xhigh only after a
  recorded failed gate.

The following pricing inputs and source links were revalidated against the
approved plan on 2026-07-24. The plan records these Codex credit rates per one
million tokens:

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| Sol | 125 | 12.5 | 750 |
| Terra | 62.5 | 6.25 | 375 |
| Luna | 25 | 2.5 | 150 |

Pricing evidence is the same-day accepted
[plan](../../../../../plans/2026-07-24-pi-codex-learning-experiment.md) and live
official verification on 2026-07-24. The
[OpenAI Codex pricing](https://learn.chatgpt.com/docs/pricing#what-are-tokens-and-credits)
page confirmed that the table is credits per one million input, cached-input,
and output tokens and confirmed all nine rates above. The
[recommended models](https://learn.chatgpt.com/docs/models#recommended-models)
page confirmed the Sol, Terra, and Luna positioning and the guidance to use the
lowest reasoning effort that works.
The plan also cites
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6)
and [subagent model choice](https://learn.chatgpt.com/docs/agent-configuration/subagents#model-choice).
No raw webpage snapshot was retained. Before reporting monetary totals after
this date, refresh the official pricing page or record the rates as `UNKNOWN`
if that cannot be done.

## Artifact tokenizer

Local estimates use `gpt-tokenizer 3.4.0` with explicit `o200k_base` encoding
(package metadata SHA-256
`f5a6ca8e43a4e5092098b88f913ee0844b9b4a0230e2f496e88b461daa2f4760`).
The package documentation identifies `o200k_base` as the default encoding for
modern GPT models. The isolated smoke encoded
`Phase 0A schema token smoke` as seven tokens and decoded it byte-for-byte.
The exact retained metadata and roundtrip smoke can be regenerated with:

```bash
set -o pipefail
wrapper=docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh
tokenizer=scratchpad/code-intelligence/runtime/tokenizer/node_modules/gpt-tokenizer
evidence=scratchpad/code-intelligence/runtime/evidence/phase0a
node_dir="$(dirname -- "$(command -v node)")"

test "$(sha256sum "$tokenizer/package.json" | cut -d ' ' -f 1)" = \
  f5a6ca8e43a4e5092098b88f913ee0844b9b4a0230e2f496e88b461daa2f4760

mkdir -p "$evidence"
CODE_INTEL_EXTRA_PATH="$node_dir" "$wrapper" tokenizer-smoke node -e \
  "const pkg=require('./$tokenizer/package.json'); const tok=require('./$tokenizer/cjs/encoding/o200k_base.js'); const input='Phase 0A schema token smoke'; const tokens=tok.encode(input); const decoded=tok.decode(tokens); const result={package:pkg.name,version:pkg.version,encoding:'o200k_base',input,tokens,token_count:tokens.length,decoded,roundtrip:decoded===input}; console.log(JSON.stringify(result)); if(pkg.version!=='3.4.0'||tokens.length!==7||decoded!==input) process.exit(1);" |
  tee "$evidence/tokenizer-roundtrip.json"
```

Provider-reported usage remains authoritative for billed/context usage. Local
token counts are reproducible estimates for serialized schemas and raw outputs;
they must remain in separate columns and must never be added to provider usage.
An unexposed provider field is `UNKNOWN`, not zero. The tokenizer directory has
no experiment-local lockfile, so version, encoding, and package-metadata hash
must all be preserved with results.

## Isolation contract

The disposable path map is:

| Role | Path |
| --- | --- |
| Pi reference | `scratchpad/code-intelligence/subjects/pi/reference` |
| Pi source-only baseline | `scratchpad/code-intelligence/subjects/pi/source-only` |
| Pi + CodeGraph | `scratchpad/code-intelligence/subjects/pi/codegraph` |
| Pi + CBM | `scratchpad/code-intelligence/subjects/pi/cbm` |
| Pi + Graphify | `scratchpad/code-intelligence/subjects/pi/graphify` |
| CodeGraph tool clone | `scratchpad/code-intelligence/tools/codegraph` |
| CBM tool clone | `scratchpad/code-intelligence/tools/cbm` |
| Graphify tool clone | `scratchpad/code-intelligence/tools/graphify` |
| Lane-local homes, caches, state, temp, and output | `scratchpad/code-intelligence/runtime/lanes/<lane>/` |

No disposable Codex subject path exists in Phase 0A; the Pi learning gate must
pass before any Codex subject clone is created.

All tool commands run through:

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  <lane> <command> [args...]
```

The intended parent-repo wrapper artifact resolves the repository root from its
own location, changes to that root, starts with `env -i`, and supplies only the
portable system executable path and lane-local values under
`scratchpad/code-intelligence/runtime/lanes/<lane>/`:

- `HOME`
- `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`
- `TMPDIR`
- `CBM_CACHE_DIR`
- `GRAPHIFY_OUT`
- `UV_CACHE_DIR`

It also redirects `CODEX_HOME` and `CLAUDE_CONFIG_DIR`, sets offline flags for
uv, pip, npm, Hugging Face, and Transformers, disables telemetry, replaces
global/system Git configuration, clears Git credential helpers, disables
interactive credentials, and provides no provider API-key variables. A fresh
`env` audit exposed no credential variable. The lane home/config directories
contained no MCP configuration. A runtime not present on the portable system
path may be supplied explicitly for one invocation with
`CODE_INTEL_EXTRA_PATH`; only that directory is added, not the caller's full
`PATH`.

These controls prevent accidental inheritance and tell supported clients to
stay offline. They do **not** enforce network denial against an arbitrary child
process. Both available namespace candidates were tested:

```text
unshare -n true
# unshare failed: Operation not permitted

bwrap --unshare-net --ro-bind / / --dev /dev --proc /proc true
# Failed to create NETLINK_ROUTE socket: Operation not permitted
```

Because neither mechanism works on this host, the wrapper does not expose or
claim a network-sandbox option. The safe-offline gate therefore additionally
requires auditing the invoked command and its retained log; a capability that
needs network access remains restricted.

CodeGraph indexes may exist only as `.codegraph/` inside its disposable Pi
clone. CBM state may exist only under its lane `CBM_CACHE_DIR`. Graphify output
and any graph passed to a mutating query must live under its lane output. A
Graphify query writes `cache/last_query_stamp` beside the graph even when the
query is otherwise read-only; therefore querying a graph stored in a tool clone
is forbidden. The smoke copied the fixture to lane output first.

No global install, network install, provider credential, paid service, live
submodule, or Codex subject clone is part of this setup.

## Evidence preservation and regeneration

Large or raw evidence remains ignored under
`scratchpad/code-intelligence/runtime/`, as required by the approved plan. The
intended parent-repo compact manifest artifact
[`phase0a-evidence.sha256`](phase0a-evidence.sha256) records SHA-256, byte size,
and repo-relative path for the Phase 0A logs, source-tree snapshots, model
catalogs, tokenizer metadata/roundtrip, tool smokes and fixtures,
clean-rebuild evidence, and rebuilt CBM binary.

From the repository root, the following deterministically regenerates the
manifest candidate and verifies that the retained raw evidence still matches:

```bash
manifest=docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/phase0a-evidence.sha256
candidate="$(mktemp)"
trap 'rm -f "$candidate"' EXIT

{
  find \
    scratchpad/code-intelligence/runtime/evidence/phase0a \
    scratchpad/code-intelligence/runtime/lanes/graphify-smoke/output/fixture \
    scratchpad/code-intelligence/runtime/logs \
    scratchpad/code-intelligence/runtime/manifests \
    scratchpad/code-intelligence/runtime/model-catalog \
    scratchpad/code-intelligence/runtime/rebuild-cbm/evidence \
    -type f -print0
  printf '%s\0' \
    scratchpad/code-intelligence/runtime/rebuild-cbm/source/build/c/codebase-memory-mcp \
    scratchpad/code-intelligence/runtime/tokenizer/node_modules/gpt-tokenizer/package.json
} |
  LC_ALL=C sort -z |
  while IFS= read -r -d '' file; do
    hash="$(sha256sum "$file" | cut -d ' ' -f 1)"
    size="$(wc -c < "$file" | tr -d ' ')"
    printf '%s\t%s\t%s\n' "$hash" "$size" "$file"
  done > "$candidate"

diff -u "$manifest" "$candidate"
```

After intentionally regenerating the raw evidence, replace the intended
parent-repo manifest artifact with the verified candidate before the shell
exits:

```bash
install -m 0644 "$candidate" "$manifest"
```

The clean CBM rebuild evidence itself is regenerated from an absent
`runtime/rebuild-cbm/source` path by running the clone and wrapper commands in
the Runtime and toolchain section, then the two CBM smoke commands below.

## Bounded smoke results

### CodeGraph

```bash
CODE_INTEL_EXTRA_PATH="$(dirname -- "$(command -v node)")" \
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  codegraph-smoke \
  node scratchpad/code-intelligence/tools/codegraph/dist/bin/codegraph.js \
  --version
```

Result: `1.0.1`, exit `0`.

```bash
set -o pipefail
evidence=scratchpad/code-intelligence/runtime/evidence/phase0a
mkdir -p "$evidence"
CODE_INTEL_EXTRA_PATH="$(dirname -- "$(command -v node)")" \
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  codegraph-smoke \
  node scratchpad/code-intelligence/tools/codegraph/dist/bin/codegraph.js \
  status scratchpad/code-intelligence/subjects/pi/codegraph 2>&1 |
  tee "$evidence/codegraph-status.txt"
```

Result: exit `0`; the CLI resolved the disposable Pi path and reported `Not
initialized` with the instruction to run `codegraph init`. Initialization was
intentionally deferred to capability discovery; this smoke proves executable
startup and subject isolation, not indexing correctness.

### CBM

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  cbm-rebuild \
  scratchpad/code-intelligence/runtime/rebuild-cbm/source/build/c/codebase-memory-mcp \
  --version
```

Result: `codebase-memory-mcp 0.9.0+53ebeb4cf1fc`, exit `0`.

```bash
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  cbm-rebuild \
  scratchpad/code-intelligence/runtime/rebuild-cbm/source/build/c/codebase-memory-mcp \
  cli list_projects '{}'
```

Result: exit `0` and
`{"projects":[],"hint":"No projects indexed. Call index_repository(repo_path=...) first."}`.
This proves binary/CLI/cache startup without beginning a Pi index.

### Graphify

```bash
set -o pipefail
evidence=scratchpad/code-intelligence/runtime/evidence/phase0a
mkdir -p "$evidence"
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  graphify-smoke \
  scratchpad/code-intelligence/tools/graphify/.venv-harness/bin/python -c \
  "import importlib.metadata as m, graphify, sys; print('python='+sys.version.split()[0]); print('distribution='+m.version('graphifyy')); print('module='+graphify.__file__)" |
  tee "$evidence/graphify-import.txt"
```

Result: Python `3.12.3`, distribution `0.9.25`, module loaded from the
disposable Graphify clone, exit `0`.

The retained 17,813-byte mixed-corpus graph and query evidence are regenerated
with:

```bash
set -o pipefail
evidence=scratchpad/code-intelligence/runtime/evidence/phase0a
fixture=scratchpad/code-intelligence/runtime/lanes/graphify-smoke/output/fixture/graph.json
mkdir -p "$evidence"

install -D -m 0600 \
  scratchpad/code-intelligence/tools/graphify/worked/mixed-corpus/graph.json \
  "$fixture"
docs/research/harness-tools/codebase-intelligence/experiments/coding-agents/run-isolated.sh \
  graphify-smoke \
  scratchpad/code-intelligence/tools/graphify/.venv-harness/bin/graphify \
  query analyze \
  --graph "$fixture" \
  --budget 80 2>&1 |
  tee "$evidence/graphify-query.txt"
```

Result: exit `0`; BFS depth 2 found 13 nodes and returned two nodes within the
80-token cap. The fixture emitted a warning that it uses the pre-`#1504`
node-ID scheme; this affects that old fixture, not runtime startup. The only
new query stamp was under the lane output, and the tool clone remained clean.

## Readiness conclusion and limits

**VERIFIED:** frozen revisions, disposable repository boundaries, source-tree
snapshots, a clean reproducible CBM build, the three local runtimes, the
live/bundled model and effort catalogs, the tokenizer, credential-stripped
environment, retained evidence hashes, and live-submodule cleanliness.

**VERIFIED WITH LIMITS:** Phase 0A is ready for offline capability discovery.
The host cannot enforce a network namespace, and no raw pricing webpage
snapshot was retained. The live/bundled context-window mismatch must remain
explicit.

**NOT YET TESTED:** Pi indexing, MCP initialization/schema discovery, complete
public capability enumeration, resource accounting, controlled agent sessions,
and answer-quality evaluation. These belong to Phase 0B/0C and later beads and
must not be inferred from these startup smokes.
