# Evaluated adapter policies

These are dry, lane-specific policy templates. They are not executable configs:
the placeholders must be resolved against one disposable fixture, one
tool-specific scratch lane, and one already-built executable.

Materialize and seal a template with:

```bash
capabilities/evaluated-interface.py \
  --materialize-template capabilities/adapter-policies/codegraph.template.json \
  --fixture-root scratchpad/code-intelligence/fixtures/codegraph \
  --scratch-root scratchpad/code-intelligence/runtime/lanes/codegraph-probe \
  --executable scratchpad/code-intelligence/runtime/lanes/codegraph-probe/bin/codegraph \
  --output-config scratchpad/code-intelligence/runtime/lanes/codegraph-probe/policy.json
```

Use absolute paths when invoking the command from outside the repository root.
The materializer resolves paths, hashes the executable, replaces every
placeholder, computes `policy_digest`, and runs the same fail-closed validation
used at runtime.

For a native MCP server whose initialize response contains instructions, also
pass `--instructions-sha256 HASH`. The native adapter starts a separate fresh
server, calls initialize plus `tools/list`, `resources/list`, and
`prompts/list`, and requires the discovered surface to equal the sealed
`expected_surface`. Only `allowed_tool_names` are then shown to the model.

All executable, cache, home, temp, graph, and index paths must remain inside
the assigned scratch lane. The only other permitted root is the assigned
disposable fixture. Live submodules, parent-repository paths outside
`scratchpad/code-intelligence`, private paths, URLs, credential environment
variables, and unresolved placeholders are rejected.
