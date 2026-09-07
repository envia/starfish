# Functional Requirements — platform-process

> **Relevant source files**
> - [`base/ProcessType.h`](src:src/platform/process/base/ProcessType.h)

## Given Factors

- Cross-platform PID abstraction

## Overview

The process module provides platform-agnostic process type definitions.

## Functional Requirements

### FR-PROC-001: PID Type
The system shall define `PID` as `pid_t` on POSIX and `DWORD` on Windows.
- **Source:** [`ProcessType.h`](src:src/platform/process/base/ProcessType.h#L25)

## Dependencies

- POSIX / Windows API

## Code Factors

- C++, LGPL v2.1

## Quality

- Cross-platform abstraction
