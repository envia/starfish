# Functional Requirements — public-bridge

> **Relevant source files**
> - [`efl/LWEWebViewEFL.cpp`](src:src/public/bridge/efl/LWEWebViewEFL.cpp)
> - [`android/AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp)
> - [`flutter/LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp)

## Given Factors

- Multiple platform window system backends
- JNI for Android, EGL/TBM for Tizen, X11 for Linux

## Overview

The public-bridge module provides platform-specific window system integration, connecting the Starfish engine to native display systems (EFL, Ecore, X11, Flutter, Android).

## Functional Requirements

### FR-BRIDGE-001: EFL Integration
The system shall integrate with EFL using threaded TBM buffer presentation via raw EGL context.
- **Source:** [`LWEWebViewEFL.cpp`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L34)

### FR-BRIDGE-002: Android JNI Bridge
The system shall provide JNI bridge for Android with `callOnLoadResourceHandler` and `registerWebContainerHandler` entry points.
- **Source:** [`AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp)

### FR-BRIDGE-003: Flutter Bridge
The system shall support window backends (GB, GL, HEADLESS) and compositor backends (CAIRO, GL, MOCK) for Flutter integration.
- **Source:** [`LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L82)

### FR-BRIDGE-004: Owner State Management
The system shall manage web view ownership states: FREE, ENGINE, READY, DISPLAYING/PRESENTING.
- **Source:** [`LWEWebViewEFL.cpp`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L153)

### FR-BRIDGE-005: Event Handler Setup
The system shall register event handlers for platform window systems via `setupEventHandlers`.
- **Source:** [`LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp)

### FR-BRIDGE-006: Accessibility Bridge
The system shall provide AT-SPI accessibility bridge when `STARFISH_ENABLE_A11Y_ATSPI` is enabled.
- **Source:** [`A11yAtspiBridge.h`](src:src/public/bridge/efl/A11yAtspiBridge.h)

## Dependencies

- public-delegate, public-contract, EGL, EFL, JNI

## Code Factors

- C++/Java, LGPL v2.1, platform-conditional compilation

## Quality

- EGL header ordering critical for Tizen builds
