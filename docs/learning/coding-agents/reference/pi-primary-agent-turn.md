# Pi primary agent turn: compact reference

Status: source-grounded

Subject: Pi commit `24bace27cf308c89707cf8005b4795d873e23f17`

Primary authority:
[frozen reference ledger](../../../research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/reference-ledger.md)

## Systems thesis

Pi's ordinary interactive path is a layered in-process event pipeline:

- `InteractiveMode` owns terminal interaction.
- `AgentSession` owns coding-agent policy, extensions, persistence, retry, and
  compaction.
- `Agent` owns one active abort-controlled in-memory run.
- The agent loop owns provider/tool iteration.
- `ModelRuntime` resolves the selected provider and normalized stream.
- `SessionManager` owns parent-linked durable JSONL entries.
- Pi TUI turns session events into coalesced differential terminal output.

These are contract boundaries, not separate services.

## Causal trace

```mermaid
sequenceDiagram
    actor User
    participant UI as InteractiveMode
    participant Session as AgentSession
    participant Agent
    participant Loop as Agent loop
    participant Provider as ModelRuntime/provider
    participant Tool
    participant Store as SessionManager
    participant TUI

    User->>UI: submit text
    UI->>Session: prompt
    Session->>Session: extensions, templates, auth, compaction check
    Session->>Agent: prompt AgentMessage[]
    Agent->>Loop: snapshot context and run with AbortSignal
    Loop->>Provider: system prompt + converted messages + tools
    Provider-->>Loop: start/delta/done or error
    Loop-->>Agent: message lifecycle events
    Agent-->>Session: state-reduced events
    Session->>Store: append finalized message on message_end
    Session-->>TUI: message/tool events
    alt assistant requests tools
        Loop->>Tool: validated call with AbortSignal
        Tool-->>Loop: updates and final result
        Loop->>Loop: append ToolResultMessage in assistant call order
        Loop->>Provider: next model turn
    end
    Loop-->>Session: agent_end
    Session->>Session: retry, compaction, or queued continuation
    Session-->>UI: agent_settled
    TUI-->>User: coalesced full/differential terminal write
```

## Four state and identity distinctions

| Identity/state | Role |
| --- | --- |
| Active run + `AbortSignal` | One Agent execution and its cancellation path |
| Tool-call ID | Joins tool intent, execution, result, and UI component |
| Session entry ID + `parentId` | Durable branch and transcript ordering |
| Session ID | Identifies the session and may support provider cache identity |

Do not collapse partial assistant state into durable history.
`streamingMessage` is transient; finalized messages enter Agent state and
session JSONL at `message_end`.

## Three completion boundaries

1. `turn_end`: one model/tool turn ended.
2. `agent_end`: the reusable Agent loop has no immediate work.
3. `agent_settled`: session-level retry, compaction, and extension-queued work
   also finished.

For operating Pi, `agent_settled` is the strongest idle boundary.

## Trust and failure

- Project trust gates project-local resources; it does not sandbox tools.
- Tools and extensions run with the launching process's OS authority unless an
  external sandbox provides isolation.
- A shared abort signal reaches provider streaming, hooks, and tools, but
  timely cancellation depends on each implementation honoring it.
- Invalid, missing, blocked, aborted, or throwing tool calls become error tool
  results when possible.
- Provider failure can end the Agent loop; `AgentSession` may still retry or
  compact before settlement.

## Evidence classes

**Verified:** the event ordering, state ownership, persistence point, identity
fields, trust scope, and render-coalescing mechanism are established in the
frozen source reference.

**Inference:** Pi is best understood as an event pipeline with policy and
runtime layers, rather than as independent agent services.

**Open:** provider-specific cancellation guarantees, concrete loaded
extensions and permissions, and crash consistency under partial JSONL writes.
