declare module "node:child_process" {
  interface WritablePipe {
    end(data: string): void;
  }

  interface ReadablePipe {
    setEncoding(encoding: "utf8"): void;
    on(event: "data", listener: (chunk: string) => void): void;
  }

  interface ChildProcess {
    stdin: WritablePipe;
    stdout: ReadablePipe;
    stderr: ReadablePipe;
    once(event: "error", listener: (error: Error) => void): void;
    once(event: "close", listener: (code: number | null) => void): void;
  }

  export function spawn(
    command: string,
    args: readonly string[],
    options: { stdio: ["pipe", "pipe", "pipe"] }
  ): ChildProcess;
}

declare module "node:process" {
  const process: {
    env: Record<string, string | undefined>;
  };
  export default process;
}
