# W2 Module Document Contract (Starfish / code2spec)

Repo root: /home/hwang/work/D/starfish_ — every `src:` path is relative to it. Output dir: /home/hwang/work/D/starfish_/code2spec. Document language: English. Starfish is "a lightweight Web browser engine for TV, mobile, headless and wearable devices" (README.md line 3), C++.

## Inputs (all under the repo root)
- Module file list: code2spec/.analysis/state/delta/module-groups.yaml → `modules[]` with `name`, `files` (full relative paths — use them VERBATIM), `rationale`, `confidence`.
- Symbol definition lines: code2spec/.ast/api.json (LARGE — grep by symbol or file path; never read whole). Reading the source file and citing the line you see is equally valid.
- Dependencies: code2spec/.ast/deps.json (LARGE — grep), or the `#include` lines of the module files.
- IPC candidate context: code2spec/.analysis/interface-candidates/by-module/<module>.json — evidence-backed leads only; verify each in source before citing; may contain zero candidates.
- Extraction results: code2spec/.analysis/llm-extraction/llm-enum-results.json, llm-constant-results.json, llm-ipc-results.json — grep for your module's file paths; entries carry `"source": "[Source: path:line]"`.
- System chapters for context (read-only): code2spec/02-architecture.md, 05-external-interfaces.md, 09-ipc-enum-catalog.md.

## Analysis depth
Grep `^class |^struct |^enum ` across all module files to inventory types; read fully the ~10 most central files (largest / most included headers and their .cpp); grep the rest. For modules over 100 files, skimming is acceptable but the Source Files list and the Relevant-source-files block must still contain ALL files.

## Rules (machine-validated in W3; violations fail the build)
1. Zero-inference: only facts from files you read. Missing → "Not specified in code". Never expand acronyms unless the repo defines them. Never describe library behavior from outside knowledge.
2. Every .md: line 1 is `# <Title>`; the very next block is
   > **Relevant source files**
   >
   > - [path/to/file.h](src:path/to/file.h)
   file-level links, no line numbers, nothing between H1 and this block.
   - Design Card RSF: ALL module files (full relative paths verbatim from module-groups.yaml) plus any other file you cite.
   - FR document RSF: 3-12 most relevant module files.
