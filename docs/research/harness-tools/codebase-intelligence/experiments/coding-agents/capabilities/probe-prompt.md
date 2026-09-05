# Fixed tool-neutral capability probe

You are evaluating one code-intelligence tool against the disposable repository
already indexed for this session. Use only the normal public capability
interface exposed to you. Do not use shell commands, generic file-search/file-
read tools, Git history, the internet, another graph tool, or prior experiment
outputs. Source text is admissible only when the evaluated tool itself returns
it. Documentation returned by the tool is admissible only as
`DOCUMENTATION_RETURNED_BY_TOOL`; it cannot by itself prove a source binding,
call edge, lifecycle, trust boundary, failure path, or change impact.

The repository is the fixture `mixed-ts-rust-capability-v1`. Do not inspect any
Pi, Codex, tool implementation, reference answer, expected-anchor file, or
scoring key. Do not identify the evaluated tool by name in your answer.

Follow the questions in order. You may make at most 24 calls to the evaluated
public interface. This is one answer turn with no repair turn. A capability
that the public interface does not expose is `NOT_APPLICABLE`; one that is
exposed but unavailable in this environment is `UNAVAILABLE`. Do not simulate
missing capabilities. When evidence is ambiguous, abstain instead of guessing.

1. **Q01 inventory/schema:** Report indexed languages, files, packages/crates,
   entry points, symbol/entity kinds, edge/relation kinds, and any skipped
   inputs that the public interface can establish.
2. **Q02 architecture:** Identify the central components and dependency
   directions. Keep graph/source relationships, documentation-only statements,
   and inference explicitly separate.
3. **Q03 lifecycle/path:** Trace the primary successful request from entry point
   through authorization, dispatch, execution, state transition, and event
   delivery. Also summarize the converging failure path.
4. **Q04 collision:** Find the distinct bindings named `normalize`, identify
   their callers and purposes, and state whether the tool keeps them separate.
5. **Q05 impact/change:** Determine the impact of adding required field
   `attempts` to `WorkResult`, using `synthetic-change.patch` and a public
   change/impact operation when available. Name constructors and consumers that
   are and are not directly affected.
6. **Q06 stale-index/update:** If a safe public incremental-update capability is
   exposed, report the pre-change result, apply or register only the supplied
   synthetic patch in this disposable clone, update the index, and report the
   post-change result. Otherwise return the appropriate capability-specific
   status without changing files.
7. **Q07 unsupported-input:** Establish whether
   `unsupported/legacy.capfixture` was indexed, skipped, or unsupported. Do not
   infer absence from a single empty search.
8. **Q08 ambiguity/abstention:** Evaluate the TypeScript-to-Rust policy
   relationship. State what is source-resolved, what is documentation-only, and
   where the tool cannot prove a concrete cross-language symbol call edge.
9. **Q09 source-evidence:** Return the strongest tool-provided source evidence
   for the lifecycle, collision, state, trust, and failure claims. Cite
   repo-relative paths and symbols; do not invent line numbers or substitute
   documentation-only evidence for source evidence.
10. **Q10 failure/status/debug:** Use public status/health/debug surfaces when
    exposed, then make one deliberately missing-symbol or impossible-path query.
    Report diagnostics, failure shape, and recovery guidance without repairing
    global state.
11. **Q11 resource/token outputs:** Report only resource, timing, output-size,
    index, or token counters actually exposed by the tool. Use `UNKNOWN` for
    unavailable values; zero is valid only when explicitly measured or
    reported.

Return one JSON object matching `probe-output.schema.json`. Include every Q01
through Q11 exactly once, in order. List each public operation in execution
order, and set `public_operation` to the exact exposed operation name that you
invoked (for example, `status`, not `index status`). `output_bytes` is `null`
when the runner did not expose it. Do not estimate provider token usage; the
runner records provider completion events outside your answer.
