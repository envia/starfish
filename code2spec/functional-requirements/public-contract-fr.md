# Functional Requirements — public-contract

> **Relevant source files**
> - [`LWEWebViewDelegate.h`](src:src/public/contract/LWEWebViewDelegate.h)
> - [`LWEWorkerDelegate.h`](src:src/public/contract/LWEWorkerDelegate.h)
> - [`CookieManagerDelegate.h`](src:src/public/contract/CookieManagerDelegate.h)

## Given Factors

- Pure-virtual interfaces across .so boundary
- ABI stability enforced by check_contract_abi.py

## Overview

The contract module defines the pure-virtual interfaces that the embedding API and delegate implementations share across the shared library boundary.

## Functional Requirements

### FR-CONTRACT-001: WebView Contract
The system shall define a pure-virtual `WebView` interface with Create, Destroy, GetSettings, LoadURL, GetURL, LoadData, Reload, StopLoading, GoBack, GoForward, CanGoBack, CanGoForward.
- **Source:** [`LWEWebViewDelegate.h`](src:src/public/contract/LWEWebViewDelegate.h#L35)

### FR-CONTRACT-002: Worker Contract
The system shall define a pure-virtual `Worker` interface with `RegisterOnStatusChangedHandler`.
- **Source:** [`LWEWorkerDelegate.h`](src:src/public/contract/LWEWorkerDelegate.h)

### FR-CONTRACT-003: Cookie Manager Contract
The system shall define a pure-virtual `CookieManager` interface for cookie management.
- **Source:** [`CookieManagerDelegate.h`](src:src/public/contract/CookieManagerDelegate.h)

### FR-CONTRACT-004: Settings Contract
The system shall define a pure-virtual `Settings` interface for configuration.
- **Source:** [`SettingsDelegate.h`](src:src/public/contract/SettingsDelegate.h)

### FR-CONTRACT-005: Resource Error Contract
The system shall define a pure-virtual `ResourceError` interface for error handling.
- **Source:** [`ResourceErrorDelegate.h`](src:src/public/contract/ResourceErrorDelegate.h)

### FR-CONTRACT-006: ABI Stability
The system shall maintain ABI stability verified by `check_contract_abi.py`.
- **Source:** [`AGENTS.md`](src:AGENTS.md)

## Dependencies

- LWEDelegateConfig

## Code Factors

- C++, LGPL v2.1, pure-virtual interfaces

## Quality

- ABI checked in CI pipeline
