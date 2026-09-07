# Functional Requirements — launcher

> **Relevant source files**
> - [`ServiceWorkerEntry.cpp`](src:src/launcher/ServiceWorkerEntry.cpp)
> - [`SharedWorkerEntry.cpp`](src:src/launcher/SharedWorkerEntry.cpp)

## Given Factors

- Compile-time gated by STARFISH_ENABLE_SERVICE_WORKER and STARFISH_WEBWORKER_HOST
- Standalone process entry points

## Overview

The launcher module provides standalone process entry points for service workers and shared workers.

## Functional Requirements

### FR-LAUNCH-001: Service Worker Entry
The system shall provide a `main()` entry point for service worker processes, parsing scriptURL and dataDir arguments.
- **Source:** [`ServiceWorkerEntry.cpp`](src:src/launcher/ServiceWorkerEntry.cpp#L55)

### FR-LAUNCH-002: Shared Worker Entry
The system shall provide a `main()` entry point for shared worker processes.
- **Source:** [`SharedWorkerEntry.cpp`](src:src/launcher/SharedWorkerEntry.cpp)

### FR-LAUNCH-003: Storage Directory
The system shall use `$HOME/Starfish-storage` as the default storage directory.
- **Source:** [`ServiceWorkerEntry.cpp`](src:src/launcher/ServiceWorkerEntry.cpp#L51)

### FR-LAUNCH-004: Signal Handling
The system shall register a signal handler that sets `g_workerDoneFlag` for graceful shutdown.
- **Source:** [`ServiceWorkerEntry.cpp`](src:src/launcher/ServiceWorkerEntry.cpp#L32)

### FR-LAUNCH-005: LWEWorker Integration
The system shall use `LWEWorker` API for worker lifecycle management.
- **Source:** [`ServiceWorkerEntry.cpp`](src:src/launcher/ServiceWorkerEntry.cpp#L28)

## Dependencies

- public-api (LWEWorker), compat-headers

## Code Factors

- C++, LGPL v2.1, compile-time gated

## Quality

- Graceful shutdown via signal handler
