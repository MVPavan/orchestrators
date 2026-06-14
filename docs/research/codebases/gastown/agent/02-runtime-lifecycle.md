# Runtime Lifecycle

## Main Entry Points

`cmd/gt/main.go` is a thin binary entry point that exits with the result of `cmd.Execute()`. The real command graph lives under `internal/cmd`. The root command is a Cobra command named `gt`; `GT_COMMAND` can change the displayed command name, and every non-exempt command runs `persistentPreRun` (`external/gastown/internal/cmd/root.go:25`, `external/gastown/internal/cmd/root.go:33`, `external/gastown/internal/cmd/root.go:98`).

The root pre-run is architecturally important because it sets up the town/session registry, does warning-only stale binary and branch checks, touches polecat heartbeats, and checks Beads version for non-exempt commands (`external/gastown/internal/cmd/root.go:120`, `external/gastown/internal/cmd/root.go:134`, `external/gastown/internal/cmd/root.go:139`, `external/gastown/internal/cmd/root.go:144`, `external/gastown/internal/cmd/root.go:150`). This means even small `gt` commands can update liveness state.

## Town Install Flow

Sequence for `gt install [path]`:

1. `runInstall` resolves target path, guards existing workspaces, checks dependencies such as Beads and Dolt, and checks port availability (`external/gastown/internal/cmd/install.go:50`, `external/gastown/internal/cmd/install.go:97`).
2. It creates the workspace and Mayor directory (`external/gastown/internal/cmd/install.go:202`).
3. It writes `mayor/town.json` and `mayor/rigs.json` (`external/gastown/internal/cmd/install.go:229`).
4. It creates town-root `CLAUDE.md` and `AGENTS.md` as identity anchors while relying on `gt prime` for full role context (`external/gastown/internal/cmd/install.go:272`).
5. It creates Mayor and Deacon runtime settings, Boot/plugin directories, and daemon patrol config (`external/gastown/internal/cmd/install.go:286`, `external/gastown/internal/cmd/install.go:315`, `external/gastown/internal/cmd/install.go:331`).
6. It initializes Git before Beads, initializes town-level Beads and Dolt server, provisions formulas, creates town-level agent beads, and sets routing mode (`external/gastown/internal/cmd/install.go:339`, `external/gastown/internal/cmd/install.go:348`, `external/gastown/internal/cmd/install.go:381`, `external/gastown/internal/cmd/install.go:390`).
7. It provisions escalation/overseer config, slash commands, hooks, optional shell/wrappers/supervisor integration, then prints next steps (`external/gastown/internal/cmd/install.go:405`, `external/gastown/internal/cmd/install.go:426`, `external/gastown/internal/cmd/install.go:447`).

Inference: install is both filesystem bootstrap and persistent identity bootstrap. It is not just a config generator.

## Rig Add Flow

`gt rig add` creates a project container around a source repository. The command docs describe the output layout: config, `.beads`, plugins, refinery/rig, mayor/rig, crew, witness, and polecats (`external/gastown/internal/cmd/rig.go:53`). The `runRigAdd` path validates options, locates the town root, loads `mayor/rigs.json`, creates a `rig.Manager`, calls `AddRig`, creates rig/agent beads, syncs hooks, commits town config changes, and refreshes tmux bindings (`external/gastown/internal/cmd/rig.go:485`).

`Manager.AddRig` performs the heavy lifting:

