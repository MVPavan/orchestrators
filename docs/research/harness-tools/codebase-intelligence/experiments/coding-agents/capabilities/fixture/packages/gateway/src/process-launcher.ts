import { spawn } from "node:child_process";
import type { ProcessLauncher } from "./policy.js";

export class NodeProcessLauncher implements ProcessLauncher {
  request(command: string, line: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const child = spawn(command, [], { stdio: ["pipe", "pipe", "pipe"] });
      let stdout = "";
      let stderr = "";

      child.stdout.setEncoding("utf8");
      child.stderr.setEncoding("utf8");
      child.stdout.on("data", (chunk) => {
        stdout += chunk;
      });
      child.stderr.on("data", (chunk) => {
        stderr += chunk;
      });
      child.once("error", reject);
      child.once("close", (code) => {
        if (code !== 0) {
          reject(new Error(`policy process exited ${String(code)}:${stderr.trim()}`));
          return;
        }
        resolve(stdout.trim());
      });
      child.stdin.end(`${line}\n`);
    });
  }
}
