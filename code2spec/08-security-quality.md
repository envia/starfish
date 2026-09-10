# Security and Quality

> **Relevant source files**
>
> - [src/core/csp/ContentSecurityPolicy.h](src:src/core/csp/ContentSecurityPolicy.h)
> - [src/core/csp/ContentSecurityPolicyDirectiveList.h](src:src/core/csp/ContentSecurityPolicyDirectiveList.h)
> - [src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp](src:src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp)
> - [src/platform/network/http/HTTPTransaction.cpp](src:src/platform/network/http/HTTPTransaction.cpp)
> - [src/platform/network/http/HTTPCache.h](src:src/platform/network/http/HTTPCache.h)
> - [src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp)
> - [src/StarfishBase.h](src:src/StarfishBase.h)
> - [inc/PlatformIntegrationData.h](src:inc/PlatformIntegrationData.h)
> - [build/config.cmake](src:build/config.cmake)
> - [tool/lint/check_tidy.py](src:tool/lint/check_tidy.py)
> - [docs/wpt.md](src:docs/wpt.md)
> - [src/core/modules/profiling/Profiling.h](src:src/core/modules/profiling/Profiling.h)

This chapter documents the security mechanisms, error handling conventions, test strategy, code quality tooling, logging/monitoring facilities, and performance-related mechanisms of the Starfish web browser engine, based solely on the repository contents.

## Security Architecture

