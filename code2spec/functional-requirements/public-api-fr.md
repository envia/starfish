# Functional Requirements — public-api

> **Relevant source files**
> - [`LWEWebView.cpp`](src:src/public/LWEWebView.cpp)
> - [`LWEWorker.cpp`](src:src/public/LWEWorker.cpp)
> - [`APIRecorder.cpp`](src:src/public/APIRecorder.cpp)

## Given Factors

- LWE namespace public API
- Tizen version compatibility checks (5.0/5.5)
- API recording for testing

## Overview

The public-api module provides the embedding API surface (LWEWebView, LWEWorker) and API recording for test replay.

## Functional Requirements

### FR-API-001: LWEWebView API
The system shall provide LWEWebView API methods including Create, LoadURL, Reload, StopLoading, GoBack, GoForward, EvaluateJavaScript.
- **Source:** [`LWEWebView.cpp`](src:src/public/LWEWebView.cpp#L51)

### FR-API-002: LWEWorker API
The system shall provide LWEWorker API for web worker management with `RegisterOnStatusChangedHandler`.
- **Source:** [`LWEWorker.cpp`](src:src/public/LWEWorker.cpp)

### FR-API-003: Version Preference
The system shall provide `SetVersionPreference` for version selection.
- **Source:** [`LWEWebView.cpp`](src:src/public/LWEWebView.cpp#L59)

### FR-API-004: API Recording
The system shall record API calls via `APIRecorder` for later replay.
- **Source:** [`APIRecorder.cpp`](src:src/public/APIRecorder.cpp)

### FR-API-005: Tizen Version Check
The system shall enforce Tizen version compatibility (5.0 vs 5.5) at compile time.
- **Source:** [`LWEWebView.cpp`](src:src/public/LWEWebView.cpp#L43)

### FR-API-006: Delegate Loading
The system shall support dynamic delegate loading when `STARFISH_API_ENABLE_LOADER` is defined.
- **Source:** [`LWEWebView.cpp`](src:src/public/LWEWebView.cpp#L21)

## Dependencies

- public-contract, public-delegate, compat-headers

## Code Factors

- C++, LGPL v2.1, .so boundary

## Quality

- Asserts disabled in release builds
- Compile-time version compatibility enforcement
