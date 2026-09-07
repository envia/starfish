# Functional Requirements — shell

> **Relevant source files**
> - [`Shell.cpp`](src:src/shell/Shell.cpp)
> - [`MiniBrowser.cpp`](src:src/shell/MiniBrowser.cpp)
> - [`UnitTestRunner.cpp`](src:src/shell/UnitTestRunner.cpp)

## Given Factors

- C++ browser shell application
- Default resolution 1920x1080
- Multiple platform window backends (EFL, X11, Windows, headless)

## Overview

The shell module provides the browser application entry point, window management, console I/O, unit test execution, and API replay for the Starfish engine.

## Functional Requirements

### FR-SHELL-001: Browser Launch
The system shall launch the browser shell with a URL argument and optional debug flags.
- **Source:** [`Shell.cpp`](src:src/shell/Shell.cpp#L74)

### FR-SHELL-002: Argument Parsing
The system shall parse command-line arguments including `--dump-computed-style`, `--dump-frame-tree`, `--pixel-test`, `--width`, `--height`.
- **Source:** [`MiniBrowser.cpp`](src:src/shell/MiniBrowser.cpp#L47)

### FR-SHELL-003: Signal Handling
The system shall register signal handlers and backtrace handlers for crash diagnostics.
- **Source:** [`Shell.cpp`](src:src/shell/Shell.cpp)

### FR-SHELL-004: Memory Optimization
The system shall configure malloc parameters (`M_MMAP_THRESHOLD=2048`, `M_MMAP_MAX=1048576`) for MSE packet memory efficiency.
- **Source:** [`Shell.cpp`](src:src/shell/Shell.cpp#L66)

### FR-SHELL-005: Unit Test Execution
The system shall provide a unit test runner for the public embedding API.
- **Source:** [`UnitTestRunner.cpp`](src:src/shell/UnitTestRunner.cpp)

### FR-SHELL-006: API Replay
The system shall record and replay LWEWebView API calls for testing and debugging.
- **Source:** [`APIReplayer.cpp`](src:src/shell/APIReplayer.cpp)

## Dependencies

- core-engine, public-api, compat-headers

## Code Factors

- C++, LGPL v2.1
- Platform-conditional compilation (EFL, X11, Windows, headless)

## Quality

- Unit tests: WebViewTest, CookieManagerTest, LWETest, SettingsTest, WebContainerTest
