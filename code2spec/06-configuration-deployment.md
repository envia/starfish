**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 6: Configuration & Deployment

> **Relevant source files:**
> - [`StarfishConfig.h`](src:src/StarfishConfig.h#L1)
> - [`MiniBrowser.cpp`](src:src/shell/MiniBrowser.cpp#L1)
> - [`CMakeLists.txt`](src:CMakeLists.txt#L1)

---

## Build Configurations
Starfish uses a flexible CMake system supporting cross-compilation configurations for Android, Windows, and Tizen containers [`CMakeLists.txt`](src:CMakeLists.txt#L1).

## Command Line Startup Flags
Engine features can be adjusted dynamically during initialization using command line flags defined inside `StarfishStartUpFlag` [`MiniBrowser.cpp`](src:src/shell/MiniBrowser.cpp#L34):
- `enableComputedStyleDump`: Dumps computed styles during debug runs.
- `enableFrameTreeDump`: Outputs internal tree structure.
- `enableRegressionTest`: Launches specialized test layout profiles.
