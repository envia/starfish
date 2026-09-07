# Quick Reference (code2spec)

> 코드 수정 전 반드시 확인. 아키텍처 일관성 유지 필수.

## 시스템 개요

- **아키텍처 패턴**: Layered architecture — Core Engine, Platform Abstraction, Public Embedding API, Shell
- **레이어 구조**: `src/core` (engine) → `src/platform` (canvas/network/loader/multimedia) → `src/public` (API/contract/delegate/bridge) → `src/shell` (browser app)
- **기술 스택**: C++ (LGPL v2.1), Escargot JS engine, BDWGC, Cairo/OpenGL ES, libcurl, HarfBuzz/ICU, CMake+Ninja

### 주요 설계 결정

1. **Contract-Delegate Pattern**: Pure-virtual interfaces (`src/public/contract/`) cross the `.so` boundary; concrete implementations in `src/public/delegate/`. ABI checked by `check_contract_abi.py`.
2. **GC-Managed Object Graph**: All engine objects inherit `gc` (BDWGC). Containers use `GCVector`/`GCTightVector` — never `std::vector` for GC-managed pointers.
3. **Default-Off Feature Gating**: Heavy/optional features (WebGL, WebRTC, Worker, IDB, WASM) are compile-time gated and default off.
4. **IDL-Generated Bindings**: `.idl` files mirror web specs; editing any `.idl` requires re-running cmake.
5. **Low Memory Core Constraint**: Pre-allocated `StaticStrings`, configurable GC frequency, lean per-instance footprint.

## 핵심 모듈 위치

| 모듈 | 주요 파일 | 역할 |
|---|---|---|
| core-engine | `src/Starfish.h`, `src/Starfish.cpp` | Engine root, configuration, GC init |
| binding | `src/binding/ScriptEngineInstance.h` | Escargot JS engine integration, DOM bindings |
| shell | `src/shell/Shell.cpp`, `src/shell/MiniBrowser.cpp` | Browser app entry point, window management |
| public-api | `src/public/LWEWebView.cpp` | Embedding API (LWEWebView, LWEWorker) |
| public-contract | `src/public/contract/LWEWebViewDelegate.h` | Pure-virtual .so boundary interfaces |
| public-delegate | `src/public/delegate/LWEWebViewDelegateImpl.cpp` | Concrete delegate implementations |
| public-bridge | `src/public/bridge/efl/LWEWebViewEFL.cpp` | Platform window system bridges |
| platform-canvas | `src/platform/canvas/CanvasCairo.cpp` | 2D rendering (Cairo/GL/Mock) |
| platform-network | `src/platform/network/http/HTTPRequest.h` | HTTP client (libcurl), caching |
| platform-loader | `src/platform/loader/Resource.h` | Resource fetch lifecycle |
| platform-multimedia | `src/platform/multimedia/MediaPlayer.h` | Media playback (9 codecs) |
| platform-message-loop | `src/platform/message_loop/MessageLoopGLib.cpp` | Event loop (GLib/libUV) |
| platform-misc | `src/platform/file/PlatformFile.h` | File I/O, key events, screen orientation |
| browser-history | `src/browser/history/HistoryManager.h` | Navigation history (max 256 entries) |
| launcher | `src/launcher/ServiceWorkerEntry.cpp` | Service/Shared worker process entry |
| compat-headers | `inc/LWEWebView.h` | Public headers for embedders |
| third-party | `third_party/robin_map/include/tsl/robin_map.h` | Header-only hash map (MIT) |
| tooling | `tool/runner/test_runner.py` | Test framework, WPT runner, lint checks |

## 아키텍처 원칙

1. **Spec is truth**: WHATWG/W3C/ECMA-262 spec is the source of truth, not another engine's quirks.
2. **Optional<T> for nullability**: Use `Optional<T>` (`src/StarfishBase.h`), not raw pointer + `nullptr`.
3. **Plain pointer = valid**: A plain pointer parameter or member is expected valid (GC-based object graph). Don't add defensive null checks.
4. **GCVector for GC pointers**: Containers of GC-managed pointers use `GCVector`/`GCTightVector`, even for short-lived locals.
5. **Fix root causes**: Don't paper over symptoms with defensive null checks or try-catch that swallows failures.
6. **Default-off gating**: Heavy features are compile-time gated (`CMakeLists.txt` flags: WEBGL, WEBRTC, WORKER, IDB, ENABLE_WASM, ...).
7. **`.idl` changes require cmake re-run**: Incremental `ninja` never regenerates bindings.

