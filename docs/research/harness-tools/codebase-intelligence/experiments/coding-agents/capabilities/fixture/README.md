# Mixed-language fixture

This small workspace contains TypeScript packages and a dependency-free Rust
crate. It exists to exercise code-indexing and query behavior across multiple
files, package boundaries, languages, documentation, and an unknown file
extension.

The workspace builds TypeScript from the root configuration. The gateway
process expects a policy command through `FIXTURE_POLICY_COMMAND`, falling back
to a command discoverable as `fixture-policy`. The two processes exchange one
line per request and response.

These notes are intentionally incomplete. They do not specify authoritative
dependency directions, lifecycle order, trust boundaries, failure behavior,
symbol bindings, or change impact. Those claims must come from source or graph
evidence, not from this document.
