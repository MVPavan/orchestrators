export type RequestKind = "payment" | "report";

export interface WorkRequest {
  id: string;
  kind: RequestKind;
  payload: string;
  actor: string;
}

export interface WorkResult {
  requestId: string;
  state: "AUTHORIZED" | "COMPLETED" | "FAILED";
  output: string;
}

export interface Handler {
  readonly kind: RequestKind;
  execute(request: WorkRequest): Promise<WorkResult>;
}

export interface Policy {
  authorize(request: WorkRequest): Promise<boolean>;
}
