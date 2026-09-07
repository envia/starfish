# Functional Requirements — platform-loader

> **Relevant source files**
> - [`Resource.h`](src:src/platform/loader/Resource.h)
> - [`ResourceClient.h`](src:src/platform/loader/ResourceClient.h)

## Given Factors

- GC-managed resource objects
- Multiple resource types (Image, Text, Font, Header)

## Overview

The loader module manages resource fetching lifecycle, from request initiation through receiving to completion or failure.

## Functional Requirements

### FR-LOADER-001: Resource State Machine
The system shall manage resource lifecycle states: BeforeSend, Receiving, Finished, Failed, Canceled.
- **Source:** [`Resource.h`](src:src/platform/loader/Resource.h#L42)

### FR-LOADER-002: Resource Type Classification
The system shall classify resources as Image, Text, Font, or Header type.
- **Source:** [`Resource.h`](src:src/platform/loader/Resource.h#L50)

### FR-LOADER-003: Resource Client Notification
The system shall notify resource clients of state changes via `ResourceClient` interface.
- **Source:** [`ResourceClient.h`](src:src/platform/loader/ResourceClient.h)

### FR-LOADER-004: Element Resource Client
The system shall provide `ElementResourceClient` for element-specific resource loading.
- **Source:** [`ElementResourceClient.cpp`](src:src/platform/loader/ElementResourceClient.cpp)

## Dependencies

- platform-network, core-engine

## Code Factors

- C++, LGPL v2.1, GC-managed

## Quality

- Friend class pattern for controlled access
