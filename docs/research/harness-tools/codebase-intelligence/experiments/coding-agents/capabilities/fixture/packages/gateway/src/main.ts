import { EventBus } from "../../core/src/events.js";
import type { Handler, RequestKind } from "../../core/src/contracts.js";
import {
  HandlerRegistry,
  PaymentHandler,
  ReportHandler
} from "../../core/src/handlers.js";
import { ResultStore } from "../../core/src/store.js";
import { WorkflowEngine } from "../../core/src/workflow.js";
import process from "node:process";
import { ProcessPolicy } from "./policy.js";
import { NodeProcessLauncher } from "./process-launcher.js";
import { handleRequest } from "./router.js";

const handlers = new HandlerRegistry(
  new Map<RequestKind, Handler>([
    ["payment", new PaymentHandler()],
    ["report", new ReportHandler()]
  ])
);
const events = new EventBus();
events.subscribe((event) => console.log(event.name, event.requestId));

const engine = new WorkflowEngine(
  new ProcessPolicy(
    new NodeProcessLauncher(),
    process.env.FIXTURE_POLICY_COMMAND ?? "fixture-policy"
  ),
  handlers,
  new ResultStore(),
  events
);

await handleRequest(engine, {
  id: "req-1",
  kind: "payment",
  payload: "  invoice-42  ",
  actor: " external-user "
});
