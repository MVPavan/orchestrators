# Anchors — paperclip (repo-SPECIFIC) — Codex-designed

**These 20 anchors are specific to paperclip and do NOT transfer to other repos.** OpenHands and
deer-flow each get their own freshly-chosen anchor set (same scenario template, different real symbols).
**Ground truth per anchor is computed independently next** (orchestrator via ripgrep + classification,
Codex cross-checks) before any tool is run.

Root: `scratchpad/harness/_paperclip_src`. Status of gold sets: **TBD — computing next.**

| ID | Anchor (symbol @ file:line) | Type | Diversity / weakness it stresses |
| --- | --- | --- | --- |
| A1 | `startServer` @ server/src/index.ts:103 | entrypoint fn | runtime trace; tests also call it |
| A2 | `createApp` @ server/src/app.ts:129 | app factory | heavy name collision w/ many test-helper `createApp`s |
| A3 | `issueRoutes` @ server/src/routes/issues.ts:1052 | route registrar | barrel-exported via routes/index.ts; many callbacks |
| A4 | `issueService` @ server/src/services/issues.ts:3164 | service factory | `issueService(db).create` object-method calls — hard for call graphs |
| A5 | `heartbeatService` @ server/src/services/heartbeat.ts:3370 | service factory | huge file; adapter dispatch; many tests |
| A6 | `createStorageServiceFromConfig` @ server/src/storage/index.ts:21 | factory | re-exported from services index; self/cache edge |
| A7 | `issues` @ packages/db/src/schema/issues.ts:22 | Drizzle table const | heavily used; common local-var name; DB barrel exports |
| A8 | `issueReferenceMentions` @ packages/db/src/schema/issue_reference_mentions.ts:6 | Drizzle table const | rarer DB symbol; cross-package via @paperclipai/db |
| A9 | `extractIssueReferenceMatches` @ packages/shared/src/issue-references.ts:176 | shared util | barrel-exported from @paperclipai/shared; calls internal helper |
| A10 | `buildIssueReferenceHref` @ packages/shared/src/issue-references.ts:97 | shared util | UI usage through package barrel; tests + runtime |
| A11 | `PaperclipPluginManifestV1` @ packages/shared/src/types/plugin.ts:509 | interface | type-only impact; validator docs; plugin boundary |
| A12 | `CatalogTeam` @ packages/shared/src/types/teams-catalog.ts:76 | interface | **same name as A13**; used by UI/server shared API |
| A13 | `CatalogTeam` @ packages/teams-catalog/src/types.ts:67 | interface | **same name as A12, different package** — name-trace trap |
| A14 | `ServerAdapterModule` @ packages/adapter-utils/src/types.ts:349 | interface | type-only contract; re-exported; implemented by object literals |
| A15 | `prepareCommandManagedRuntime` @ packages/adapter-utils/src/command-managed-runtime.ts:230 | async fn | cross-module util; nested `runner.execute` calls |
| A16 | `execute` @ packages/adapters/codex-local/src/server/execute.ts:323 | adapter fn | **many sibling `execute` defs** — collision/name-trace stress |
| A17 | `MarkdownBody` @ ui/src/components/MarkdownBody.tsx:566 | React component | JSX uses; createElement; test mocks |
| A18 | `ChatComposer` @ ui/src/components/ChatComposer.tsx:111 | forwardRef component | inner fn same name; JSX + test-mock usage |
| A19 | `usePaperclipIssueRuntime` @ ui/src/hooks/usePaperclipIssueRuntime.ts:40 | React hook | called inside component bodies — often missed by graph tools |
| A20 | `registerRunCommands` @ cli/src/commands/client/run.ts:46 | CLI registrar | CLI registration + test registration |

**Coverage by bucket:** entrypoint/lifecycle (A1, A20) · service/app factory (A2, A4, A5, A6) ·
barrel-exported (A3, A6, A9, A10) · cross-package (A8, A9, A10, A12/A13) · name-collision/shadow
(A2, A12+A13, A16) · DB schema (A7, A8) · type-only interface (A11, A12, A13, A14) · React/JSX
(A17, A18, A19) · adapter `execute` (A16) · structural-sweep targets (A3 routes, A7 tables, A18 forwardRef).
