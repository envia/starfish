# Functional Requirements — platform-message-loop

> **Relevant source files**
> - [`MessageLoopGLib.cpp`](src:src/platform/message_loop/MessageLoopGLib.cpp)
> - [`Timer.h`](src:src/core/modules/message_loop/Timer.h)

## Given Factors

- Two event loop backends: GLib (default), libUV (optional)
- Rendezvous mechanism for thread coordination

## Overview

The message loop module provides event loop abstraction with timer support and thread rendezvous coordination.

## Functional Requirements

### FR-ML-001: GLib Event Loop
The system shall provide a GLib-based event loop backend.
- **Source:** [`MessageLoopGLib.cpp`](src:src/platform/message_loop/MessageLoopGLib.cpp)

### FR-ML-002: libUV Event Loop
The system shall provide a libUV-based event loop backend as alternative.
- **Source:** [`MessageLoopLibUV.cpp`](src:src/platform/message_loop/MessageLoopLibUV.cpp)

### FR-ML-003: Timer Support
The system shall provide timer functionality for scheduled callbacks.
- **Source:** [`Timer.h`](src:src/core/modules/message_loop/Timer.h)

### FR-ML-004: Rendezvous
The system shall coordinate main thread and LWE thread via RendezvousOwner states: None, MainBlockedOnLWE, LWEPausingMain.
- **Source:** [`MessageLoopGLib.cpp`](src:src/platform/message_loop/MessageLoopGLib.cpp#L99)

## Dependencies

- GLib, libUV, core-engine

## Code Factors

- C++, LGPL v2.1

## Quality

- Thread-safe rendezvous for engine/main coordination
