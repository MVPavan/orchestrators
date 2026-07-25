# Coding-agent systems glossary

- **AgentSession:** Pi coding-agent's orchestration layer. It owns prompt
  preflight, extension policy, persistence bridging, retries, compaction, and
  settled/idle notification.
- **Agent:** Reusable in-memory runtime that owns one active abort-controlled
  run and reduces loop events into public state.
- **Agent loop:** Provider/tool iteration that streams an assistant message,
  executes tool calls, appends tool results, and continues until no work
  remains.
- **AgentMessage:** Pi's internal transcript message. It is converted to a
  provider-safe message only at the model boundary.
- **Context:** Effective system prompt, converted messages, and exposed tools
  sent to the selected provider stream.
- **`message_end`:** Finalization boundary for one user, assistant, or
  tool-result message. `AgentSession` persists finalized messages here.
- **`turn_end`:** End of one provider/tool turn. It does not imply that the
  full user-visible run is settled.
- **`agent_end`:** End of the reusable Agent's current loop. Session-level
  retry, compaction, or extension-queued continuation may still follow.
- **`agent_settled`:** Coding-agent boundary after post-run handling finishes.
  This is the stronger session-idle signal.
- **Tool-call ID:** Joins model tool intent, execution events, tool result, and
  UI component.
- **Session entry ID / `parentId`:** Defines durable transcript-tree identity
  and branch order in session JSONL.
- **Project trust:** Startup resource-loading decision for project settings,
  packages, and extensions. It is not a tool sandbox or general permission
  system.
