**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 7: Resources

> **Relevant source files:**
> - [`AppLoopLibuv.cpp`](src:src/shell/libuv/AppLoopLibuv.cpp#L1)
> - [`Process.cpp`](src:src/platform/process/base/Process.cpp#L1)
> - [`StarfishBase.h`](src:src/StarfishBase.h#L1)

---

## Threading Model
Starfish operates on a dedicated multi-threaded architecture:
1. **Main Thread (UI/Render):** Handles DOM building and painting events, powered by platform-specific loops (e.g. Libuv [`AppLoopLibuv.cpp`](src:src/shell/libuv/AppLoopLibuv.cpp#L39) or GLib).
2. **Worker Threads:** Web workers spawned in background contexts [`LWEWorker.h`](src:inc/LWEWorker.h#L44).
3. **IO/Network Thread:** cURL resource transaction thread pools.

## Process Abstraction
Processes are spawned and managed cleanly through the abstract `Process` helper, allowing for cross-platform process isolation when running web services [`Process.cpp`](src:src/platform/process/base/Process.cpp#L193).
