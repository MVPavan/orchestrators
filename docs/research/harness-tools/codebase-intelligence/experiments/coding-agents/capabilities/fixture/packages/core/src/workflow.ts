import type { Policy, WorkRequest, WorkResult } from "./contracts.js";
import { EventBus } from "./events.js";
import { HandlerRegistry } from "./handlers.js";
import { ResultStore } from "./store.js";

export class WorkflowEngine {
  constructor(
    private readonly policy: Policy,
    private readonly handlers: HandlerRegistry,
    private readonly store: ResultStore,
    private readonly events: EventBus
  ) {}

  async run(request: WorkRequest): Promise<WorkResult> {
    try {
      if (!(await this.policy.authorize(request))) {
        throw new Error(`denied actor:${request.actor}`);
      }

      const authorized: WorkResult = {
        requestId: request.id,
        state: "AUTHORIZED",
        output: ""
      };
      this.store.save(authorized);

      const handler = this.handlers.resolve(request.kind);
      const completed = await handler.execute(request);
      this.store.save(completed);
      this.events.publish({ name: "workflow.completed", requestId: request.id });
      return completed;
    } catch (error) {
      const reason = error instanceof Error ? error.message : "unknown";
      const failed: WorkResult = {
        requestId: request.id,
        state: "FAILED",
        output: reason
      };
      this.store.save(failed);
      this.events.publish({ name: "workflow.failed", requestId: request.id, reason });
      throw error;
    }
  }
}
