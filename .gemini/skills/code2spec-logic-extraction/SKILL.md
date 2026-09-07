---
name: code2spec-logic-extraction
metadata:
  code-skills:
    id: code2spec/code2spec-logic-extraction
description: "Extracts business logic, rendering strategies, and algorithmic flows from source files. Analyzes page components, API handlers, data fetching methods (SSR/CSR), validation rules, and complex conditional flows. Generates sequence diagrams or logic flowcharts for complex request-response cycles."
---
# Skill: Deep Logic Extraction
## Objective
Extract business logic, rendering strategies, and algorithmic flows from individual source files.

## Instructions
1. Use `read_file` to analyze Page components, Server/Client components, and API Handlers.
2. Use `search_files` to find specific code patterns and logic flows.
3. Define the core logic of each module, including data fetching methods (SSR/CSR) and validation rules.
4. Identify complex conditional flows or mathematical algorithms.

## Visualization Requirement
- For complex logic or request-response cycles, use the `code-to-diagram` skill to generate a **Sequence Diagram** or **Logic Flowchart** in Mermaid format.