3. Symbol citations are backticked deep links [`Symbol`](src:path#L<n>) where n is the REAL definition/declaration line of that identifier in that file (verify by reading). Label = bare identifier or `Class::method` — no signatures, parentheses, or extra words. To cite a file location rather than a symbol, use a backticked file-name label: [`Foo.cpp`](src:src/x/Foo.cpp#L12). Never https:// source links, never a bare `[출처]`/`[Source]` label, never #L1 as a default, never mention an identifier as evidence without a link.
4. Wiki-internal links are plain markdown without backticks: [System Architecture](../02-architecture.md), [core-dom-fr.md](../functional-requirements/core-dom-fr.md).
5. Mermaid: quote every label containing spaces or @ / \ . : ( ) { } % # & ; participant/node IDs are real class or file names (underscore instead of special chars); one edge per line (no `A-->B-->C`); only relations you verified (calls/includes/inheritance). Use `sequenceDiagram` for flows, `classDiagram` for structure.
6. Forbidden words in the documents (internal process vocabulary): LLM, prompt, template, "candidate" as a status word, verification, promotion, llm_suggested, llm_identified, "static analysis result", "read the code directly". Write for end users. (The IPC "Candidate:" line format below is the one allowed use.)
7. Create/modify ONLY your two output files. Do not run any code2spec progress or cache tool.

## Output 1 — Module Design Card → code2spec/modules/<module>.md
```
# Module Design Card: <module>

> **Relevant source files**
>
> - [<every module file>](src:<path>)  … (all files, plus other cited files)

**Module**: `<module>` — <N> files under <directories>
**Role**: <one verified sentence> [`Sym`](src:path#L<n>)
**Module Boundary**: <rationale from module-groups.yaml>
**Confidence**: <confidence from module-groups.yaml>
**Core selection**: All approved modules are Core (boundary approved in W1 human review)
**Generated**: 2026-09-10

## Source Files
<all files as `src:` file links, grouped by subdirectory if helpful>

## Public Interface
| Function/Class | Signature | Main callers | Source |
8-20 rows of real externally-used entry points (classes/methods included or called from outside the module; find callers by grepping includes/usages across src/). Signature column in backticks as plain code (no link needed); Source column is the deep link.

## IPC / Message / Interface Contracts
- <verified contract summary>. [`Sym`](src:path#L<n>)
- Candidate: <summary>; confidence=HIGH|MEDIUM|LOW (<reason>). [`Sym`](src:path#L<n>)   ← only when evidence is partial
- If none: "- No cross-module IPC or message contract is identifiable in code for this module."
Then, only if contracts exist, 1-3 sentences on their architectural role (e.g. process boundary, async decoupling).
Not IPC: DOM events, in-process callbacks/observers, plain function calls, generic EventEmitter-style calls that stay inside the process.

## Key Flow
One or more ```mermaid sequenceDiagram``` blocks of verified call chains (≤5 depth), each followed by one sentence naming the entry symbol with a deep link.

## Architectural Rules
- [ ] <rule verified from code or consistent pattern> [`Sym`](src:path#L<n>)   (3-8 rules; write "Not specified in code" if none)

## Dependencies
### Internal modules
| Module | File(s) | Purpose | Source |   ← other approved logical modules this module includes/calls
### External libraries
| Library | Version | Purpose | Source |   ← from include lines (e.g. <unicode/…>, curl, cairo, GC); Version = "Not specified in code" unless a manifest states it

## Quick Navigation
| To change… | Location |   (6-12 rows, each a symbol deep link)

## FR Linkage
- [FR-<CODE>-001](../functional-requirements/<module>-fr.md#fr-<code>-001): <title>
…one line per FR in the FR document
```

## Output 2 — FR document → code2spec/functional-requirements/<module>-fr.md
```
# Functional Requirements: <module>

> **Relevant source files**
>
> - [<3-12 files>](src:<path>)

**Module**: [`<main file name>`](src:<path>)
**Version**: 2026-09-10
**Linked Design Card**: [modules/<module>.md](../modules/<module>.md)
**Analysis basis**: AST export and direct source reading

## Overview
1-3 sentences, each fact with a deep link.

## Functional Requirements
### FR-<CODE>-001
**<Title>**

| Item | Content |
|------|---------|
| **Description** | WHAT the module does (not how) |
| **Input** | data/parameters |
| **Output** | return values / side effects |
| **Preconditions** | … |
| **Postconditions** | … |
| **Source** | [`Sym`](src:path#L<n>) |

**Acceptance criteria**:
- [ ] …
(3-6 FRs for modules under 30 files; 6-12 for larger modules; each FR grounded in a real symbol)

## Non-Functional Requirements
| Item | Requirement | Source |   (Performance / Security / Error handling / Logging; "Not specified in code" where absent)

## Constraints
verified constraints, or "Not specified in code"

## Module Design Card Linkage
| FR | Implementation | Design Card section |

## ENUM Definitions
| ENUM | Values | Used in | Source |   ← llm-enum-results.json entries whose source file is in this module; convert `[Source: p:l]` to [`Name`](src:p#Ll); "None found in code" if empty

## Error Code Definitions
| Error code | Value | Trigger | Recovery | Source |   ← constants typed error_code or named ERR_/ERROR_/EXIT_ in this module; else "None found in code"

## Constant Definitions
| Constant | Value | Purpose | Source |   ← llm-constant-results.json entries for this module's files (cap 40 rows; state the total if more)

## Message Protocol
| Message ID | Direction | Payload | Handler | Mechanism | Source |   ← from llm-ipc-results.json or verified code; else "None found in code"

## Class Diagram
```mermaid
classDiagram
``` of verified inheritance/containment (5-15 classes)

## Sequence Diagram
```mermaid
sequenceDiagram
``` of the primary flow (verified calls, ≤5 depth)

## Test Cases
### Positive
### Negative
### Edge
bullet lists (input → expected) derived from verified behavior, each citing the governing symbol
```
FR CODE = module name upper-cased with hyphens kept (core-dom → CORE-DOM; FR-CORE-DOM-001). The FR heading is EXACTLY `### FR-CORE-DOM-001` with the title in bold on the next line, so the Design Card anchor `#fr-core-dom-001` resolves.

## Final report (your last message, ≤6 lines)
Files written, FR count, IPC contracts found (count), anything you could not ground. Do not paste document content.
