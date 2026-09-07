# Functional Requirements — browser-history

> **Relevant source files**
> - [`HistoryManager.h`](src:src/browser/history/HistoryManager.h)
> - [`HistoryManager.cpp`](src:src/browser/history/HistoryManager.cpp)

## Given Factors

- GC-managed history manager
- Max 256 entries
- WebView and HTMLIFrame ownership

## Overview

The browser-history module manages navigation history entries with state, title, and URL.

## Functional Requirements

### FR-HIST-001: History Entry
The system shall store history entries with state (SerializedTypedData), title (String), and url (ResourceURL).
- **Source:** [`HistoryManager.h`](src:src/browser/history/HistoryManager.h#L40)

### FR-HIST-002: Max Entry Size
The system shall limit history entries to `MAX_ENTRY_SIZE` = 256.
- **Source:** [`HistoryManager.h`](src:src/browser/history/HistoryManager.h#L39)

### FR-HIST-003: History Actions
The system shall support history actions: Add, Replace, Intact.
- **Source:** [`HistoryManager.h`](src:src/browser/history/HistoryManager.h#L33)

### FR-HIST-004: Ownership
The system shall track history ownership: OwnerIsWebView, OwnerIsHTMLIFrame.
- **Source:** [`HistoryManager.h`](src:src/browser/history/HistoryManager.h#L119)

## Dependencies

- core-engine, binding

## Code Factors

- C++, LGPL v2.1, GC-managed

## Quality

- Bounded history size (256 entries)
