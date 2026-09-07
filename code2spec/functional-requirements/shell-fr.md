**Related Documents**: [README](../README.md) | [Module Card](../modules/shell.md) | [Quick Reference](../code2spec-quick-reference.md)

# Functional Requirements: shell

> **Relevant source files**
>
> - [src/shell/APIReplayer.cpp](src:src/shell/APIReplayer.cpp)
> - [src/shell/APIReplayer.h](src:src/shell/APIReplayer.h)
> - [src/shell/AppLoop.h](src:src/shell/AppLoop.h)
> - [src/shell/Console.cpp](src:src/shell/Console.cpp)
> - [src/shell/Console.h](src:src/shell/Console.h)
> - [src/shell/MiniBrowser.cpp](src:src/shell/MiniBrowser.cpp)
> - [src/shell/MiniBrowser.h](src:src/shell/MiniBrowser.h)
> - [src/shell/RendererDelegate.h](src:src/shell/RendererDelegate.h)
> - [src/shell/Shell.cpp](src:src/shell/Shell.cpp)
> - [src/shell/Shell.h](src:src/shell/Shell.h)
> - [src/shell/ShellConfig.h](src:src/shell/ShellConfig.h)
> - [src/shell/UnitTestRunner.cpp](src:src/shell/UnitTestRunner.cpp)
> - [src/shell/UnitTestRunner.h](src:src/shell/UnitTestRunner.h)
> - [src/shell/Window.h](src:src/shell/Window.h)
> - [src/shell/WindowKeyType.h](src:src/shell/WindowKeyType.h)
> - [src/shell/dummy/WindowDummy.cpp](src:src/shell/dummy/WindowDummy.cpp)
> - [src/shell/ecore/AppLoopEcore.cpp](src:src/shell/ecore/AppLoopEcore.cpp)
> - [src/shell/ecore/ConsoleEcore.cpp](src:src/shell/ecore/ConsoleEcore.cpp)
> - [src/shell/efl/AppLoopEFL.cpp](src:src/shell/efl/AppLoopEFL.cpp)
> - [src/shell/efl/AppLoopEFLHeadless.cpp](src:src/shell/efl/AppLoopEFLHeadless.cpp)
> - [src/shell/efl/ConsoleEFL.cpp](src:src/shell/efl/ConsoleEFL.cpp)
> - [src/shell/efl/WindowEFL.cpp](src:src/shell/efl/WindowEFL.cpp)
> - [src/shell/glib/AppLoopGlib.cpp](src:src/shell/glib/AppLoopGlib.cpp)
> - [src/shell/glib/ConsoleGlib.cpp](src:src/shell/glib/ConsoleGlib.cpp)
> - [src/shell/headless/WindowHeadless.cpp](src:src/shell/headless/WindowHeadless.cpp)
> - [src/shell/libuv/AppLoopLibuv.cpp](src:src/shell/libuv/AppLoopLibuv.cpp)
> - [src/shell/libuv/ConsoleLibuv.cpp](src:src/shell/libuv/ConsoleLibuv.cpp)
> - [src/shell/tcore_wl/AppLoopTcoreWl.cpp](src:src/shell/tcore_wl/AppLoopTcoreWl.cpp)
> - [src/shell/tcore_wl/ConsoleTcoreWl.cpp](src:src/shell/tcore_wl/ConsoleTcoreWl.cpp)
> - [src/shell/test/APIRecorderTest.cpp](src:src/shell/test/APIRecorderTest.cpp)
> - [src/shell/test/CookieManagerTest.cpp](src:src/shell/test/CookieManagerTest.cpp)
> - [src/shell/test/LWETest.cpp](src:src/shell/test/LWETest.cpp)
> - [src/shell/test/SettingsTest.cpp](src:src/shell/test/SettingsTest.cpp)
> - [src/shell/test/WebContainerTest.cpp](src:src/shell/test/WebContainerTest.cpp)
> - [src/shell/test/WebViewTest.cpp](src:src/shell/test/WebViewTest.cpp)
> - [src/shell/windows/RendererWGL.cpp](src:src/shell/windows/RendererWGL.cpp)
> - [src/shell/windows/RendererWGL.h](src:src/shell/windows/RendererWGL.h)
> - [src/shell/windows/StarfishShell.cpp](src:src/shell/windows/StarfishShell.cpp)
> - [src/shell/x11_webcontainer/WindowX11Webcontainer.cpp](src:src/shell/x11_webcontainer/WindowX11Webcontainer.cpp)

**Module**: [`src/shell/APIReplayer.cpp`](src:src/shell/APIReplayer.cpp)
**Version**: 2026-08-27
**Connected Design Card**: [modules/shell.md](../modules/shell.md)

---

## Overview

This module provides functional capabilities for shell within the Lightweight Web Engine, fulfilling design specifications and platform constraints.

---

## Functional Requirements

### FR-015-01: Core Operation of shell

| Item | Content |
|------|---------|
| **Description** | Executes native tasks and handles domain abstractions for the module |
| **Input** | Subsystem config and hardware capabilities |
| **Output** | Status flags and allocated resources |
| **Pre-conditions** | System main loop must be active |
| **Post-conditions** | Core state is correctly transitioned |
| **Source** | [`APIReplayer.cpp`](src:src/shell/APIReplayer.cpp#L1) |

**Acceptance Criteria**:
- [ ] Task executes without thread blocks
- [ ] Resource boundaries are strictly observed

---

## Non-Functional Requirements

| Item | Requirement | Source |
|------|-------------|--------|
| Performance | Initialization completes in less than 5ms | [`APIReplayer.cpp`](src:src/shell/APIReplayer.cpp#L1) |
| Security | Sanitizes state and handles boundary inputs | [`APIReplayer.cpp`](src:src/shell/APIReplayer.cpp#L1) |

---

## Constraints
- Memory boundaries strictly configured by general heap allocation.

---

## Module Design Card Linkage

| FR | Implementation Location | Design Card Section |
|----|-------------------------|---------------------|
| FR-015-01 | [`APIReplayer.cpp`](src:src/shell/APIReplayer.cpp#L1) | Public Interface |
