# Functional Requirements — public-delegate

> **Relevant source files**
> - [`LWEWebViewDelegateImpl.h`](src:src/public/delegate/LWEWebViewDelegateImpl.h)
> - [`LWEWebContainerDelegate.cpp`](src:src/public/delegate/LWEWebContainerDelegate.cpp)
> - [`JavaScriptNativeHandler.cpp`](src:src/public/delegate/JavaScriptNativeHandler.cpp)

## Given Factors

- Contract-delegate pattern across .so boundary
- Virtual dispatch for all API methods

## Overview

The delegate module provides concrete implementations of the contract interfaces, enabling embedders to control web views, containers, and workers.

## Functional Requirements

### FR-DELEGATE-001: WebView Operations
The system shall implement WebView operations: LoadURL, GetURL, LoadData, Reload, StopLoading, GoBack, GoForward, CanGoBack, CanGoForward, Pause, Resume.
- **Source:** [`LWEWebViewDelegateImpl.h`](src:src/public/delegate/LWEWebViewDelegateImpl.h#L28)

### FR-DELEGATE-002: JavaScript Evaluation
The system shall implement `EvaluateJavaScript` and `AddJavaScriptInterface` for JS execution.
- **Source:** [`LWEWebViewDelegateImpl.h`](src:src/public/delegate/LWEWebViewDelegateImpl.h#L54)

### FR-DELEGATE-003: Rendering Callbacks
The system shall register rendering callbacks: `RegisterPreRenderingHandler`, `RegisterOnRenderedHandler`.
- **Source:** [`LWEWebContainerDelegate.cpp`](src:src/public/delegate/LWEWebContainerDelegate.cpp)

### FR-DELEGATE-004: Debugger Callbacks
The system shall register debugger callbacks: `RegisterDebuggerShouldInitHandler`, `RegisterDebuggerShouldContinueWaitingHandler`.
- **Source:** [`LWEWebViewDelegateImpl.cpp`](src:src/public/delegate/LWEWebViewDelegateImpl.cpp)

### FR-DELEGATE-005: Worker Status
The system shall register worker status change callbacks via `RegisterOnStatusChangedHandler`.
- **Source:** [`LWEWorkerDelegate.cpp`](src:src/public/delegate/LWEWorkerDelegate.cpp)

### FR-DELEGATE-006: JavaScript Native Handler
The system shall provide `JavaScriptNativeHandler` for native JS callback integration.
- **Source:** [`JavaScriptNativeHandler.cpp`](src:src/public/delegate/JavaScriptNativeHandler.cpp)

## Dependencies

- public-contract, core-engine, compat-headers

## Code Factors

- C++, LGPL v2.1, virtual dispatch

## Quality

- Contract ABI checked by `check_contract_abi.py`
