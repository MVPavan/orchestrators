export type WorkflowEvent =
  | { name: "workflow.completed"; requestId: string }
  | { name: "workflow.failed"; requestId: string; reason: string };

export type EventListener = (event: WorkflowEvent) => void;

export class EventBus {
  private readonly listeners: EventListener[] = [];

  subscribe(listener: EventListener): void {
    this.listeners.push(listener);
  }

  publish(event: WorkflowEvent): void {
    for (const listener of this.listeners) {
      listener(event);
    }
  }
}
