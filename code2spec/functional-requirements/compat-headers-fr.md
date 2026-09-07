# Functional Requirements — compat-headers

> **Relevant source files**
> - [`inc/LWEWebView.h`](src:inc/LWEWebView.h)
> - [`inc/PlatformIntegrationData.h`](src:inc/PlatformIntegrationData.h)
> - [`compat/tizen_5.0/inc/LWEWebView.h`](src:compat/tizen_5.0/inc/LWEWebView.h)

## Given Factors

- Public headers for embedders
- Tizen 5.0 compatibility layer
- Platform export macros

## Overview

The compat-headers module provides the public C++ header files that embedders include to use the Starfish engine, plus Tizen 5.0 backward compatibility.

## Functional Requirements

### FR-COMPAT-001: Export Macro
The system shall provide `LWE_EXPORT` macro for cross-platform symbol export (dllexport/dllimport on MSVC, visibility on GCC).
- **Source:** [`LWEWebView.h`](src:inc/LWEWebView.h#L29)

### FR-COMPAT-002: Delegate Reference
The system shall provide `LWEDelegateRef` as `unique_ptr<void, function<void(void*)>>` for delegate lifetime management.
- **Source:** [`LWEWebView.h`](src:inc/LWEWebView.h#L49)

### FR-COMPAT-003: Key Value Enum
The system shall define 229 KeyValue types for keyboard input.
- **Source:** [`PlatformIntegrationData.h`](src:inc/PlatformIntegrationData.h#L7)

### FR-COMPAT-004: Mouse Button Enum
The system shall define MouseButtonValue: NoButton, LeftButton, MiddleButton, RightButton.
- **Source:** [`PlatformIntegrationData.h`](src:inc/PlatformIntegrationData.h#L239)

### FR-COMPAT-005: TTS Mode
The system shall define TTSMode: Default, Forced.
- **Source:** [`PlatformIntegrationData.h`](src:inc/PlatformIntegrationData.h#L253)

### FR-COMPAT-006: Font Size Constants
The system shall define font size limits: default=16, min=1, max=72.
- **Source:** [`LWEWebView.h`](src:compat/tizen_5.0/inc/LWEWebView.h#L180)

### FR-COMPAT-007: Tizen 5.0 Compatibility
The system shall provide Tizen 5.0 compatible headers in `compat/tizen_5.0/`.
- **Source:** [`compat/tizen_5.0/inc/LWEWebView.h`](src:compat/tizen_5.0/inc/LWEWebView.h)

## Dependencies

- C++ standard library

## Code Factors

- C++ headers, LGPL v2.1

## Quality

- Cross-platform export macros
- Comprehensive key event coverage
