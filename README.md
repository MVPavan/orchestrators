# Agent Orchestrators

Workspace for agent orchestration experiments. The default direction is subscription-first CLI integrations where possible, with API-based providers available when a workflow needs them.

## Upstream Projects

This repository keeps the upstream projects as Git submodules:

- `gascity`: `https://github.com/gastownhall/gascity.git`
- `gastown`: `https://github.com/gastownhall/gastown.git`

Only the submodule commit pointers are tracked in this parent repository. The internal files and history of `gascity` and `gastown` stay in their own repositories.

## Clone

```bash
git clone --recurse-submodules <this-repo-url>
```

For an existing clone:

```bash
git submodule update --init --recursive
```

## Sync Upstreams

Update one upstream project:

```bash
git submodule update --remote --merge gascity
git add gascity
git commit -m "Update gascity submodule"
```

Update both upstream projects:

```bash
git submodule update --remote --merge gascity gastown
git add gascity gastown
git commit -m "Update upstream submodules"
```
