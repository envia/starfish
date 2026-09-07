---
name: code2spec-doc-generation
metadata:
  code-skills:
    id: code2spec/code2spec-doc-generation
description: "Consolidates analysis results into structured Markdown files for Software Design Documentation (Spec). Enforces a strict Zero-Inference Policy and generates a modular file structure (including a dedicated /modules directory) to ensure high-fidelity documentation based solely on code artifacts."
---

# Skill: Documentation Generation (Evidence-Based)

## Objective

Generate a structured, hyperlinked set of Markdown documents that accurately represent the system's technical reality without adding external assumptions or creative interpretations.

## 🚫 Zero-Inference & Strict Data-Driven Principle

### 1. Evidence-Only Documentation

- **Source of Truth:** Extract information ONLY from actual project files (source code, config, README, official docs).
- **Prohibit Hallucination:** Never use internal LLM knowledge to fill gaps. If a purpose is not found, state "Not specified in codebase."
- **Citation form = backticked deep link** (see §"Source Citation Discipline" below). Write every citation of an external source as ``[`Sym`](src:path#L<n>)``.

### 2. Prohibit Arbitrary Inferences

- **No Name Expansion:** Do not infer meaning from project names or abbreviations (e.g., "SIRIUS" remains "SIRIUS" unless a literal definition is found in comments).
- **No Contextual Guessing:** Do not assume application types or business goals based on common class names (e.g., a "User" class does not prove it is a "Social Media App").

### 3. Missing Data Protocol

- When information is missing, use these fallback phrases:
  - `"Not specified in code"`
  - `"Technical implementation identified, but business intent not documented"`
  - `"Value/Definition not found in codebase"`

---

## Instructions

1. **Language Sync:** Write all content in the language selected by the user in Workflow Step 2.
2. **Hyperlink Network:** Ensure all files are interconnected. The `README.md` must link to all chapters and every module file.
3. **Mermaid Integration:** Embed Mermaid code blocks from `code-to-diagram` into relevant sections. Ensure valid syntax for rendering.
4. **File Writing:** Use `write_to_file` to create the directory structure and all `.md` files.
5. **Fixed Layout (MANDATORY):** Write every chapter plus `README.md`, `code2spec-quick-reference.md` and `history.md` **directly into the root of** `OUTPUT_DIR` (= `code2spec/`). **Do not create arbitrary subfolders such as `sdd/`.** Modules and FRs go under `modules/` and `functional-requirements/`. Output of skills such as `logic-extraction` and `pattern-mapping` **must not be left behind as separate loose .md files** — absorb it into the relevant chapter or module card. (Validated by: `code2spec-doc-review` / `validate_layout.py`)

## Source Citation Discipline — Backticked Deep Links (Default & Mandatory)

**Write every external source citation as a backticked deep link from the start.**
(A deep link is the only form accepted by server-side rendering and grounding validation — the rule
is to emit deep links at generation time; the deterministic conversion in finalize is only a safety
net.) For details see
[references/grounding-and-deep-links.md](references/grounding-and-deep-links.md):

- Every .md opens (directly under the H1) with a `> **Relevant source files**` blockquote block — a
  list of file-level deep links.
- Cite code symbols as backticked **deep links** ``[`Sym`](src:path#L<n>)`` — take the line from
  `.ast/api.json`, and **omit the host prefix** — `repo.json.deepLink.base` is prepended at render
  time (issue #54). The W1 (discovery) prepare step generates `.ast`/`repo.json` first, so this
  evidence always exists by the time chapters are written.
- Every factual statement either carries such a deep-link citation or leaves a missing-data marker
  such as "Not specified in code" (§Missing Data Protocol).

For Mermaid node IDs, edges and quoting, follow the "Validation-Aware Diagram Rules" section of the
`code2spec-code-to-diagram` skill.

## Visualization Requirement

- Ensure diagrams are context-aware (e.g., place a Sequence Diagram in the Logic section, not the Overview).

# CRITICAL RULE FOR INTRODUCTION

You are acting as a strict code auditor, not a technical writer. When writing 01-introduction.md, you are forbidden from expanding project names or acronyms (e.g., MBR, SIRIUS) unless you can explicitly quote the definition from a specific file in the repository. If no definition exists, strictly state: "Project name is [Name]. Definition and business purpose are not documented in the analyzed files."

---
