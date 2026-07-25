# Coding-agent systems resources

## Knowledge

- [Pi primary-turn reference](../../research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/reference-ledger.md)
  Frozen source-first trace for Pi commit `24bace27cf30`. Use for primary-turn
  control, state, persistence, trust, failure, and rendering claims.
- [Pi tracer synthesis](../../research/harness-tools/codebase-intelligence/experiments/coding-agents/pi/synthesis.md)
  Reconciles the four experimental answers with the frozen reference. Use for
  understanding what each graph tool helped or missed.
- [Learning and experiment plan](../../plans/2026-07-24-pi-codex-learning-experiment.md)
  Defines the systems scope, cost controls, quality rubric, teaching protocol,
  and Pi-before-Codex gates.
- [Pi security documentation](../../../external/coding-agents/pi/packages/coding-agent/docs/security.md)
  Primary source for project trust, host authority, and the fact that project
  trust is not a tool sandbox.
- [Pi agent loop](../../../external/coding-agents/pi/packages/agent/src/agent-loop.ts)
  Primary source for provider streaming, tool execution, tool-result ordering,
  steering/follow-up handling, and lifecycle events.
- [Pi session orchestration](../../../external/coding-agents/pi/packages/coding-agent/src/core/agent-session.ts)
  Primary source for prompt preflight, extension policy, persistence bridging,
  retries, compaction, and `agent_settled`.

## Wisdom (Communities)

External community review is deferred. The current phase prioritizes frozen
source evidence and the learner's own teach-back before seeking practitioner
opinions.

## Gaps

- Provider-specific transport and cancellation behavior remains outside the
  provider-neutral first lesson.
- Crash consistency of session JSONL under partial writes has not been tested.
- Runtime-specific extension and tool permission policies require a concrete
  configured Pi installation.