## 기능 수정 시 참조

| 기능 | 파일 | 라인 |
|---|---|---|
| Engine init | `src/Starfish.h` | L49 (StarfishConfiguration), L58 (Starfish class) |
| GC config | `src/Starfish.h` | L40 (BDWGC_FREE_SPACE_DIVISOR) |
| Renderer type | `src/Starfish.h` | L43 (kOpenGL/kSoftware/kHeadless) |
| HTTP cache gate | `src/Starfish.h` | L35 (STARFISH_ENABLE_HTTPCACHE) |
| WebView API | `src/public/contract/LWEWebViewDelegate.h` | L35 (WebView class), L37 (Create) |
| JS engine | `src/binding/ScriptEngineInstance.h` | L33 (ScriptEngineInstance) |
| Same-origin security | `src/binding/WindowProxy.h` | L1 (WindowProxy) |
| Media playback states | `src/platform/multimedia/MediaPlayer.h` | L67 (PlaybackState) |
| Canvas Cairo backend | `src/platform/canvas/CanvasCairo.cpp` | L23 (PORT_CANVAS_BACKEND_CAIRO) |
| EFL bridge | `src/public/bridge/efl/LWEWebViewEFL.cpp` | L34 (TBM presenter), L153 (owner states) |
| History max entries | `src/browser/history/HistoryManager.h` | L39 (MAX_ENTRY_SIZE=256) |
| Key event types | `inc/PlatformIntegrationData.h` | L7 (KeyValue enum, 229 values) |
| Font size limits | `compat/tizen_5.0/inc/LWEWebView.h` | L180 (default=16, min=1, max=72) |
| Test runner | `tool/runner/test_runner.py` | L55 (res list execution) |
| Tidy check | `tool/lint/check_tidy.py` | L33 (clang-format check) |

## 코드 수정 전 확인 순서

1. 본 Quick Reference에서 관련 모듈 찾기
2. Module Design Card (`modules/<name>.md`) 읽기
3. `02-architecture.md` → 레이어 규칙 준수 확인
4. `03-design-patterns.md` → 설계 패턴 위반 여부 확인
5. `04-data-layer.md` → 스키마 변경 시 마이그레이션 필요 여부
6. `05-external-interfaces.md` → 외부 API 변경 시 에러 처리 확인
7. `08-security-quality.md` → 보안 경계(same-origin, CORS, CSP) 영향 확인
8. `.idl` 변경 시 cmake 재실행 필요
9. `docs/Spec.md` → 웹 서피스 변경 시 동일 커밋에서 업데이트

## Core 모듈 역할 한줄 요약

| 모듈 | 역할 |
|---|---|
| core-engine | 엔진 루트, GC/설정/정적 문자열 |
| binding | Escargot JS 엔진 통합, DOM 바인딩, same-origin 보안 |
| shell | 브라우저 앱 진입점, 창 관리, 유닛 테스트 |
| public-api | 임베더 API (LWEWebView/LWEWorker) |
| public-contract | .so 경계 순수 가상 인터페이스 |
| public-delegate | delegate 구현체 |
| public-bridge | 플랫폼별 윈도우 시스템 브릿지 |
| platform-canvas | 2D 렌더링 (Cairo/GL/Mock) |
| platform-network | HTTP 클라이언트 (libcurl), 캐싱 |
| platform-loader | 리소스 fetch 라이프사이클 |
| platform-multimedia | 미디어 재생 (9 코덱) |
| platform-message-loop | 이벤트 루프 (GLib/libUV) |
| platform-misc | 파일 I/O, 키 이벤트, 화면 방향 |
| browser-history | 네비게이션 히스토리 (최대 256) |
| launcher | 서비스/공유 워커 프로세스 진입점 |
| compat-headers | 임베더용 공개 헤더 |
| third-party | tsl::robin_map 헤더 온리 해시맵 |
| tooling | 테스트 프레임워크, WPT 러너, 린트 |

## Interface / Message Contract Review

- System-wide message contracts: `.analysis/message-contract-candidates.md`
- Module-local contract details: `modules/<name>.md` → `IPC / Message / Interface Contracts`