import type { WorkRequest, WorkResult } from "../../core/src/contracts.js";
import { WorkflowEngine } from "../../core/src/workflow.js";
import { normalize } from "./normalize.js";

export async function handleRequest(
  engine: WorkflowEngine,
  request: WorkRequest
): Promise<WorkResult> {
  if (!request.id || !request.actor || !request.payload) {
    throw new Error("invalid external request");
  }

  const trustedRequest = { ...request, actor: normalize(request.actor) };
  return engine.run(trustedRequest);
}
