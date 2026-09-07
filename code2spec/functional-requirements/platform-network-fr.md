# Functional Requirements — platform-network

> **Relevant source files**
> - [`http/HTTPRequest.h`](src:src/platform/network/http/HTTPRequest.h)
> - [`http/HTTPTransaction.h`](src:src/platform/network/http/HTTPTransaction.h)
> - [`http/HTTPCache.h`](src:src/platform/network/http/HTTPCache.h)

## Given Factors

- libcurl-based HTTP client
- Optional HTTP response caching (STARFISH_ENABLE_HTTPCACHE)
- CORS and CSP support

## Overview

The network module provides HTTP request/response handling, transaction management, header processing, and optional response caching.

## Functional Requirements

### FR-NET-001: HTTP Request Creation
The system shall create HTTP requests with URL, base URL, method, headers, entity body, and credential options.
- **Source:** [`HTTPRequest.h`](src:src/platform/network/http/HTTPRequest.h#L29)

### FR-NET-002: HTTP Transaction
The system shall manage HTTP transactions via libcurl with handler registration.
- **Source:** [`HTTPTransaction.h`](src:src/platform/network/http/HTTPTransaction.h)

### FR-NET-003: HTTP Cache
The system shall cache HTTP responses when `STARFISH_ENABLE_HTTPCACHE` is enabled.
- **Source:** [`HTTPCache.h`](src:src/platform/network/http/HTTPCache.h), [`Starfish.h`](src:src/Starfish.h#L35)

### FR-NET-004: Shared Resource Management
The system shall manage shared curl resources via `NetworkSharedResourceManager`.
- **Source:** [`NetworkSharedResourceManager.h`](src:src/platform/network/curl/NetworkSharedResourceManager.h)

### FR-NET-005: Header Map
The system shall provide HTTP header storage via `HTTPHeaderMap`.
- **Source:** [`HTTPHeaderMap.h`](src:src/platform/network/http/HTTPHeaderMap.h)

## Dependencies

- libcurl, OpenSSL, core-engine, platform-loader

## Code Factors

- C++, LGPL v2.1, compile-time cache gating

## Quality

- CORS and CSP enforced per WHATWG spec
