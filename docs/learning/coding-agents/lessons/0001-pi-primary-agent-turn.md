# Lesson 1: Trace one Pi agent turn

Mission link: understand an unfamiliar coding agent as a system, not as a pile
of TypeScript files.

Reference:
[Pi primary-agent-turn compact reference](../reference/pi-primary-agent-turn.md)

## Tangible win

After this lesson, you should be able to explain why a Pi "turn" is not one
function call or one model response.

## The smallest useful model

Think of Pi as a policy shell around a reusable event engine:

```text
terminal
  -> InteractiveMode
  -> AgentSession
  -> Agent + agent loop
  -> ModelRuntime/provider
  -> tools
  -> AgentSession persistence
  -> InteractiveMode + Pi TUI
  -> terminal
```

`AgentSession` is the systems hinge. On the way in, it applies extension,
template, model/auth, and compaction policy. During the run, it bridges Agent
events to persistence and the UI. On the way out, it decides whether retry,
compaction, or queued work means the session is not really finished.

## Walk the mechanism

1. `InteractiveMode` hands ordinary input to `AgentSession.prompt()`. Input
   arriving during a run becomes steering or follow-up work instead of a
   second direct Agent run.
2. `AgentSession` performs prompt preflight and creates `AgentMessage` values.
3. `Agent` snapshots system prompt, transcript, and tools, creates one active
   `AbortSignal`, and enters the agent loop.
4. The loop converts internal messages to provider messages and streams through
   `ModelRuntime`.
5. Stream events build a partial assistant message and then finalize it.
6. Tool calls are validated and intercepted, run sequentially or in parallel,
   and become ordered `ToolResultMessage` values for another model turn.
7. At `message_end`, finalized messages enter parent-linked session JSONL.
8. UI events update components; Pi TUI coalesces render requests and writes
   only the necessary terminal changes.
9. `agent_end` may still be followed by retry, compaction, or extension work.
   `agent_settled` is the stronger idle boundary.

## The two traps

**Trap 1: "The model response is the final answer."**

Extensions can replace finalized messages, tools can trigger more model turns,
and session-level recovery can continue after the Agent loop ends.

**Trap 2: "Project trust protects tool execution."**

Project trust controls loading project resources. It is not a tool sandbox.
Tool isolation comes from the host OS, container, VM, or a separately loaded
policy extension.

## Primary source to revisit

Read the verified lifecycle in the
[frozen reference ledger](../../../research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/reference-ledger.md),
especially steps 2 through 12. Ask your teaching agent about any transition
that feels like a jump rather than a cause.

## Feynman teach-back

Without using package jargon as a substitute for explanation, teach a capable
newcomer how one submitted prompt can cause multiple model calls, tool work,
durable state changes, and terminal updates—and explain why `agent_end` is not
always the same as "Pi is idle."
