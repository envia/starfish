---
name: code2spec-structure-discovery
metadata:
  code-skills:
    id: code2spec/code2spec-structure-discovery
description: "Analyzes project directory structure and identifies architectural patterns. Scans core directories (app, src, components, routes), determines routing patterns, and generates directory tree diagrams or high-level architecture visualizations."
---

# Skill: Structure Discovery

## Objective

Analyze the physical directory structure and identify the overarching architectural patterns of the project.

## Instructions

1. Use `list_files` to scan the root and subdirectories (e.g., `/app`, `/src`, `/api`, `/components`).
2. Use `read_file` to examine key files for architectural patterns.
3. Identify the routing pattern used by the project.
4. Locate core layers: UI Components, API Routes, Services, and Repositories.

## Visualization Requirement

- Use the `code-to-diagram` skill to generate a **Directory Tree Diagram** or a **High-level Folder Architecture** in Mermaid format.
