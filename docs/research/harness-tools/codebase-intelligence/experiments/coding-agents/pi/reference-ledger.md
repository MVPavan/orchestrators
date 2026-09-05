# Pi primary agent-turn reference ledger

Status: `FROZEN`

Recorded: 2026-07-24

Tracking: `orch-8sk.3`

Subject: `external/coding-agents/pi`

Revision: `24bace27cf308c89707cf8005b4795d873e23f17`

Question: `PI-T01` in `tracer-prompt.md`

## Scope

This is the source-first reference for one ordinary interactive Pi prompt that
may cause one or more model/tool turns and finishes in the terminal UI. It is
not the complete Pi architecture report. Print, JSON, RPC, server, compaction,
resume, extension authoring, and provider-specific wire protocols are included
only where they change this lifecycle.

The reference was built directly from the frozen source checkout. No graph
tool, model session, network request, or runtime execution was used.

## Systems thesis

**INFERENCE:** Pi is a layered, in-process event pipeline rather than a set of
independent agent services. The coding-agent package owns orchestration policy,
resource loading, persistence, retries, and user interaction. Agent core owns
the provider/tool loop and its event protocol. Pi AI owns provider resolution
and normalizes provider-specific streams. Pi TUI turns session events into
coalesced differential terminal writes.

The important boundary is therefore not a process boundary between these
packages. It is the contract boundary between:

- terminal input and `InteractiveMode`;
- coding-agent policy and the reusable `Agent`;
- normalized `Context`/`AssistantMessageEvent` and a selected provider;
- validated tool calls and ordinary host-process execution;
- in-memory agent state and append-only session JSONL;
- session events and terminal rendering.

## System boundary

| Element | Role in this trace | Evidence |
| --- | --- | --- |
| Human and terminal | Submit text, see streamed/final output, request cancellation | `packages/coding-agent/src/modes/interactive/interactive-mode.ts:2639-2642`, `:2815-2824`, `:3967-3984` |
| `InteractiveMode` | UI control loop and event-to-component adapter | `packages/coding-agent/src/modes/interactive/interactive-mode.ts:905-914`, `:2828-2834` |
| `AgentSession` | Prompt preflight, extension policy, persistence, retry/compaction coordination | `packages/coding-agent/src/core/agent-session.ts:1114-1265`, `:595-665` |
| `Agent` and agent loop | In-memory run state, normalized lifecycle events, provider/tool iteration | `packages/agent/src/agent.ts:337-410`, `packages/agent/src/agent-loop.ts:95-275` |
| `ModelRuntime` and provider | Auth/config resolution and provider-specific normalized streaming | `packages/coding-agent/src/core/sdk.ts:294-329`, `packages/coding-agent/src/core/model-runtime.ts:492-496` |
| Tool registry and host OS | Validate, optionally intercept, then execute tool code with process authority | `packages/agent/src/agent-loop.ts:600-703`, `packages/coding-agent/docs/security.md:31-37` |
| `SessionManager` | Durable session identity and parent-linked JSONL entries | `packages/coding-agent/src/core/session-manager.ts:930-955`, `:1015-1066` |
| Pi TUI | Coalesce render requests and write only changed terminal regions when possible | `packages/tui/src/tui.ts:716-763`, `:1258-1285`, `:1372-1406` |

External actors are the model provider, the terminal, the filesystem and
subprocess/network environment used by tools, and extension code. The selected
provider is outside Pi's trust boundary. Tool and extension execution remains
inside the launching user's OS authority; Pi does not create a lower-privilege
execution boundary.

## Verified lifecycle

### 1. Accept the interactive submission

`InteractiveMode.setupEditorSubmitHandler()` trims the input, handles Pi
commands and direct shell escapes, and places an ordinary prompt into the
pending-input handoff. The main interactive loop awaits that handoff and calls
`AgentSession.prompt()`.

Evidence:

- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:2639-2644`
- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:2774-2825`
- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:3490-3501`
- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:905-914`

### 2. Apply coding-agent preflight and extension policy

`AgentSession.prompt()` can execute an extension command instead of starting an
agent run. Otherwise it lets extensions handle or transform input, expands
skill and prompt-template syntax, queues the input if a run is already active,
validates model/auth state, checks whether prior context needs compaction, and
creates the user `AgentMessage`. A `before_agent_start` extension may add custom
messages or replace the system prompt before `_runAgentPrompt()` begins.

Evidence:

- `packages/coding-agent/src/core/agent-session.ts:1114-1172`
- `packages/coding-agent/src/core/agent-session.ts:1174-1216`
- `packages/coding-agent/src/core/agent-session.ts:1218-1265`

### 3. Establish one active agent run

`Agent.prompt()` rejects a second direct prompt while another run is active,
normalizes input, snapshots the current system prompt, messages, and tools, and
invokes `runAgentLoop()`. `runWithLifecycle()` owns an `AbortController`, marks
the agent streaming, and clears runtime-only state after the loop and awaited
listeners settle.