1. Validate the rig name and require a Dolt server path (`external/gastown/internal/rig/manager.go:318`).
2. Create the rig path and ownership stamp with rollback on failure (`external/gastown/internal/rig/manager.go:350`).
3. Save rig config with Beads prefix (`external/gastown/internal/rig/manager.go:402`).
4. Create the shared bare repo `.repo.git`, set push/upstream remotes, determine/save default branch, and create a canonical `mayor/rig` clone (`external/gastown/internal/rig/manager.go:420`, `external/gastown/internal/rig/manager.go:482`, `external/gastown/internal/rig/manager.go:499`, `external/gastown/internal/rig/manager.go:527`).
5. Initialize or adopt rig Beads, set custom types and prefix, and verify metadata (`external/gastown/internal/rig/manager.go:577`, `external/gastown/internal/rig/manager.go:674`, `external/gastown/internal/rig/manager.go:1001`).
6. Provision PRIME instructions, refinery worktree, crew/witness/polecat directories, runtime settings/commands, Beads routes, rig settings, agent beads, patrol molecules, plugin directories, and registry entries (`external/gastown/internal/rig/manager.go:748`, `external/gastown/internal/rig/manager.go:758`, `external/gastown/internal/rig/manager.go:789`, `external/gastown/internal/rig/manager.go:816`, `external/gastown/internal/rig/manager.go:824`, `external/gastown/internal/rig/manager.go:856`, `external/gastown/internal/rig/manager.go:886`, `external/gastown/internal/rig/manager.go:899`).

## Work Dispatch Flow

`gt sling` is the primary work dispatch command. Its docs describe it as unified dispatch for existing agents, auto-spawned polecats, dogs, formulas, auto-convoys, target resolution, merge strategy, and natural-language arguments (`external/gastown/internal/cmd/sling.go:25`). The implementation serializes dispatch through `SlingParams`, which acts as the queue dispatch boundary (`external/gastown/internal/cmd/sling_dispatch.go:15`).

`executeSling` follows this core sequence:

1. Acquire a per-bead file lock (`external/gastown/internal/cmd/sling_dispatch.go:97`).
2. Validate bead, target rig, rig operational state, parked/docked/deferred status, and existing ownership (`external/gastown/internal/cmd/sling_dispatch.go:116`).
3. Optionally force-steal by sending lifecycle shutdown to the old worker's witness (`external/gastown/internal/cmd/sling_dispatch.go:175`).
4. Burn stale molecules and allocate/spawn a polecat if needed (`external/gastown/internal/cmd/sling_dispatch.go:207`, `external/gastown/internal/cmd/sling_dispatch.go:231`).
5. Optionally create an auto-convoy (`external/gastown/internal/cmd/sling_dispatch.go:257`).
6. Cook formula work and instantiate formula/wisp state when a formula is involved (`external/gastown/internal/cmd/sling_dispatch.go:274`).
7. Hook the bead with an assignee lock and cleanup path on failure (`external/gastown/internal/cmd/sling_dispatch.go:331`).
8. Log the sling event, update the worker's agent bead, store fields such as branch/hook/source, and start the polecat session (`external/gastown/internal/cmd/sling_dispatch.go:350`, `external/gastown/internal/cmd/sling_dispatch.go:357`, `external/gastown/internal/cmd/sling_dispatch.go:379`).

## Polecat Startup Flow

Polecat creation is a worktree and identity operation:

1. The manager resolves rig path, Beads path, town root, and name pool (`external/gastown/internal/polecat/manager.go:150`).
2. It uses pool and per-polecat locks so concurrent dispatch does not allocate the same worker (`external/gastown/internal/polecat/manager.go:214`, `external/gastown/internal/polecat/manager.go:657`).
3. It derives a branch name from configured templates or defaults to `polecat/<name>/<issue>@<timestamp>` or `polecat/<name>-<timestamp>` (`external/gastown/internal/polecat/manager.go:544`).
4. It creates the worktree from the shared repo or mayor clone, provisions `CLAUDE.md`/PRIME, sets Beads redirects, copies overlays/excludes, installs runtime settings and setup hooks, then creates or reopens an agent bead (`external/gastown/internal/polecat/manager.go:725`).
5. It returns a working state with branch and clone path (`external/gastown/internal/polecat/manager.go:1099`).

The session startup layer uses a startup beacon that tells the agent how it was invoked and includes cold-start/attach/handoff guidance; assigned prompts tell agents to run `gt prime --hook` (`external/gastown/internal/session/startup.go:27`, `external/gastown/internal/session/startup.go:59`, `external/gastown/internal/session/startup.go:117`).

