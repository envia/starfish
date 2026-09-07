# 01 — Introduction

> **Relevant source files**
> - [`README.md`](README.md)
> - [`src/Starfish.h`](src:src/Starfish.h)
> - [`src/Starfish.cpp`](src:src/Starfish.cpp)
> - [`inc/LWEWebView.h`](inc:LWEWebView.h)
> - [`docs/Spec.md`](docs:Spec.md)

## Project Identity

**Project name:** Starfish

**Definition (from code):** "Starfish is a lightweight Web browser engine for TV, mobile, headless and wearable devices." [`README.md`](README.md)

**License:** GNU Lesser General Public License (LGPL) v2.1 — [`Starfish.h`](src:src/Starfish.h#L4)

**Copyright:** Samsung Electronics Co., Ltd (2015–present) — [`Starfish.h`](src:src/Starfish.h#L2)

## Purpose and Scope

Starfish is a browser engine designed for resource-constrained devices. The core constraint is **low runtime memory usage**, as stated in `AGENTS.md`: "low memory usage is the core constraint."

The engine supports:
- **TV, mobile, headless, and wearable devices** [`README.md`](README.md)
- Multiple platforms: Ubuntu 24.04/22.04 (x64, aarch64, armhf, x86 cross builds), Tizen, Windows, Android [`README.md`](README.md#L6)
- Web Platform Tests (WPT) as proof of spec compliance [`AGENTS.md`](AGENTS.md)

## Key Characteristics

| Characteristic | Detail | Source |
|---|---|---|
| JS Engine | Escargot (`third_party/escargot`) | [`AGENTS.md`](AGENTS.md) |
| GC | Boehm-Demers-Weiser GC (BDWGC) | [`Starfish.h`](src:src/Starfish.h#L39) |
| Renderer types | OpenGL, Software, Headless | [`Starfish.h`](src:src/Starfish.h#L43) |
| Build system | CMake + Ninja | [`README.md`](README.md#L51) |
| Binding generation | `.idl` files → JS bindings (cmake-time) | [`README.md`](README.md#L55) |
| Default-off posture | Heavy/optional features compile-time gated | [`AGENTS.md`](AGENTS.md) |

## Source Layout

| Directory | Role |
|---|---|
| `src/core/` | Engine proper (DOM, style, layout, etc.) — not in AST scope (submodule) |
| `src/binding/` | JavaScript engine binding layer (Escargot integration) |
| `src/platform/` | Platform abstractions (canvas, network, multimedia, etc.) |
| `src/public/` | Embedding API (`bridge/` = per-platform, `delegate/` = implementation, `contract/` = pure-virtual interfaces) |
| `src/shell/` | Browser shell (MiniBrowser, Console, Window) |
| `src/launcher/` | Worker entry points |
| `inc/` | Public headers for embedders |
| `compat/` | Tizen compatibility headers |
| `tool/` | Test drivers, WPT scripts, lint, CI tools |
| `third_party/` | Third-party libraries (robin_map, escargot) |

## Document Scope

This document set covers the **embedding API, platform layer, binding layer, shell, and tooling** of Starfish. The `src/core/` engine internals (DOM, CSS, layout, paint) are in a separate submodule and are not in the AST analysis scope.