Evidence:

- `packages/agent/src/agent.ts:337-410`
- `packages/agent/src/agent.ts:426-469`
- `packages/agent/src/agent.ts:471-519`

### 4. Emit the user-side lifecycle and build provider context

The loop appends the prompt to its current context and emits `agent_start`,
`turn_start`, then user `message_start`/`message_end`. Before each provider
call, it optionally transforms `AgentMessage[]`, converts it to provider-safe
`Message[]`, and builds a `Context` from the system prompt, messages, and
currently exposed tools.

Evidence:

- `packages/agent/src/agent-loop.ts:95-117`
- `packages/agent/src/agent-loop.ts:281-312`
- `packages/ai/src/types.ts:477-503`

### 5. Resolve and stream through the selected provider

The coding-agent-created `Agent` delegates to `ModelRuntime.streamSimple()`
with configured timeout/retry/header behavior. `ModelRuntime` prepares auth and
provider configuration, then calls the selected provider's normalized
`streamSimple()` implementation. Agent core consumes normalized start, text,
thinking, tool-call, done, and error events.

Evidence:

- `packages/coding-agent/src/core/sdk.ts:294-329`
- `packages/coding-agent/src/core/model-runtime.ts:450-496`
- `packages/ai/src/types.ts:484-503`
- `packages/agent/src/agent-loop.ts:308-371`

### 6. Reduce stream events into message state and UI events

On provider `start`, the loop inserts a partial assistant message and emits
`message_start`. Each delta replaces that partial message and emits
`message_update`. `done` or `error` replaces it with the final assistant
message and emits `message_end`. `Agent.processEvents()` mirrors those events
into public agent state before awaiting subscribers.

Evidence:

- `packages/agent/src/agent-loop.ts:314-371`
- `packages/agent/src/agent.ts:529-575`

### 7. Execute requested tools and create tool-result messages

If the assistant message contains tool calls, the loop selects sequential
execution when globally configured or when any requested tool requires it;
otherwise it uses parallel execution. Each call is resolved by name,
arguments are validated, and the optional `beforeToolCall` hook can block it.
The tool receives the shared abort signal and may stream updates. The optional
`afterToolCall` hook can replace result fields. A finalized
`ToolResultMessage`, keyed by the provider tool-call ID, is emitted and added
to the current context.

Evidence:

- `packages/agent/src/agent-loop.ts:202-224`
- `packages/agent/src/agent-loop.ts:411-425`
- `packages/agent/src/agent-loop.ts:433-553`
- `packages/agent/src/agent-loop.ts:600-703`
- `packages/agent/src/agent-loop.ts:709-792`

`AgentSession` installs extension-backed `tool_call` and `tool_result` hooks,
but those are extension points, not a universal permission system.

Evidence:

- `packages/coding-agent/src/core/agent-session.ts:460-518`

### 8. Continue or terminate the agent loop

After tool results, the loop emits `turn_end`, refreshes next-turn
context/model/tool state, and normally starts another provider turn so the
model can consume the tool results. It can instead stop after the turn, accept
queued steering messages, accept follow-up messages after the agent would
otherwise stop, terminate early when every tool in the batch requests
termination, or finish with `agent_end`.

Evidence:

- `packages/agent/src/agent-loop.ts:218-275`
- `packages/agent/src/agent-loop.ts:582-584`
- `packages/coding-agent/src/core/agent-session.ts:520-540`

### 9. Persist finalized messages

`AgentSession` forwards events to extensions and UI listeners, then persists
each finalized user, assistant, and tool-result message on `message_end`.
`SessionManager` assigns an entry ID, links it to the current leaf with
`parentId`, advances the leaf, and writes JSONL when persistence is enabled.
The session ID is also passed into the `Agent` for provider cache-aware
backends.

Evidence:

- `packages/coding-agent/src/core/agent-session.ts:618-665`
- `packages/coding-agent/src/core/session-manager.ts:930-955`
- `packages/coding-agent/src/core/session-manager.ts:1015-1066`
- `packages/coding-agent/src/core/sdk.ts:349-374`

### 10. Render streaming and final state

`InteractiveMode` maps session events to assistant and tool components:
`message_start` creates the streaming component, deltas update it, tool events
update tool components, and `agent_end` clears working state. Each path requests
a render. Pi TUI coalesces render requests to a minimum interval, renders the
component tree, compares it with previous terminal lines, and emits a full or
differential terminal update.

Evidence:

- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:2828-2865`
- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:2890-3031`
- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:3035-3052`
- `packages/tui/src/tui.ts:716-763`
- `packages/tui/src/tui.ts:1258-1285`
- `packages/tui/src/tui.ts:1372-1406`

### 11. Settle, retry, or recover

After the core loop ends, `AgentSession._runAgentPrompt()` may continue after a
retryable error, compaction, or messages queued by an `agent_end` extension.
Only after this post-run handling stops does it emit `agent_settled` and resolve
its idle wait. Retry uses configurable exponential backoff and can be aborted.

Evidence:

- `packages/coding-agent/src/core/agent-session.ts:1061-1103`
- `packages/coding-agent/src/core/agent-session.ts:581-588`
- `packages/coding-agent/src/core/agent-session.ts:2634-2735`

### 12. Propagate cancellation without creating a sandbox

The `Agent` owns an abort controller and passes its signal to provider streaming,
tool hooks, and tool execution. Aborted provider/error paths finalize an
assistant message with `stopReason: "aborted"` or `"error"` and terminate the
loop. The interactive layer can call `agent.abort()`. A tool must honor its
received signal for cancellation to be timely.

Evidence:

- `packages/agent/src/agent.ts:306-323`
- `packages/agent/src/agent.ts:471-511`
- `packages/agent/src/agent-loop.ts:196-200`
- `packages/agent/src/agent-loop.ts:304-312`
- `packages/agent/src/agent-loop.ts:666-706`
- `packages/coding-agent/src/modes/interactive/interactive-mode.ts:3967-3984`

## State and identity invariants

| Invariant | Status | Evidence |
| --- | --- | --- |
| One `Agent` has at most one direct active run; concurrent user input becomes steering/follow-up at the session layer | VERIFIED | `packages/agent/src/agent.ts:337-376`, `packages/coding-agent/src/core/agent-session.ts:1158-1172` |
| `Agent.state.messages` contains finalized in-memory messages; `streamingMessage` is runtime-only partial state | VERIFIED | `packages/agent/src/agent.ts:529-566` |
| Tool-call ID joins assistant tool intent, execution events, result message, and UI component | VERIFIED | `packages/agent/src/agent-loop.ts:763-791`, `packages/coding-agent/src/modes/interactive/interactive-mode.ts:2918-2941`, `:2992-3031` |
| Session entry ID and `parentId` form the durable branch; `leafId` advances on append | VERIFIED | `packages/coding-agent/src/core/session-manager.ts:958-977`, `:1044-1066` |
| Session ID identifies the JSONL session and is forwarded to providers that use cache-aware session identity | VERIFIED | `packages/coding-agent/src/core/session-manager.ts:930-955`, `packages/coding-agent/src/core/sdk.ts:349-350` |
| Final messages persist at `message_end`, before later `turn_end`/`agent_end` policy completes | VERIFIED | `packages/coding-agent/src/core/agent-session.ts:624-665` |

## Trust and permission boundary

**VERIFIED:** Pi project trust decides whether project-local settings,
resources, packages, and extensions load. It is explicitly not a sandbox and
does not restrict tool behavior after startup. Built-in tools and extensions
run with the launching process's permissions. Strong isolation must come from
the OS, a container, or a VM.

Evidence:

- `packages/coding-agent/docs/security.md:3-37`
- `README.md:37-45`

**INFERENCE:** An extension can implement a policy by blocking `tool_call`
events, but the security of that policy depends on which extensions were
loaded and on the host boundary. The core loop provides an interception seam;
it does not make that seam a mandatory authorization service.

## Failure domains

- Provider preparation or streaming can end in a normalized error/aborted
  assistant message; `AgentSession` may retry selected transient errors.
- A missing tool or invalid arguments becomes an error tool result rather than
  a process crash.
- A tool exception becomes an error tool result. Cancellation depends on the
  provider, hook, and tool honoring the shared signal.
- Extension input/context/provider/tool hooks can transform or block the path;
  extension behavior is runtime-dependent.
- Session persistence is synchronous file I/O in the event path. This makes
  finalized-message durability straightforward, but persistence failure can
  interrupt event settlement.
- TUI writes are throttled and differential; an event requests rendering but
  does not necessarily cause an immediate distinct terminal write.

## Open questions

1. The tracer should remain provider-neutral. Provider-specific event mapping,
   request payloads, retries, and cancellation behavior require selecting one
   concrete provider implementation.
2. Exact loaded extensions, tools, skills, prompt templates, and trust decisions
   are configuration-dependent. The reference describes the default coding
   agent and its extension seams, not one user's runtime inventory.
3. The source establishes cancellation propagation, not a universal upper
   bound on cancellation latency for arbitrary tool or provider implementations.
4. The source shows synchronous JSONL append/rewrite paths; crash consistency
   under partial writes is outside this tracer.
5. `agent_end` is not the final coding-agent settlement boundary when retry,
   compaction, or extension-queued work continues. Controlled answers must
   distinguish core-loop completion from `agent_settled`.

## Do not over-index on

- Package directory counts: the lifecycle is defined by contracts and events,
  not the monorepo tree.
- Provider-specific adapters: they implement the normalized stream boundary but
  do not own the agent loop.
- TUI component details: the architectural point is event-driven state plus
  throttled differential rendering.
- Project trust: it protects startup resource loading, not tool execution.
