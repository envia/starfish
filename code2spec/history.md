# Code2Spec History

> **Relevant source files**
>
> - [README.md](src:README.md)

## 2026-08-27 — W1 code2spec-discovery (full run)

- **Tool**: code2spec v0.5.2 (release build, commit `2c251e6`), coding agent: claude-code
- **Target**: repository root (`/home/hwang/work/D/starfish_`), branch `master`
- **Document language**: English
- **Analysis scope**: 3 (Detail) — all modules Core
- **AST export**: 1,815 files, 28,929 nodes, 152,362 edges (`.analysis/cache/code-to-ast/`)
  - Note: `.code2specignore` was added at the repo root with `!core` because the exporter's
    directory-name matching of `.gitignore`'s `core` (core-dump) pattern wrongly excluded
    `src/core` (1,485 files) and the `!src/core` negation is not supported by the exporter.
- **IPC pattern discovery**: 8 custom patterns applied (`nanomsg`, `subprocess`, `websocket`)
  → `.analysis/ipc-discovery/discovered-ipc-patterns.json`
- **LLM extraction**: 169 enums / 480 constants / 34 verified IPC records; merged set 2,021 items;
  validation gate passed (ENUM 429 ≥ 5, CONSTANT 1412 ≥ 20, IPC 180 ≥ 10)
- **Interface scan**: 34 message-contract candidates (`.analysis/interface-candidates.json`, W2 input)
- **Module discovery**: 32 logical modules proposed and approved via human review
  (coverage: 1,815/1,815 files assigned exactly once; 0 missing / 0 duplicates)
- **Deliverables**: SDD chapters `01`–`09`, `diagrams/architecture.mmd` (32 nodes / 46 AST-backed edges),
  `diagrams/dependency-heatmap.mmd`, `functional-requirements/index.md` (32 modules, pending W2),
  `.ast/{api,deps}.json`, `repo.json`
- **Next**: run W2 (`code2spec-modules`) for Module Design Cards and per-module FR documents,
  then W3 (`code2spec-finalize`) for interlinking, quick reference, and validation.

## 2026-09-10 — W1 completion after interruption

- The 2026-08-27 run was interrupted during chapter generation by an API spend-limit error
  (chapters 01, 02, 04, 06, 07 had been written but their final self-verification passes did not finish).
- Resumed and completed: format validation of all chapters (H1 + Relevant-source-files block,
  `src:` deep links, no absolute URLs), grounding recheck of 1,641 symbol deep links with
  16 label/line corrections applied, `README.md` index written.
- W1 status: **complete**. Next step: W2 (`code2spec-modules`).
