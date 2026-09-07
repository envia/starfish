---
name: code2spec-pattern-mapping
metadata:
  code-skills:
    id: code2spec/code2spec-pattern-mapping
description: "Maps dependencies between modules and tracks data flow through state management and props. Identifies Context Providers, custom Hooks, global state stores, traces parent-child component data passing, and maps shared utility modules. Generates component dependency diagrams and module relationship maps."
---

# Skill: Pattern & Relationship Mapping

## Objective

Map the dependencies between modules and track the flow of data through state management and props.

## Instructions

1. Use `search_files` to find usages of Context Providers, Hooks, and global state stores.
2. Use `read_file` to examine component implementations and data flow.
3. Trace how data is passed from Parent to Child components or across different Route Handlers.
4. Identify shared utility modules and their impact on the system.

## Visualization Requirement

- Use the `code-to-diagram` skill to generate a **Component Dependency Diagram** or a **Module Relationship Map** in Mermaid format.
