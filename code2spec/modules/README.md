# Core Module Specifications

This folder contains the complete technical Module Design Cards representing the logical components of the Lightweight Web Engine.

| Module | Purpose | Rationale | Design Card Link |
|--------|---------|-----------|------------------|
| `compat-tizen` | Core subsystem for `compat-tizen` | Tizen 5.0 compatibility layer and headers | [compat-tizen.md](compat-tizen.md) |
| `docs-generator` | Core subsystem for `docs-generator` | Documentation generators and static web pages for API exploration | [docs-generator.md](docs-generator.md) |
| `inc-headers` | Core subsystem for `inc-headers` | Public Lightweight Web Engine API headers | [inc-headers.md](inc-headers.md) |
| `engine-core` | Core subsystem for `engine-core` | Starfish engine startup, central configuration, static strings, and entry points | [engine-core.md](engine-core.md) |
| `bindings` | Core subsystem for `bindings` | JavaScript custom bindings for Web APIs and DOM objects | [bindings.md](bindings.md) |
| `browser` | Core subsystem for `browser` | Browser management components, history manager, and frame tree | [browser.md](browser.md) |
| `launcher` | Core subsystem for `launcher` | Service worker and shared worker entry points | [launcher.md](launcher.md) |
| `platform-canvas` | Core subsystem for `platform-canvas` | Canvas rendering backend using GL, Cairo, and Mock renderers | [platform-canvas.md](platform-canvas.md) |
| `platform-core` | Core subsystem for `platform-core` | Operating system process management, thread loops, key events, and feedback | [platform-core.md](platform-core.md) |
| `platform-file` | Core subsystem for `platform-file` | File and directory system abstractions | [platform-file.md](platform-file.md) |
| `platform-loader` | Core subsystem for `platform-loader` | Resource loaders, element clients, and network cache interfaces | [platform-loader.md](platform-loader.md) |
| `platform-multimedia` | Core subsystem for `platform-multimedia` | Media player and demuxer core for audio/video playback | [platform-multimedia.md](platform-multimedia.md) |
| `platform-network` | Core subsystem for `platform-network` | Network abstraction layer, cURL multi managers, and HTTP caching | [platform-network.md](platform-network.md) |
| `public-bridge` | Core subsystem for `public-bridge` | Public interface delegates and native window-manager bridge wrappers for EFL, Android JNI, and Flutter | [public-bridge.md](public-bridge.md) |
| `shell` | Core subsystem for `shell` | MiniBrowser main interface, API replayer, window hooks, and unit tests | [shell.md](shell.md) |
| `third-party` | Core subsystem for `third-party` | Third-party libraries (e.g. robin_map) integrated into the project | [third-party.md](third-party.md) |
| `tooling` | Core subsystem for `tooling` | CI checks, WPT test runner, lint tools, and local testing servers | [tooling.md](tooling.md) |
