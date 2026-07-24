import type { Handler, RequestKind, WorkRequest, WorkResult } from "./contracts.js";
import { normalize } from "./normalize.js";

export abstract class BaseHandler implements Handler {
  abstract readonly kind: RequestKind;

  async execute(request: WorkRequest): Promise<WorkResult> {
    return {
      requestId: request.id,
      state: "COMPLETED",
      output: this.transform(normalize(request.payload))
    };
  }

  protected abstract transform(payload: string): string;
}

export class PaymentHandler extends BaseHandler {
  readonly kind = "payment" as const;

  protected transform(payload: string): string {
    return `charged:${payload}`;
  }
}

export class ReportHandler extends BaseHandler {
  readonly kind = "report" as const;

  protected transform(payload: string): string {
    return `reported:${payload}`;
  }
}

export class HandlerRegistry {
  constructor(private readonly handlers: ReadonlyMap<RequestKind, Handler>) {}

  resolve(kind: RequestKind): Handler {
    const handler = this.handlers.get(kind);
    if (!handler) {
      throw new Error(`unresolved handler:${kind}`);
    }
    return handler;
  }
}
