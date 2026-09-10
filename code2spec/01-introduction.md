# Introduction

> **Relevant source files**
>
> - [README.md](src:README.md)
> - [CMakeLists.txt](src:CMakeLists.txt)
> - [.gitmodules](src:.gitmodules)
> - [vcpkg.json](src:vcpkg.json)
> - [vcpkg-configuration.json](src:vcpkg-configuration.json)
> - [packaging/lightweight-web-engine.spec](src:packaging/lightweight-web-engine.spec)
> - [inc/LWEWebView.h](src:inc/LWEWebView.h)
> - [src/core/cdp/CDPServer.h](src:src/core/cdp/CDPServer.h)
> - [src/core/inspector/Inspector.h](src:src/core/inspector/Inspector.h)
> - [src/binding/ScriptBindingInstance.h](src:src/binding/ScriptBindingInstance.h)
> - [docs/Spec.md](src:docs/Spec.md)
> - [AGENTS.md](src:AGENTS.md)

## System Purpose

Starfish is "a lightweight Web browser engine for TV, mobile, headless and wearable devices" ([`README.md`](src:README.md#L3)). The repository's agent guide restates this and adds that "low memory usage is the core constraint", that "the relevant WHATWG/W3C/ECMA-262 spec is the source of truth for behavior", and that "Web Platform Tests (WPT) are the proof of spec compliance" ([`AGENTS.md`](src:AGENTS.md#L3)). The engine's feature surface is described in a dedicated specification document, which "describes the complete list of features supported by the lightweight Web engine (LWE)" ([`Spec.md`](src:docs/Spec.md#L3)).

The supported platforms are Ubuntu 24.04 / 22.04 (x64 native, and aarch64 / armhf / x86 cross builds), Tizen, Windows, and Android ([`README.md`](src:README.md#L8)). For Tizen, the engine is packaged as lightweight-web-engine with the summary "Lightweight Web Engine for Tizen" ([`lightweight-web-engine.spec`](src:packaging/lightweight-web-engine.spec#L19)), and RPMs can be generated per profile: tv, mobile, headless, wearable, or all ([`README.md`](src:README.md#L203)). The build produces three target forms: an executable (starfish.executable), a shared library (liblightweight-web-engine.so), and a static library (liblightweight-web-engine.a) ([`README.md`](src:README.md#L62)).

## System Scope

### Included

The following capabilities are identifiable from the module layout under src/core, the public headers under inc/, and build options, each verified by a concrete definition in the source tree:

- HTML/DOM tree and documents — src/core/dom, e.g. [`Document`](src:src/core/dom/Document.h#L102); browsing context and window objects under src/core/page, e.g. [`Window`](src:src/core/page/Window.h#L57).
- CSS style resolution — src/core/style, e.g. [`ComputedStyle`](src:src/core/style/ComputedStyle.h#L795).
- Layout — src/core/layout, e.g. [`Frame`](src:src/core/layout/Frame.h#L1203).
- 2D canvas rendering and compositing — src/core/modules/canvas, e.g. [`Canvas`](src:src/core/modules/canvas/Canvas.h#L296).
- WebGL — src/core/dom/canvas/webgl, e.g. [`WebGLRenderingContext`](src:src/core/dom/canvas/webgl/WebGLRenderingContext.h#L68), gated by the [`WEBGL`](src:CMakeLists.txt#L17) build option (default 0).
- Workers — src/core/modules/worker, src/core/modules/sharedworker ([`SharedWorker`](src:src/core/modules/sharedworker/SharedWorker.h#L33)), and src/core/modules/serviceworker ([`ServiceWorker`](src:src/core/modules/serviceworker/ServiceWorker.h#L31)), gated by [`WORKER`](src:CMakeLists.txt#L20), [`SHARED_WORKER`](src:CMakeLists.txt#L21), and [`SERVICE_WORKER`](src:CMakeLists.txt#L22) (defaults 0); a public worker API is exposed in inc/LWEWorker.h, e.g. [`ServiceWorker`](src:inc/LWEWorker.h#L52).
- IndexedDB — src/core/modules/indexeddb, e.g. [`IDBDatabase`](src:src/core/modules/indexeddb/IDBDatabase.h#L57), gated by [`IDB`](src:CMakeLists.txt#L23) (default 0).
- Media source playback — src/core/modules/mediasource, e.g. [`MediaSource`](src:src/core/modules/mediasource/MediaSource.h#L44); an [`ENABLE_ESPLUSPLAYER`](src:CMakeLists.txt#L19) option exists to "Use esplusplayer for MSE playback on Tizen".
- Web audio — src/core/modules/webaudio, e.g. [`AudioContext`](src:src/core/modules/webaudio/AudioContext.h#L37).
- Networking — fetch under src/core/fetch, e.g. [`Fetch`](src:src/core/fetch/Fetch.h#L39); sockets under src/core/modules/networking, e.g. [`WebSocket`](src:src/core/modules/networking/WebSocket.h#L33).
- Content Security Policy — src/core/csp, e.g. [`ContentSecurityPolicy`](src:src/core/csp/ContentSecurityPolicy.h#L56).
- Storage — src/core/storage, e.g. [`Storage`](src:src/core/storage/Storage.h#L34).
- File API — src/core/fileapi, e.g. [`Blob`](src:src/core/fileapi/Blob.h#L33).
- Animation — src/core/animation, e.g. [`Animation`](src:src/core/animation/Animation.h#L154).
- Device and platform modules — src/core/modules contains battery, cast, crypto ([`Crypto`](src:src/core/modules/crypto/Crypto.h#L28)), location ([`Geolocation`](src:src/core/modules/location/Geolocation.h#L36)), resize_observer ([`ResizeObserver`](src:src/core/modules/resize_observer/ResizeObserver.h#L44)), tts, profiling, renderer, message_loop, threading, resource_request, and related directories.
- WebRTC — present as the [`WEBRTC`](src:CMakeLists.txt#L18) build option (default 0) and the third_party/webrtc submodule ([`.gitmodules`](src:.gitmodules#L61)); no directory named webrtc exists under src.
- Developer tooling — a Chrome DevTools Protocol (CDP) server under src/core/cdp ([`CDPServer`](src:src/core/cdp/CDPServer.h#L38)); a remote inspector under src/core/inspector ([`Inspector`](src:src/core/inspector/Inspector.h#L29)); a JS debugger enabled by [`ENABLE_DEBUGGER`](src:CMakeLists.txt#L35); API recording/replay via [`APIRecorder`](src:src/public/APIRecorder.h#L34) and [api_record_replay.md](src:docs/api_record_replay.md).
- Accessibility — touch-exploration accessibility described as "tap=speak aria-label, double-tap=activate, swipe=next/prev" in [`build/config.cmake`](src:build/config.cmake#L53), with sources under src/core/page (A11yAtspiTreeSource, A11yTouchExploration).
- Additional core areas — src/core also contains event, csp, extra, serialize, util, and xml directories, and JS bindings live under src/binding, e.g. [`ScriptBindingInstance`](src:src/binding/ScriptBindingInstance.h#L68); bindings "for spec-defined interfaces are generated from [`src/**/*.idl`](src:README.md#L55) at cmake configure time" ([`README.md`](src:README.md#L55)).

### Excluded

Explicit exclusions stated in the repository:

- Windows "supports Intel x86 and x64 only. ARM/ARM64 is intentionally rejected" ([`README.md`](src:README.md#L208)).
- The Win32 shell "uses no .NET, WinForms, or MSBuild, and no Windows-specific bridge inside the engine" ([`README.md`](src:README.md#L257)).
- The default Linux x86_64 release build ships with WEBGL=0, WEBRTC=0, WORKER=0, SHARED_WORKER=0, SERVICE_WORKER=0, IDB=0 — these features are excluded from that default build configuration ([`Spec.md`](src:docs/Spec.md#L228)).

Other exclusions: Not specified in code.

## Users and Actors

| Actor | Type (human/system) | Role | Source |
|---|---|---|---|
| Embedder application | system | Creates and drives the engine through the public API: [`WebContainer`](src:inc/LWEWebView.h#L290) and [`WebView`](src:inc/LWEWebView.h#L536), after engine startup via [`Initialize`](src:inc/LWEWebView.h#L137). The README states the Windows shell, "like the other ports", "drives [`LWE::WebContainer`](src:inc/LWEWebView.h#L290) through the public [`WebContainer`](src:inc/LWEWebView.h#L290) API only" ([`README.md`](src:README.md#L259)). | [`WebContainer`](src:inc/LWEWebView.h#L290) |
| DevTools / CDP client | system | Browser-automation clients — "Puppeteer, Playwright, chrome-remote-interface, or any raw WebSocket client" — drive a headless Starfish WebView through the in-tree CDP server ([`CDP.md`](src:docs/CDP.md#L4)). | [`CDPServer`](src:src/core/cdp/CDPServer.h#L38) |
| Remote inspector client | system | Connects to the engine's inspector, which sends info/error/warn/debug messages over a socket ([`m_nnmSocket`](src:src/core/inspector/Inspector.h#L47)) and evaluates commands ([`commandEvaluator`](src:src/core/inspector/Inspector.h#L43)); a client named StarfishInspector lives under inspector/ ([`package.json`](src:inspector/package.json#L2)). | [`Inspector`](src:src/core/inspector/Inspector.h#L29) |
| Web content (HTML/CSS/JS) | system | Pages and scripts loaded by the engine execute against generated bindings; the binding layer is anchored by [`ScriptBindingInstance`](src:src/binding/ScriptBindingInstance.h#L68) and globals such as [`Window`](src:src/core/page/Window.h#L57); bindings are generated from [`src/**/*.idl`](src:README.md#L55) files ([`README.md`](src:README.md#L55)). | [`ScriptBindingInstance`](src:src/binding/ScriptBindingInstance.h#L68) |
| Developer / tester | human | Runs the shell executable on an HTML file ([`README.md`](src:README.md#L117)) hosted by [`MiniBrowser`](src:src/shell/MiniBrowser.h#L49), and runs the test suites via tool/runner/test_runner.py ([`README.md`](src:README.md#L310)). | [`MiniBrowser`](src:src/shell/MiniBrowser.h#L49) |

## System Context

An embedder links Starfish as an executable, shared library, or static library ([`README.md`](src:README.md#L62)) and interacts with it exclusively through the public headers in inc/ ([`WebContainer`](src:inc/LWEWebView.h#L290), [`WebView`](src:inc/LWEWebView.h#L536), and the worker API in inc/LWEWorker.h, e.g. [`ServiceWorker`](src:inc/LWEWorker.h#L52)). The engine can run on its own thread started by [`Initialize`](src:inc/LWEWebView.h#L137); for the Windows shell, "the engine runs on the LWE thread that [`LWE::LWE::Initialize`](src:inc/LWEWebView.h#L137) starts inside the DLL" and "the embedding API marshals every call there" ([`README.md`](src:README.md#L260)). Reference shells under src/shell (x11_webcontainer, glib, headless, efl, ecore, tcore_wl, libuv, windows, and others) host the engine through this same API; the executable target is selected via the [`SHELL`](src:CMakeLists.txt#L101) option with values x11 or glib_headless ([`README.md`](src:README.md#L101)). For the Updatable Web Engine (UWE) configuration, "UWE pairs an installed public API library with a separately delivered impl library", and "the delegate contract headers under src/public/contract/ therefore form a binary compatibility boundary" ([`uwe.md`](src:docs/uwe.md#L3)), with experimental flags [`ENABLE_DYNAMIC_LOADER`](src:CMakeLists.txt#L46) and [`ENABLE_MULTI_BACKEND`](src:CMakeLists.txt#L47).

Below the engine core (src/core, src/binding), platform integration is concentrated in src/platform (canvas, event, feedback, file, loader, message_loop, multimedia, network, process, tts, windows). The graphics backend is chosen at build time via [`BACKEND`](src:CMakeLists.txt#L13); per the README, the choice is between glib_cairo_gl and uv_cairo_gl, using "either cairo or cairo_gl as the backend graphics library" ([`README.md`](src:README.md#L88)). For the overall component relationships, see [architecture.mmd](./diagrams/architecture.mmd) and [System Architecture](./02-architecture.md).

## Technology Stack

| Layer | Technology | Version | License | Source |
|---|---|---|---|---|
| Web engine (this repository) | lightweight-web-engine ("Lightweight Web Engine for Tizen") | 1.5.2 ([`lightweight-web-engine.spec`](src:packaging/lightweight-web-engine.spec#L21)) | LGPL-2.1+ and BSD-2-Clause and BSD-3-Clause and BSL-1.0 and MIT and ISC and Zlib and BOEHM-GC and ICU | [`lightweight-web-engine.spec`](src:packaging/lightweight-web-engine.spec#L24) |
| JS engine | Escargot ("The JS engine is Escargot (third_party/escargot)") | Not specified in code | Not specified in code | [`AGENTS.md`](src:AGENTS.md#L4), [`.gitmodules`](src:.gitmodules#L9) |
| Backend graphics library | cairo / cairo_gl; on Windows the cairo vcpkg port with fontconfig and freetype features | Not specified in code | Not specified in code | [`README.md`](src:README.md#L88), [`vcpkg.json`](src:vcpkg.json#L14) |
| System packages (Ubuntu builds) | glib, cairo, freetype, fontconfig, harfbuzz, x11/xext/xrender/xi, egl/gles/gl, png/turbojpeg/jpeg/gif/webp, curl/openssl, icu, cap, asound, zlib | Not specified in code | Not specified in code | [`README.md`](src:README.md#L20) |
| Windows dependencies (vcpkg manifest) | curl (ssl, sspi), libwebsockets, cairo, harfbuzz, fontconfig, freetype, giflib, glew, libpng, pthreads | Registry baseline 06d00ffa491e4668627728f14b891d22c6fea146 ([`vcpkg-configuration.json`](src:vcpkg-configuration.json#L4)) | Not specified in code | [`vcpkg.json`](src:vcpkg.json#L5) |
| Engine idler/timer loop | third_party/libtuv ("supplies the engine idler/timer loop") | Not specified in code | Not specified in code | [`README.md`](src:README.md#L268), [`.gitmodules`](src:.gitmodules#L37) |
| Inspector socket transport | third_party/nanomsg and third_party/nanomsgcpp (used via [`m_nnmSocket`](src:src/core/inspector/Inspector.h#L47)) | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L49) |
| Third-party submodule | third_party/httplib (upstream cpp-httplib) | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L57) |
| Media container parsing | third_party/MP4Parse and third_party/webm ("MP4Parser and WebM are emitted as mp4parse.dll and webm.dll" on Windows) | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L13), [`README.md`](src:README.md#L263) |
| Third-party submodule | third_party/rapidxml | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L21) |
| Third-party submodules | third_party/clipper, third_party/skia_matrix, third_party/earcut.hpp | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L17) |
| Hash map/set ("fast hash map and hash set using robin hood hashing") | third_party/robin_map (vendored, not a submodule) | 1.2.1 ([`CMakeLists.txt`](src:third_party/robin_map/CMakeLists.txt#L3)) | MIT ([`LICENSE`](src:third_party/robin_map/LICENSE#L1)) | [`README.md`](src:third_party/robin_map/README.md#L3) |
| Image codec submodules | third_party/libjpeg-turbo, third_party/giflib, third_party/libpng, third_party/libwebp | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L70) |
| WebSocket library | third_party/libwebsockets (submodule and vcpkg overlay port) | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L64), [`USE_LIBWEBSOCKETS`](src:build/config.cmake#L116) |
| TLS submodule | third_party/openssl | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L67) |
| Tizen device API loader | third_party/deviceapi ("TIZEN device API Loader for escargot") | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L1), [`config.cmake`](src:build/config.cmake#L57) |
| JS binding generation | binding_generator submodule with python3-jinja2; bindings generated from [`src/**/*.idl`](src:README.md#L55) at cmake configure time | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L5), [`README.md`](src:README.md#L55) |
| WebRTC submodule | third_party/webrtc, gated by [`WEBRTC`](src:CMakeLists.txt#L18) | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L61) |
| Testing | third_party/googletest, third_party/wpt, test submodule (web_tc_new) | Not specified in code | Not specified in code | [`.gitmodules`](src:.gitmodules#L79) |
| Build toolchain | CMake (minimum 2.8.12, policy range up to 4.0), Ninja, vcpkg in manifest mode, tool/gyp submodule | Not specified in code | Not specified in code | [`CMakeLists.txt`](src:CMakeLists.txt#L10), [`README.md`](src:README.md#L215), [`.gitmodules`](src:.gitmodules#L33) |
| Windows threading | pthreads vcpkg port; "the official PThreads4W port is built from source... and deployed as pthreadVC3.dll" | Not specified in code | Not specified in code | [`vcpkg.json`](src:vcpkg.json#L25), [`README.md`](src:README.md#L271) |

## Document Overview

- [01 Introduction](./01-introduction.md) — this chapter: purpose, scope, actors, context, technology stack, and document map.
- [02 System Architecture](./02-architecture.md) — overall component structure and relationships of the engine.
- [03 Design Patterns](./03-design-patterns.md) — recurring implementation patterns observed in the codebase.
- [04 Data Layer](./04-data-layer.md) — data storage and persistence-related components.
- [05 External Interfaces](./05-external-interfaces.md) — public embedding API and externally reachable interfaces.
- [06 Configuration and Deployment](./06-configuration-deployment.md) — build options, packaging, and platform deployment.
- [07 Resources](./07-resources.md) — resource loading and management.
- [08 Security and Quality](./08-security-quality.md) — security-relevant mechanisms and quality/testing practices.
- [09 IPC and Enum Catalog](./09-ipc-enum-catalog.md) — catalog of IPC patterns, enums, and constants.
- [modules/](./modules/) — Module Design Cards, generated by W2.
- [functional-requirements/](./functional-requirements/) — functional requirement documents extracted per module.

## Reference Documents

| Document | Type | Source |
|---|---|---|
| Chrome DevTools Protocol (CDP) server support | Documentation | [`CDP.md`](src:docs/CDP.md#L1) |
| CDP domain coverage status | Documentation | [`CDP_DOMAINS.md`](src:docs/CDP_DOMAINS.md#L1) |
| C++ style convention | Style guide | [`Coding_Style_Guide.md`](src:docs/Coding_Style_Guide.md#L1) |
| Progressive Web App design (Service Worker) | Design document | [`PWA.md`](src:docs/PWA.md#L1) |
| Raspberry Pi 3 setup guide | Guide | [`RPi3_Guide.md`](src:docs/RPi3_Guide.md#L1) |
| Complete list of supported engine features | Specification | [`Spec.md`](src:docs/Spec.md#L1) |
| Public API call recording and replay | Documentation | [`api_record_replay.md`](src:docs/api_record_replay.md#L1) |
| Updatable Web Engine (UWE) contract | Documentation | [`uwe.md`](src:docs/uwe.md#L1) |
| Web Platform Tests (WPT) usage | Documentation | [`wpt.md`](src:docs/wpt.md#L1) |
| Starfish CDP MVP detailed design | Design document | [`CDP_DESIGN.md`](src:CDP_DESIGN.md#L1) |
| Engine constraints and documentation map | Documentation | [`AGENTS.md`](src:AGENTS.md#L1) |
| Build, run, and test instructions | Documentation | [`README.md`](src:README.md#L1) |
