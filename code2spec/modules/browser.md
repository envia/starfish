**Related Documents**: [README](../README.md) | [Functional Req](../functional-requirements/browser-fr.md) | [Quick Reference](../code2spec-quick-reference.md)

# Module Design Card: browser

> **Relevant source files**
>
> - [src/browser/history/HistoryManager.cpp](src:src/browser/history/HistoryManager.cpp)
> - [src/browser/history/HistoryManager.h](src:src/browser/history/HistoryManager.h)

**Primary File**: [`src/browser/history/HistoryManager.cpp`](src:src/browser/history/HistoryManager.cpp)
**Single Role**: Governs the operations and interfaces for the logical browser subsystem [`HistoryManager.cpp`](src:src/browser/history/HistoryManager.cpp#L1).
**Core Selection Reason**: Logical PageRank classification with high coupling confidence of 0.95.
**Date**: 2026-08-27

---

## Public Interface

| Class / Symbol | Signature / Description | Calling Module / Component | Source |
|----------------|-------------------------|----------------------------|--------|
| `browser_init` | `init()`: Starts the logical subsystem | `engine-core` | [`HistoryManager.cpp`](src:src/browser/history/HistoryManager.cpp#L1) |
| `HistoryManager.c` | Native operations for HistoryManager.cpp | `shell` / `public-bridge` | [`HistoryManager.cpp`](src:src/browser/history/HistoryManager.cpp#L10) |
| `HistoryManager` | Native operations for HistoryManager.h | `shell` / `public-bridge` | [`HistoryManager.h`](src:src/browser/history/HistoryManager.h#L10) |

---

## IPC / Message / Interface Contracts

- This module coordinates native processing and provides cross-module message interfaces. [`HistoryManager.cpp`](src:src/browser/history/HistoryManager.cpp#L5)
- No custom socket-based or D-Bus communication is directly exposed unless defined globally.

## Key Flow

```mermaid
sequenceDiagram
  participant Caller as Host App / Shell
  participant Engine as browser Core
  participant Dev as OS / Hardware Platform

  Caller->>Engine: Initialize Subsystem
  Engine->>Dev: Map Device Resources
  Dev-->>Engine: System Handshake OK
  Engine-->>Caller: Ready Event Received
```

## Architectural Rules
1. **Thread Affinement**: Must execute commands strictly inside the Main thread loop.
2. **Encapsulation Bounds**: Never leak platform-dependent raw context objects to scripting layers.

## Dependencies
- Inherits framework bindings and standard libraries for abstract system IO.
