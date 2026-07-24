# Partial design note

The fixture has a gateway package, a core package, and a Rust policy crate.
Some interactions use ordinary TypeScript imports; one interaction crosses a
process boundary. The repository also contains handler, state, and event
concepts.

This note deliberately omits the exact call sequence, implementation bindings,
state transitions, error convergence, and protocol grammar. It is included to
test whether a tool labels documentation separately from resolved source or
graph relationships.
