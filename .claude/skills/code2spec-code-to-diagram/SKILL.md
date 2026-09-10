---
name: code2spec-code-to-diagram
metadata:
  code-skills:
    id: code2spec/code2spec-code-to-diagram
description: "Generate architecture diagrams, ER diagrams, sequence diagrams, flowcharts, and class diagrams from codebases using Mermaid.js. Use when users ask to visualize code structure, draw architecture diagrams, create ER diagrams from database models, generate sequence diagrams from API flows, or produce any diagram from source code. Triggers on: 'draw architecture', 'generate diagram', 'visualize code', 'ER diagram', 'sequence diagram', 'class diagram', 'flowchart from code', 'module dependency graph'."
---

# Code to Diagram

Generate production-quality diagrams from source code via Mermaid.js, rendered to SVG/PNG with `mmdc`.

## Environment

**Executor required:** This skill needs the `diagram` executor (Chromium + Node.js + mmdc pre-installed).
If `mmdc` is not available, install first:
```bash
npm install -g @mermaid-js/mermaid-cli
```

Puppeteer config for headless environments — create at `/tmp/puppeteer-config.json` if missing:
```json
{"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
```

## Workflow

1. **Analyze** — Read the codebase to understand structure (`glob`, `grep`, `read`)
2. **Plan** — Decide diagram type(s) based on user request and code patterns
3. **Generate** — Write `.mmd` file with Mermaid syntax
4. **Render** — Run `mmdc` to produce SVG and PNG
5. **Verify** — Read the output image and check correctness

## Diagram Type Selection

| User Intent | Diagram Type | Mermaid Keyword |
|-------------|-------------|-----------------|
| System overview, module layout | Architecture | `graph TD` + `subgraph` |
| Database tables, ORM models | ER Diagram | `erDiagram` |
| API flow, request lifecycle | Sequence Diagram | `sequenceDiagram` |
| Inheritance, interfaces | Class Diagram | `classDiagram` |
| Business logic, conditionals | Flowchart | `flowchart TD` |
| Task states, lifecycle | State Diagram | `stateDiagram-v2` |
| Import/dependency tree | Dependency Graph | `graph LR` |
| Timeline, project phases | Gantt Chart | `gantt` |

## Analysis Strategy

Do NOT read every file. Use progressive analysis:

**Step 1 — Directory scan:**
`glob("**/*.py")` or `glob("**/*.ts")` to understand module structure.

**Step 2 — Entry points:**
- Python: `main.py`, `app.py`, `__init__.py`, `pyproject.toml`
- Node.js: `package.json`, `index.ts`, `app.ts`
- Java: `pom.xml`, `Application.java`

**Step 3 — Targeted reads by diagram type:**
- **ER** → ORM models (`models.py`, `schema.prisma`, `*.entity.ts`)
- **Architecture** → Router registrations, dependency injection, config
- **Sequence** → Specific endpoint handler + service call chain
- **Class** → Class definitions via `grep("class ")`

**Step 4 — GitHub repos:**
```bash
git clone --depth 1 <url> /tmp/repo-name
```
Then apply the same progressive scan.

## Rendering

```bash
# SVG (transparent background, good for docs)
mmdc -i diagram.mmd -o diagram.svg -b transparent -p /tmp/puppeteer-config.json

# PNG (white background, 2x scale for sharpness)
mmdc -i diagram.mmd -o diagram.png -b white -s 2 -p /tmp/puppeteer-config.json
```

Always generate both formats. Use `-s 2` for PNG (sharp at any zoom level).

## Mermaid Syntax Reference

For detailed patterns and examples per diagram type, see [references/mermaid-patterns.md](references/mermaid-patterns.md).