## Completion And MR Submission

`gt done` is the polecat completion path. It is intended for polecats, reconstructs worker identity from the environment/current directory, handles CWD drift, protects stashes, auto-commits uncommitted work when safe, parses branch/issue/sender/agent bead, and writes completion intent fields (`external/gastown/internal/cmd/done.go:30`, `external/gastown/internal/cmd/done.go:116`, `external/gastown/internal/cmd/done.go:137`, `external/gastown/internal/cmd/done.go:299`, `external/gastown/internal/cmd/done.go:419`).

For completed work, it blocks default-branch completion, verifies the workspace, requires commits ahead unless explicitly no-merge/review-only, checks contamination, fetches, rebases, then either closes directly or submits a merge request depending on mode (`external/gastown/internal/cmd/done.go:538`, `external/gastown/internal/cmd/done.go:697`).

`gt mq submit` creates the Beads-backed MR:

1. Find town/rig/CWD and reject default-branch submission (`external/gastown/internal/cmd/mq_submit.go:78`).
2. Parse source issue and worker from branch; determine target branch from explicit args, formula variables, integration branch detection, or default branch (`external/gastown/internal/cmd/mq_submit.go:147`, `external/gastown/internal/cmd/mq_submit.go:164`).
3. Enforce molecule step dependencies and verify pushed branch/commit SHA (`external/gastown/internal/cmd/mq_submit.go:207`, `external/gastown/internal/cmd/mq_submit.go:235`, `external/gastown/internal/cmd/mq_submit.go:367`).
4. Deduplicate existing MRs for the same branch/SHA and create an ephemeral Beads issue with label `gt:merge-request` (`external/gastown/internal/cmd/mq_submit.go:260`, `external/gastown/internal/beads/beads_mr.go:63`).
5. Nudge refinery, back-link source issue, supersede older open MRs for the source, and optionally ask witness to clean up polecat state (`external/gastown/internal/cmd/mq_submit.go:290`, `external/gastown/internal/cmd/mq_submit.go:306`, `external/gastown/internal/cmd/mq_submit.go:472`).

## Refinery Merge Flow

Refinery has two related layers:

- `Manager` handles refinery session lifecycle and queue listing from Beads MRs (`external/gastown/internal/refinery/manager.go:37`, `external/gastown/internal/refinery/manager.go:333`).
- `Engineer` performs the actual merge logic (`external/gastown/internal/refinery/engineer.go:255`).

Single MR path in `doMerge`:

1. Reject no-merge, verify local branch exists, checkout/pull target, and check conflicts (`external/gastown/internal/refinery/engineer.go:499`).
2. Push submodule commits and run configured gates/tests unless preverified skip applies (`external/gastown/internal/refinery/engineer.go:499`).
3. Use PR merge path when configured or squash merge locally (`external/gastown/internal/refinery/engineer.go:499`).
4. Run post-squash gates, get merge commit, acquire merge slot, push and verify, or stop before push when `auto_push` is false (`external/gastown/internal/refinery/engineer.go:499`).
5. On success, release slot, update/close MR, force-close source issue, close superseded conflicts, delete branches, run convoy checks, and nudge Mayor (`external/gastown/internal/refinery/engineer.go:1167`).
6. On failure, handle slot timeout, no-merge, approval wait, missing branches, conflict resolution tasks, worker/mayor nudges, and MR blocking (`external/gastown/internal/refinery/engineer.go:1294`).

Batch path:

- Batch config sets max size, wait time, and flaky retry behavior (`external/gastown/internal/refinery/batch.go:10`).
- `AssembleBatch` selects up to max size while respecting blockers (`external/gastown/internal/refinery/batch.go:55`).
- `ProcessBatch` stacks MRs on target, runs gates once on stack tip, fast-forwards on green, retries for flakiness, and bisects to isolate culprits if still red (`external/gastown/internal/refinery/batch.go:190`).
- Scoring combines base score, convoy age, priority, retry penalty, and MR age (`external/gastown/internal/refinery/score.go:11`, `external/gastown/internal/refinery/score.go:78`).

