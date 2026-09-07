# Functional Requirements — core-engine

> **Relevant source files**
> - [`Starfish.h`](src:src/Starfish.h)
> - [`Starfish.cpp`](src:src/Starfish.cpp)
> - [`StarfishBase.h`](src:src/StarfishBase.h)

## Given Factors

- GC-managed engine root (BDWGC)
- Three renderer types: OpenGL, Software, Headless
- Optional HTTP cache

## Overview

The core-engine module provides the root `Starfish` class, base type definitions, configuration, static string constants, and storage path management.

## Functional Requirements

### FR-CORE-001: Engine Initialization
The system shall initialize the engine with `StarfishConfiguration` providing storageDirectoryPath, gcFrequency, isThreadMode, backend, and rendererType.
- **Source:** [`Starfish.h`](src:src/Starfish.h#L49)

### FR-CORE-002: Renderer Type Selection
The system shall support three renderer types: kOpenGL, kSoftware, kHeadless.
- **Source:** [`Starfish.h`](src:src/Starfish.h#L43)

### FR-CORE-003: GC Configuration
The system shall configure BDWGC with `gcFrequency` (default: `BDWGC_FREE_SPACE_DIVISOR=12`).
- **Source:** [`Starfish.h`](src:src/Starfish.h#L40)

### FR-CORE-004: Static Strings
The system shall pre-allocate static string constants via `StaticStrings` for memory efficiency.
- **Source:** [`StaticStrings.h`](src:src/StaticStrings.h)

### FR-CORE-005: Storage Path
The system shall provide file system path management via `StoragePathProvider`.
- **Source:** [`StoragePathProvider.h`](src:src/StoragePathProvider.h)

### FR-CORE-006: HTTP Cache (Optional)
The system shall enable HTTP response caching when `STARFISH_ENABLE_HTTPCACHE` is defined.
- **Source:** [`Starfish.cpp`](src:src/Starfish.cpp#L32)

### FR-CORE-007: Aliveness Check
The system shall provide `isAlive()` check via `m_staticStrings` pointer validity.
- **Source:** [`Starfish.h`](src:src/Starfish.h#L73)

## Dependencies

- BDWGC, Escargot, platform-network, platform-message-loop, binding

## Code Factors

- C++, LGPL v2.1, GC-managed, NOT thread-safe constructor

## Quality

- Low memory via pre-allocated static strings
- Configurable GC frequency
