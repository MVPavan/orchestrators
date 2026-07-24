import type { Policy, WorkRequest } from "../../core/src/contracts.js";

export interface ProcessLauncher {
  request(command: string, line: string): Promise<string>;
}

export class ProcessPolicy implements Policy {
  constructor(
    private readonly launcher: ProcessLauncher,
    private readonly command: string
  ) {}

  async authorize(request: WorkRequest): Promise<boolean> {
    if (request.actor.includes("|")) {
      throw new Error("actor contains protocol delimiter");
    }

    const response = await this.launcher.request(
      this.command,
      `fixture-policy-v1|${request.actor}`
    );
    if (!response.startsWith("fixture-policy-v1|")) {
      throw new Error("invalid policy response");
    }
    return response === "fixture-policy-v1|allow";
  }
}
