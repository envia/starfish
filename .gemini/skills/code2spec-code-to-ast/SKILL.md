---
name: code2spec-code-to-ast
metadata:
  code-skills:
    id: code2spec/code2spec-code-to-ast
description: Export code graph as Markdown files (raw data and Mermaid diagrams) for AST analysis
argument-hint: "[--format raw|mermaid|both]"
---

# Code-to-AST

Export the AST graph as Markdown files for analysis and documentation.

## Steps

1. **Verify CLI is available** before running:

   ```bash
   PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
   ${PYTHON} .code2spec-tools/cli.py --help
   ```

   > ⛔ **If this command fails — STOP. Do not proceed with the workflow.**
   > Report the error to the user with the following message:
   >
   > ```
   > [ERROR] code-to-ast 의존성이 설치되어 있지 않습니다. 워크플로우를 중단합니다.
   > 원인: tree-sitter, tree-sitter-language-pack, 또는 networkx 미설치
   > 해결: install.py (또는 install.sh)를 먼저 실행하세요.
   > ```

2. **Run the export command**:

   ```bash
   PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
   ${PYTHON} .code2spec-tools/cli.py export \
     --output-dir "<target-path>/code2spec/.analysis/cache/code-to-ast"
   ```

   Or with options:

   ```bash
   PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
   ${PYTHON} .code2spec-tools/cli.py export \
     --format both \
     --workers 4 \
     --output-dir "<target-path>/code2spec/.analysis/cache/code-to-ast"
   ```

3. **Check the output files** in `code2spec/.analysis/cache/code-to-ast/` directory:

   - `graph-raw.md` - Raw node/edge data as tables
   - `graph-mermaid/00-summary.md` - File-level import diagram
   - `graph-mermaid/01-calls-all.md` - All function calls
   - `graph-mermaid/02-inherits.md` - Inheritance hierarchy
   - `graph-mermaid/03-tests.md` - Test relationships
   - `graph-mermaid/by-module/` - Module-level diagrams

4. **Report the results**:
   - Number of files parsed
   - Number of nodes and edges
   - Output file locations

## Options

- `--format`: Export format
  - `raw` - Only raw data (Markdown tables)
  - `mermaid` - Only Mermaid diagrams
  - `both` - Both formats (default)
- `--repo`: Repository root path (auto-detected)
- `--output-dir`: AST 산출물 저장 경로. code2spec 워크플로우에서는 `code2spec/.analysis/cache/code-to-ast` 권장
- `--workers N`: 병렬 파싱 워커 수 (기본값: 1=직렬). 대규모 프로젝트에서 `--workers 4` 권장
- `--cache-dir PATH`: 파싱 캐시 디렉토리 (기본값: `.code-to-ast/.cache/`)
- `--no-cache`: 파싱 캐시 비활성화

## Output Structure

```
code2spec/.analysis/cache/code-to-ast/
├── graph-raw.md              # Raw data tables (LLM 가독성)
├── graph-raw.json            # JSON 포맷 (ast_analyzer 빠른 로드용, 자동 생성)
└── graph-mermaid/
    ├── 00-summary.md         # File-level imports
    ├── 01-calls-all.md       # Function calls
    ├── 02-inherits.md        # Inheritance
    ├── 03-tests.md           # Test coverage
    └── by-module/            # Module diagrams
```

## Use Cases

- Generate documentation for code structure
- Analyze dependencies and call graphs
- Create visual representations for spec documents
- Understand codebase architecture