| Mechanism | Implementation in code | Source |
|---|---|---|
| Content Security Policy (CSP) | [`ContentSecurityPolicy`](src:src/core/csp/ContentSecurityPolicy.h#L56) parses policies received via [`didReceiveHeader`](src:src/core/csp/ContentSecurityPolicy.h#L60) and enforces them through `allow*` checks | [src/core/csp/](src:src/core/csp/ContentSecurityPolicy.h) |
| Web security on/off switch | [`WebSecurityMode`](src:inc/PlatformIntegrationData.h#L258) enum (`Enable = 0, Disable = 1`) exposed per WebView via [`GetWebSecurityMode`](src:inc/LWEWebView.h#L231) / [`SetWebSecurityMode`](src:inc/LWEWebView.h#L256) | [inc/PlatformIntegrationData.h](src:inc/PlatformIntegrationData.h) |
| CORS checks | [`checkCors`](src:src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp#L978) (annotated with the WHATWG fetch "CORS check" URL) plus CORS preflight method/header validation; both are skipped when `WebSecurityMode::Disable` | [src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp](src:src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp) |
| TLS via libcurl | `CURLOPT_SSL_VERIFYPEER` / `CURLOPT_SSL_VERIFYHOST` are enabled unless an explicit ignore flag is set; Android sets `CURLOPT_CAINFO` from the `STARFISH_CURL_CA_BUNDLE` environment variable | [src/platform/network/http/HTTPTransaction.cpp](src:src/platform/network/http/HTTPTransaction.cpp) |
| Service worker process isolation | [`getConnection`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L188) keeps a per-origin process map and launches a separate `./Starfish-serviceworker` process | [src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp) |
| Linux capabilities (libcap) | Probed and linked at build time only; no `cap_*` API call sites found under `src/` | [build/config.cmake](src:build/config.cmake) |

### Content Security Policy

CSP lives in `src/core/csp/` (`ContentSecurityPolicy.{h,cpp}`, `ContentSecurityPolicyDirectiveList.{h,cpp}`, `ContentSecurityPolicySourceListDirective.{h,cpp}`, `SecurityPolicyViolationEvent.{h,idl}`). The [`ContentSecurityPolicy`](src:src/core/csp/ContentSecurityPolicy.h#L56) class receives policies through [`didReceiveHeader`](src:src/core/csp/ContentSecurityPolicy.h#L60), distinguishing [`ContentSecurityPolicyHeaderType`](src:src/core/csp/ContentSecurityPolicy.h#L27) (`Report`, `Enforce`) and [`ContentSecurityPolicyHeaderSource`](src:src/core/csp/ContentSecurityPolicy.h#L29) (`HTTP`, `Meta`, `OriginPolicy`, `Inherited`). Supported directives are enumerated in [`CSPDirectives`](src:src/core/csp/ContentSecurityPolicy.h#L36): `BaseURI`, `ConnectSrc`, `ChildSrc`, `DefaultSrc`, `FormAction`, `FrameAncestors`, `ImgSrc`, `MediaSrc`, `ObjectSrc`, `ScriptSrc`, `StyleSrc`.

Enforcement entry points on the class are [`allowInlineEventHandler`](src:src/core/csp/ContentSecurityPolicy.h#L63), [`allowSource`](src:src/core/csp/ContentSecurityPolicy.h#L64), [`allowInline`](src:src/core/csp/ContentSecurityPolicy.h#L67), [`allowEval`](src:src/core/csp/ContentSecurityPolicy.h#L69), [`allowNonceOrSource`](src:src/core/csp/ContentSecurityPolicy.h#L70), and [`allowAncestors`](src:src/core/csp/ContentSecurityPolicy.h#L74) (frame-ancestors has no default-src fallback, per the in-code comment). Violations are reported via [`dispatchViolationEvent`](src:src/core/csp/ContentSecurityPolicy.h#L76). Each policy string is parsed into a [`ContentSecurityPolicyDirectiveList`](src:src/core/csp/ContentSecurityPolicyDirectiveList.h#L28) through its [`parse`](src:src/core/csp/ContentSecurityPolicyDirectiveList.h#L38) method, with per-list checks such as [`allowSource`](src:src/core/csp/ContentSecurityPolicyDirectiveList.h#L42) and [`allowEval`](src:src/core/csp/ContentSecurityPolicyDirectiveList.h#L47). [`isFrameAncestorsEnforceable`](src:src/core/csp/ContentSecurityPolicyDirectiveList.h#L77) restricts frame-ancestors enforcement to policies delivered with the HTTP response (inherited and `<meta>` policies must not block, per the in-code comment). A process-wide enforcement bypass for CDP `Page.setBypassCSP` exists via [`setBypass`](src:src/core/csp/ContentSecurityPolicy.h#L91); policies are still parsed and stored but all `allow*` checks short-circuit to true.

### Web Security Mode and CORS

[`WebSecurityMode`](src:inc/PlatformIntegrationData.h#L258) is a two-state public-API enum. In the network resource request delegate, [`checkCors`](src:src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp#L978) immediately returns `true` (skipping the CORS check) when the mode is `Disable`, and CORS preflight validation of `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` is performed only when the mode is [`Enable`](src:src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp#L918). Request semantics follow the fetch specification data model: [`RequestMode`](src:src/core/fetch/RequestData.h#L47) (`SameOrigin`, `CORS`, `NoCORS`, `Navigate`, `Websocket`), [`RequestCredentials`](src:src/core/fetch/RequestData.h#L55) (`Omit`, `SameOrigin`, `Include`), and [`isCORSsafelistedResponseHeaderName`](src:src/core/fetch/FetchUtils.h#L41). Referrer handling defines a [`ReferrerPolicy`](src:src/platform/loader/ResourceURL.h#L282) enum including `NoReferrerWhenDowngrade`, `OriginWhenCrossOrigin`, and `StrictOriginWhenCrossOrigin`.

Mixed content: no mixed-content blocking logic was found in `src/core/fetch` or `src/platform/loader`. The only occurrence is the Android bridge method [`setMixedContentMode`](src:src/public/bridge/android/java/com/samsung/android/lightweightwebengine/WebSettings.java#L127), which has an empty body. Mixed-content policy is otherwise Not specified in code.

### TLS Configuration

HTTP transfers use libcurl. Certificate verification is controlled by `m_ignoreSSLVerify`, which is initialized to `true` only when built with [`STARFISH_IGNORE_SSL_VERIFYPEER` or `STARFISH_ENABLE_TEST`](src:src/platform/network/http/HTTPTransaction.cpp#L69) and can also be turned on by the [`IGNORE_SSL_VERIFY`](src:src/platform/network/http/HTTPTransaction.cpp#L75) environment variable or at runtime by CDP `Security.setIgnoreCertificateErrors` through [`setGlobalIgnoreSSLVerify`](src:src/platform/network/http/HTTPTransaction.h#L43). When set, [`CURLOPT_SSL_VERIFYPEER` and `CURLOPT_SSL_VERIFYHOST` are disabled](src:src/platform/network/http/HTTPTransaction.cpp#L116). On Android the CA bundle is supplied explicitly via [`CURLOPT_CAINFO`](src:src/platform/network/http/HTTPTransaction.cpp#L121) from `STARFISH_CURL_CA_BUNDLE` (asserted to exist). The build system documents [`STARFISH_IGNORE_SSL_VERIFYPEER`](src:build/config.cmake#L59) as "ignore SSL connection verification only for Android", and the Windows build [defines it](src:build/windows.cmake#L80).

### Service Worker Process Isolation

[`ServiceWorkerProcessManager::getConnection`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L188) maintains an [origin-to-process map](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L208). When `STARFISH_USE_WORKER_PROCESS` is defined, a service worker runs in a separate OS process: either a platform-supplied [`serviceWorkerProcessExecutor`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L216) is invoked, or the executable [`./Starfish-serviceworker`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L229) is spawned via [`ProcessUtil::launchProcess`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L234). Without that define, the worker is started on a thread instead ([`startWorkerOnThread`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L214)). The client communicates with the worker process over an IPC socket ([`connect`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L259) to an address derived from the connection name).

### Sandboxing and Capabilities

The build probes for libcap with [`CHECK_LIBRARY_EXISTS(cap cap_set_flag ...)`](src:build/config.cmake#L718) and appends `cap` to the default link libraries when found; `libcap-dev` appears in the [required package list](src:README.md#L28). However, no `cap_get_proc`/`cap_set_flag`/`sys/capability.h` call sites were found anywhere under `src/`, so capability dropping/usage by engine code is Not specified in code. No seccomp usage was found. Any further OS-level sandboxing is Not specified in code.

## User Authentication and Authorization

Engine-level authentication support is limited to protocol plumbing: the HTTP header table defines [`kAuthorization`](src:src/platform/network/http/HTTPHeaderMap.h#L50) and [`kProxyAuthorization`](src:src/platform/network/http/HTTPHeaderMap.h#L68) header names (string-to-enum mapping in [`HTTPUtil.cpp`](src:src/platform/network/http/HTTPUtil.cpp#L131)), and the status code table defines [`UNAUTHORIZED`](src:src/platform/network/http/HTTPStatus.h#L56). No `CURLOPT_USERPWD` usage, credential store, `WWW-Authenticate` challenge handling, or authentication prompt logic was found in `src/platform/network` or `src/core/fetch`. Beyond these header/status definitions, user authentication and authorization are Not specified in code.

## Error Handling Strategy

Error handling is based on assertion macros defined in [src/StarfishBase.h](src:src/StarfishBase.h):

- [`STARFISH_ASSERT`](src:src/StarfishBase.h#L479) — compiled out to `((void)0)` when `NDEBUG` is defined; otherwise expands to [`assert(assertion)`](src:src/StarfishBase.h#L483). [`STARFISH_ASSERT_NOT_REACHED`](src:src/StarfishBase.h#L484) is `assert(false)` in debug builds and a no-op in release builds.
- [`STARFISH_RELEASE_ASSERT`](src:src/StarfishBase.h#L499) — active in all build types: on failure it logs `"RELEASE_ASSERT"` via `STARFISH_LOG_ERROR` and calls `::abort()`.
- [`STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE`](src:src/StarfishBase.h#L506) — unconditionally logs `"RELEASE_ASSERT_NOT_REACHED"` and calls `::abort()`; [`STARFISH_CRASH`](src:src/StarfishBase.h#L476) is an alias for it.
- [`STARFISH_COMPILE_ASSERT`](src:src/StarfishBase.h#L496) — `static_assert` wrapper.
- [`RETURN_FALSE_IF_FAILED`](src:src/StarfishBase.h#L512) — logs a warning and returns `false` from the enclosing function when a condition fails (early-return error propagation).

C++ exception policy: the Android build explicitly passes [`-fexceptions`](src:build/android.cmake#L242) together with [`-fno-rtti`](src:build/android.cmake#L241). No `-fno-exceptions` flag was found in `CMakeLists.txt` or `build/*.cmake`, so exceptions are not globally disabled; a project-wide exception-usage policy is otherwise Not specified in code. An AddressSanitizer build is available behind the [`ASAN` option](src:build/config.cmake#L475) (`-fsanitize=address`).

## Test Strategy

| Item | Content | Source |
|---|---|---|
| Internal TC suite (submodule) | `test/` is a git submodule pointing to `lws-test/web_tc_new` (ignore = dirty) | [.gitmodules](src:.gitmodules#L45) |
| Test driver | [`run_test.py`](src:tool/drivers/run_test.py) runs suites in parallel, e.g. [`run_dom_conformance_test`](src:tool/drivers/run_test.py#L19) ("W3C DOM Conformace Test Suites") and [`run_vendor_basic_test`](src:tool/drivers/run_test.py#L26), summarizing pass/fail counts | [tool/drivers/run_test.py](src:tool/drivers/run_test.py) |
| Web Platform Tests (WPT) | Curated WPT subset run against an on-demand `wpt serve`; corpus pinned as the `third_party/wpt` submodule ([.gitmodules](src:.gitmodules#L85)); covers testharness.js, reftest (`imgdiff`-based pixel comparison), and crashtest types; scripts in `tool/wpt/scripts/` (`wpt_status.py`, `wpt_runner.py`, `wpt_reftest.py`, `wpt_server.py`, ...) | [docs/wpt.md](src:docs/wpt.md) |
| WPT in CI | Nightly job runs [`wpt_status_nightly.yml`](src:.github/workflows/wpt_status_nightly.yml#L126); per-build jobs `test_wpt_serve_testharness_and_crashtest` ([x64_test.yml](src:.github/workflows/x64_test.yml#L290)) and `test_wpt_serve_reftest` ([x64_test.yml](src:.github/workflows/x64_test.yml#L346)) | [.github/workflows/wpt_status_nightly.yml](src:.github/workflows/wpt_status_nightly.yml) |
| Reftest suite | [`reftest.sh`](src:tool/reftest/reftest.sh) regression runner producing `result.csv` with pass/fail/skip counters; CI job `test_reftest_all` ([x64_test.yml](src:.github/workflows/x64_test.yml#L198)) | [tool/reftest/](src:tool/reftest/reftest.sh) |
| Pixel test (golden images) | [`pixel_test.sh`](src:tool/pixel_test/pixel_test.sh) compares screenshots against stored expected images (`EXPECTED_IMAGE_PATH`); expectation lists in `.res` files (css1, css21, selector, svg, ...) | [tool/pixel_test/](src:tool/pixel_test/pixel_test.sh) |
| Unit tests (test shell) | `src/shell/test/` contains six googletest files (`APIRecorderTest`, `CookieManagerTest`, `LWETest`, `SettingsTest`, `WebContainerTest`, `WebViewTest`) exercising the public `LWEWebView.h` API, e.g. fixture [`LWETestInitialize`](src:src/shell/test/LWETest.cpp#L27); the shell dispatches [`"unit-test"`](src:src/shell/Shell.cpp#L82) to [`Shell::runUnitTest`](src:src/shell/Shell.cpp#L97); CI runs `./Starfish unit-test` in job `test_unit_test` ([x64_test.yml](src:.github/workflows/x64_test.yml#L95), command at [L137](src:.github/workflows/x64_test.yml#L137)) | [src/shell/test/](src:src/shell/test/LWETest.cpp) |
| Internal test CI job | `test_internal_test` job exists in the x64 test workflow | [x64_test.yml](src:.github/workflows/x64_test.yml#L139) |

## Code Quality Tools

| Tool | Purpose | Config file | Source |
|---|---|---|---|
| clang-format | Formatting style generated from `clang-format-3.8 -style=google -dump-config`, "then modified according to MWE style guide" (per file header comment) | [.clang-format](src:.clang-format) | [.clang-format](src:.clang-format) |
| check_tidy.py | Repository lint gate that runs clang-format over sources with extensions [`.cpp/.h/.hpp`](src:tool/lint/check_tidy.py#L33) via [`check_tidy`](src:tool/lint/check_tidy.py#L63) and diffs the result; executed in PR CI ([pr_ci.yml](src:.github/workflows/pr_ci.yml#L47)). Note: no `.clang-tidy` file exists in the repository; despite its name the script drives clang-format | [.clang-format](src:.clang-format) | [tool/lint/check_tidy.py](src:tool/lint/check_tidy.py) |
| check_contract_abi.py | Gates ABI breaks in the UWE delegate contract headers (`src/public/contract/*.h`) — vtable slot order, `extern "C"` wrapper signatures, enum/struct layout across the API/impl `.so` boundary (module docstring); executed in PR CI ([pr_ci.yml](src:.github/workflows/pr_ci.yml#L92)) | [tool/lint/contract_abi](src:tool/lint/check_contract_abi.py) | [tool/lint/check_contract_abi.py](src:tool/lint/check_contract_abi.py) |
| Coverage (gcov) | `-DCOVERAGE=1` adds [`-fprofile-arcs -ftest-coverage` and links `gcov`](src:build/config.cmake#L482); documented as "Enable coverage measurements with gcov" ([README.md](src:README.md#L99)); `tool/coverage/` scripts (`genCoverage.sh`, `combineCsv.sh`) generate tab-separated dom/html/css TC-coverage reports from recorded `*.raw` logs (per its README) | [build/config.cmake](src:build/config.cmake) | [tool/coverage/README](src:tool/coverage/README) |
| AddressSanitizer | `-DASAN=1` adds [`-fsanitize=address`](src:build/config.cmake#L475) and links `asan` | [build/config.cmake](src:build/config.cmake) | [build/config.cmake](src:build/config.cmake) |

## Logging and Monitoring

Logging is macro-based with a per-platform backend, all defined in [src/StarfishBase.h](src:src/StarfishBase.h). Every message is prefixed with module file name, function, and line via [`LOG_FUNCTION_TYPE`](src:src/StarfishBase.h#L376):

- Tizen (non-test builds): `dlog_print` — [`STARFISH_LOG_INFO`](src:src/StarfishBase.h#L397), [`STARFISH_LOG_ERROR`](src:src/StarfishBase.h#L416), [`STARFISH_LOG_WARN`](src:src/StarfishBase.h#L438), [`STARFISH_LOG_DEBUG`](src:src/StarfishBase.h#L458).
- Android: `__android_log_print` — [`STARFISH_LOG_INFO`](src:src/StarfishBase.h#L401), [`STARFISH_LOG_ERROR`](src:src/StarfishBase.h#L421).
- Windows: forwarding functions — [`STARFISH_LOG_INFO`](src:src/StarfishBase.h#L405) calls `forwardPrintingLogInfo`.
- Default (other platforms): `fprintf` to stdout/stderr with ANSI colors — [`STARFISH_LOG_INFO`](src:src/StarfishBase.h#L407) is additionally gated per module by [`LoggerOption::isLogEnable`](src:src/core/util/ProgramOptions.h#L36) (filter set parsed from the environment via [`parseEnv`](src:src/core/util/ProgramOptions.h#L38)); [`STARFISH_LOG_ERROR`](src:src/StarfishBase.h#L429) prints in red to stderr.
- Worker host processes prepend the tag [`"[WORKER] "`](src:src/StarfishBase.h#L363).

Monitoring/profiling facilities:

- The profiling module `src/core/modules/profiling/` defines [`ProfileKind`](src:src/core/modules/profiling/Profiling.h#L31) (`kStyle`, `kLayout`, `kPaint`, `kScript`, `kMISC`), the scoped [`ProfilerTimer`](src:src/core/modules/profiling/Profiling.h#L39), a [`LongTaskFinder`](src:src/core/modules/profiling/Profiling.h#L52) that reports tasks exceeding a millisecond threshold, and [`FrameRateCounter`](src:src/core/modules/profiling/FrameRateCounter.h#L31). Building with [`STARFISH_ENABLE_PROFILE`](src:src/StarfishBase.h#L357) turns on `STARFISH_ENABLE_PROFILE_TIMER` and `STARFISH_ENABLE_PROFILE_LOADING`.
- ARM Streamline annotation support: the vendored ARM header [src/streamline_annotate.h](src:src/streamline_annotate.h) provides the `ANNOTATE_*` macro family; it is included and activated only under [`STREAMLINE_PROFILE`](src:src/core/page/WebView.cpp#L91) in `WebView.cpp` (with [`ANNOTATE_SETUP`](src:src/core/page/WebView.cpp#L1019) executed during WebView initialization; no-op stubs otherwise).
- `tool/perf_tools/` contains the performance tooling directories `measure-bench`, `mp4-avc-equiv`, `mse-smoke`, and `style-smoke`.

## Performance Targets

No explicit performance targets (frame-rate, latency, or memory budgets) are defined in the repository — Not specified in code. The following optimization mechanisms are verified in code:

- **Link-time optimization (opt-in):** `-DLTO=1` adds [`-flto`](src:build/config.cmake#L470) to compile and link flags (documented as "Enable complier link time optimization", [README.md](src:README.md#L93)). On Tizen, LTO is force-disabled with [`-fno-lto`](src:build/config.cmake#L492) because, per the in-code comment, "lto causes GC bug". Non-Debug builds default to [`-O2`](src:build/config.cmake#L467).
- **HTTP disk cache:** [`HTTPCache`](src:src/platform/network/http/HTTPCache.h#L31) with cache modes [`LOAD_DEFAULT`/`LOAD_NORMAL`/`LOAD_CACHE_ELSE_NETWORK`/`LOAD_NO_CACHE`/`LOAD_CACHE_ONLY`](src:src/platform/network/http/HTTPCache.h#L34), an LRU list ([`HTTPCacheLRUList`](src:src/platform/network/http/HTTPCache.h#L26)), entry lookup/insertion ([`get`](src:src/platform/network/http/HTTPCache.h#L50), [`put`](src:src/platform/network/http/HTTPCache.h#L52)), and space management ([`expire`](src:src/platform/network/http/HTTPCache.h#L56), [`pruneAsNeededForCacheSpace`](src:src/platform/network/http/HTTPCache.h#L57)). The engine owns it as [`m_httpCache`](src:src/Starfish.h#L154); the cache mode is settable through the public API ([`GetCacheMode`](src:inc/LWEWebView.h#L228) / [`SetCacheMode`](src:inc/LWEWebView.h#L246)).
- **Resource cache in the loader:** [`ResourceCacheData`](src:src/platform/loader/ResourceLoader.h#L33) pairs a `Resource*` with a last-used tick count inside `ResourceLoader`.
- **Font cache:** [`PlatformFontCache`](src:src/core/modules/canvas/font/Font.h#L260) caches loaded font faces (`lookupFaceCache`/`insertFaceCache`/`clearFaceCache`).
- **Idle-time memory reclamation:** [`IdleModeJob`](src:inc/PlatformIntegrationData.h#L260) defines `ClearDrawnBuffers`, `ForceGC` (including `malloc_trim(0)` per comment), `DropDecodedImageBuffer`, and `ClearFontCache`, composable into full/middle/none presets.
- **Transport tuning:** optional HTTP/2 ([`UseHttp2`](src:inc/LWEWebView.h#L239) selecting [`CURL_HTTP_VERSION_2_0`](src:src/platform/network/http/HTTPTransaction.cpp#L124)) and TCP keepalive on media connections ([`CURLOPT_TCP_KEEPALIVE`](src:src/platform/network/http/HTTPTransaction.cpp#L130)).
