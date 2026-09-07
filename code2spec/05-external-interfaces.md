**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 5: External Interfaces

> **Relevant source files:**
> - [`LWEWebView.h`](src:inc/LWEWebView.h#L1)
> - [`AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp#L1)
> - [`LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L1)

---

## Public Platform APIs
Starfish exposes its core control capabilities through **LWEWebView**, allowing client software to instantiate WebViews, manage viewport size, and handle lifecycle delegates [`LWEWebView.h`](src:inc/LWEWebView.h#L58).

## Native App Containers
1. **Android Bridge:** JNI interface binding the Java class `LweWebViewImpl` directly to native Starfish functions [`AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp#L443).
2. **Flutter Embedding:** Instantiates custom EGL contexts and binds canvas frames directly to Flutter textures [`LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L466).
3. **EFL Embedding:** Coordinates rendering passes inside EFL application containers via Wayland protocols [`LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L456).
