# 05 — External Interfaces

> **Relevant source files**
> - [`inc/LWEWebView.h`](inc:LWEWebView.h)
> - [`inc/LWEWorker.h`](inc/LWEWorker.h)
> - [`inc/PlatformIntegrationData.h`](inc/PlatformIntegrationData.h)
> - [`src/public/bridge/android/AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp)
> - [`src/public/bridge/efl/LWEWebViewEFL.cpp`](src:src/public/bridge/efl/LWEWebViewEFL.cpp)

## Public Embedding API

### LWEWebView

The primary embedding interface. Defined in [`inc/LWEWebView.h`](inc:LWEWebView.h). Exported via `LWE_EXPORT` macro (dllexport/dllimport on Windows, visibility("default") on Linux).

Key API methods (from entry points detected in AST):
- `Create` / `CreateGL` / `CreateHeadless` / `CreateWebContainer` — factory methods
- `RegisterPreRenderingHandler` / `RegisterOnRenderedHandler` — rendering callbacks
- `RegisterDebuggerShouldInitHandler` / `RegisterDebuggerShouldContinueWaitingHandler` — debugger callbacks

### LWEWorker

Web worker control interface. Defined in [`inc/LWEWorker.h`](inc:LWEWorker.h). Key method: `RegisterOnStatusChangedHandler`.

### PlatformIntegrationData

Defined in [`inc/PlatformIntegrationData.h`](inc/PlatformIntegrationData.h). Carries platform-specific integration data across the embedding boundary.

## Platform Bridges

### Android Bridge

[`src/public/bridge/android/AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp) — JNI bridge for Android. Java classes in `src/public/bridge/android/java/`:
- `LweWebView` / `LweWebViewImpl` — Android WebView implementation
- `WebViewClient` / `WebChromeClient` — standard Android WebView callbacks
- `WebSettings` — configuration
- `DownloadListener` — download handling

### EFL Bridge

[`src/public/bridge/efl/LWEWebViewEFL.cpp`](src:src/public/bridge/efl/LWEWebViewEFL.cpp) — EFL (Enlightenment Foundation Libraries) window integration. Includes `A11yAtspiBridge` for accessibility.

### Other Bridges

- **Ecore WL2**: [`src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp)
- **Ecore X**: [`src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp`](src:src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp)
- **Flutter**: [`src/public/bridge/flutter/LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp)
- **Tcore WL**: [`src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp`](src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp)
- **X11**: [`src/public/bridge/x11/LWEWebViewX11.cpp`](src/public/bridge/x11/LWEWebViewX11.cpp)

## Contract Interfaces

Pure-virtual interfaces in `src/public/contract/`:
- `LWEWebViewDelegate` — web view delegate
- `LWEWebContainerDelegate` — web container delegate
- `LWEWorkerDelegate` — worker delegate
- `LWEDelegate` — base delegate
- `CookieManagerDelegate` — cookie management
- `SettingsDelegate` — settings management
- `ResourceErrorDelegate` — resource error handling

## External Libraries (SOUP)

| Library | Purpose | Source |
|---|---|---|
| Escargot | JavaScript engine | `third_party/escargot` |
| libcurl | HTTP networking | System dependency |
| Cairo | 2D graphics | System dependency |
| OpenGL/EGL | GPU rendering | System dependency |
| HarfBuzz | Text shaping | System dependency |
| ICU | Internationalization | System dependency |
| libpng | PNG decoding | System dependency |
| BDWGC | Garbage collection | System dependency |
| robin_map | Hash map | `third_party/robin_map/` |
| nanomsg | Messaging (optional) | `third_party/nanomsg/` |
| libtuv | libUV for Tizen (optional) | `third_party/libtuv/` |
