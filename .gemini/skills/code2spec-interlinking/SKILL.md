---
name: code2spec-interlinking
metadata:
  code-skills:
    id: code2spec/code2spec-interlinking
description: "Creates cohesive navigation structure between Spec documents. Analyzes generated files to determine relative paths, inserts hyperlinks between related sections using cross-referencing, and generates README.md or Index.md as the main Table of Contents. Ensures every document contains functional Markdown links for easy exploration."
---

# Skill: Knowledge Interlinking

## Objective

Create a cohesive navigation structure between disparate Spec documents for easy exploration.

## Instructions

1. Analyze the generated file set to determine relative paths using `list_files`.
2. Create markdown hyperlinks manually to link related sections (e.g., linking a Component list to its Detailed Module View).
3. Generate a `README.md` or `Index.md` as the main Table of Contents.
4. Use markdown link syntax: `[Link Text](./relative/path/to/file.md)`

## Requirement

- Every document must contain a "Next Steps" or "Related Modules" section with functional Markdown links.
