import type { WorkResult } from "./contracts.js";

export class ResultStore {
  private readonly transitions = new Map<string, WorkResult[]>();

  save(result: WorkResult): void {
    const history = this.transitions.get(result.requestId) ?? [];
    history.push(result);
    this.transitions.set(result.requestId, history);
  }

  history(requestId: string): readonly WorkResult[] {
    return this.transitions.get(requestId) ?? [];
  }
}