Key rules:
- Short IDs, descriptive labels: `DB[("PostgreSQL 16")]`
- Use `subgraph` for logical grouping in architecture diagrams
- Limit ER diagrams to ~10 entities — split by domain if larger
- `participant` aliases in sequence diagrams for short names
- Quote labels with special chars — **node AND edge labels**: `A["Node (v1)"]`, and pipe-edge labels too: `A -->|"HTTP /api/search"| B` (an unquoted `/`, space, `.`, `:`, `()` in a `-->|label|` breaks mermaid v10 parsing → mermaidSyntax hard-gate FAIL)
- Max ~20 nodes per diagram — split into multiple if larger

## Validation-Aware Diagram Rules (code2spec-wiki)

When diagrams are embedded in SDD output that the wiki validation pipeline checks
(`diagramAccuracy`, `mermaidSyntax`), the following rules apply **in addition to** the
above. They affect validation scores, so they override the general "short IDs" guidance
where they conflict.

**diagramAccuracy — `graph`/`flowchart` edges must be backed by `.ast/deps.json`:**
- **Node ID = a real AST/deps token**, not an arbitrary abbreviation. Use a file basename
  without extension (`MCPServer.ts` → `MCPServer`), a symbol from `.ast/api.json`
  (`RetrieverService`), a `depends_on[].from`/`to` path token, or an external package
  basename (`sqlite`). Arbitrary IDs (`ModA`, `Srv`, `DB`, `Client`) are flagged as
  *unknown-node*. Keep the human-readable name in the quoted **label**: `ctl["SsoAuthController"]`.
- **Draw an edge only when a relation backs it**, in the same direction as in `.ast/deps.json`
  (`internal`/`external`/`depends_on`/`calls`/`inherits`/`implements`). Do not reverse
  direction for aesthetics; do not chain (`A --> B --> C` → separate lines). `contains[]`
  (class→method) is described in prose/tables, not as an edge.
- **Runtime coupling is not a `graph` edge.** HTTP requests, shared DB, message buses, user
  flows — anything not backed by a static import/call — goes in a `sequenceDiagram`
  (not checked by `diagramAccuracy`), not a `graph`/`flowchart`.
- **External / conceptual nodes (not in AST) → mark them `external`.** Nodes that do not exist in
  the codebase AST — external IdPs, external DBs, clients (ADFS, SQLite, Cline, …) — must be
  **marked as external explicitly**. `diagramAccuracy` then **excludes from scoring** every edge
  that touches such a node (only internal edges are validated). Either form works:
  - inline: `ADFS["ADFS (external IdP)"]:::external`
  - statement: `class ADFS,SQLITE_AUTH external`
  An arbitrary node that is *not* marked external still fails the hard gate as `unknown-node`.
  **Do not use `external` as an escape hatch for internal entities that are in the AST** — real
  code relations must go through validation normally.

**mermaidSyntax — keep blocks parseable (HARD gate; one unquoted label fails the whole build):**
- **Quote EVERY label — node, edge, and subgraph — if it contains a space or any of ``@ / \ . : ( ) { } % # &``.** This is the most common failure. Edge (pipe) labels are the usual miss:
  - ❌ `A -->|HTTP /api/search| B` · ❌ `A -->|search/ingest| B` · ❌ `A[/api/eval]`
  - ✅ `A -->|"HTTP /api/search"| B` · ✅ `A -->|"search/ingest"| B` · ✅ `A["/api/eval"]`
- A label containing a URL, a path or a slash **always** takes double quotes. (validate-mermaid
  reports it as `unescaped /`.)
- The first line of a block is the diagram type (`graph LR`, `flowchart TD`, `sequenceDiagram`);
  do not leave a blank line before it.

## Output Conventions

- Write `.mmd` source + rendered files to workspace
- Descriptive names: `architecture.mmd`, `er-diagram.png`, `api-sequence.svg`
- Multiple diagrams → create `diagrams/` folder with index

## Quality Checklist

- All entities/modules from the code are represented
- Relationships and data flow directions are correct
- Labels readable, not truncated or overlapping
- No Mermaid syntax errors
- Output image visually verified