## Supervision And Recovery Flow

Daemon startup:

1. Acquire an exclusive daemon lock and write PID/state files (`external/gastown/internal/daemon/daemon.go:420`, `external/gastown/internal/daemon/daemon.go:435`, `external/gastown/internal/daemon/daemon.go:465`).
2. Block if town/rig Beads are not using Dolt backend (`external/gastown/internal/daemon/daemon.go:452`, `external/gastown/internal/daemon/daemon.go:1057`).
3. Start feed curator, convoy manager, KRC pruner, Dolt health ticker, Dolt remote/backup tickers, JSONL backup, wisp reaper, doctor dog, and other patrol tickers depending on config (`external/gastown/internal/daemon/daemon.go:492`, `external/gastown/internal/daemon/daemon.go:500`, `external/gastown/internal/daemon/daemon.go:545`, `external/gastown/internal/daemon/daemon.go:558`).
4. Run a fixed recovery heartbeat; normal wake is intended to come from feed subscription, while heartbeat catches dead or stuck sessions (`external/gastown/internal/daemon/daemon.go:485`).

Deacon:

- Daemon `ensureDeaconRunning` starts Deacon through `deacon.Manager` and uses a restart tracker/backoff to avoid crash loops (`external/gastown/internal/daemon/daemon.go:1437`).
- Deacon manager creates the deacon directory, runtime settings, startup prompt, agent env, tmux session, auto-respawn hook, and startup dialog acceptance (`external/gastown/internal/deacon/manager.go:97`, `external/gastown/internal/deacon/manager.go:109`, `external/gastown/internal/deacon/manager.go:128`, `external/gastown/internal/deacon/manager.go:139`, `external/gastown/internal/deacon/manager.go:169`).
- Daemon checks Deacon heartbeat and distinguishes grace period, stale, very stale, active-work gating, usage-limit pause, and crash-loop backoff (`external/gastown/internal/daemon/daemon.go:1490`, `external/gastown/internal/daemon/daemon.go:1580`, `external/gastown/internal/daemon/daemon.go:1632`).

Witness and Refinery:

- Daemon maintains witnesses and refineries per configured rig with bounded per-rig worker pool (`external/gastown/internal/daemon/daemon.go:120`, `external/gastown/internal/daemon/daemon.go:1697`, `external/gastown/internal/daemon/daemon.go:1774`).
- Witness startup is tmux-backed, rig-scoped, with Beads redirect, role config, runtime settings, startup command, nudge poller, startup fallback, and optional log streaming (`external/gastown/internal/witness/manager.go:104`, `external/gastown/internal/witness/manager.go:160`, `external/gastown/internal/witness/manager.go:172`, `external/gastown/internal/witness/manager.go:227`, `external/gastown/internal/witness/manager.go:264`).
- Refinery startup uses `refinery/rig` as the worktree when present, repairs from `.repo.git` if missing, ensures settings/gitignore, builds a `gt prime --hook` patrol startup prompt, and starts a tmux session with role env (`external/gastown/internal/refinery/manager.go:108`, `external/gastown/internal/refinery/manager.go:141`, `external/gastown/internal/refinery/manager.go:167`, `external/gastown/internal/refinery/manager.go:190`, `external/gastown/internal/refinery/manager.go:209`).

Lifecycle messages:

- The daemon reads Deacon mail for `LIFECYCLE:` subjects, deletes/claims messages before executing, then maps identity to tmux session and restarts/shuts down/cycles the session (`external/gastown/internal/daemon/lifecycle.go:41`, `external/gastown/internal/daemon/lifecycle.go:91`, `external/gastown/internal/daemon/lifecycle.go:161`).
- Identity parsing supports Mayor, Deacon, witness/refinery suffixes, crew/polecat hyphen formats, and polecat slash formats (`external/gastown/internal/daemon/lifecycle.go:221`).

