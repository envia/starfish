# WebGL2 구현 작업 정리 (OSM/MapLibre 렌더링 목표)

## 1. 배경 / 출발점

`2026-06-30/iframe.html` (네이버 지도 iframe; 당시 http 로 서빙해 열었음) 이 검게 보이는 문제에서 출발.

- **네이버 지도가 검게 보인 직접 원인**: `m.map.naver.com` 이 `X-Frame-Options: SAMEORIGIN` 을
  내려 cross-origin iframe 임베드를 거부 → iframe 이 비고 body 의 검정 배경이 노출.
  (Starfish 의 정상 보안 동작. 버그 아님.)
- 대안으로 OSM 임베드(`https://www.openstreetmap.org/export/embed.html`)를 써보니, OSM 이 최근
  **MapLibre GL JS (WebGL 기반 벡터 렌더러)** 로 바뀌어 `webglcontextcreationerror` 가 발생.
- 원인 분석 결과: WebGL2 **컨텍스트 생성·기본 드로우는 정상**이나, MapLibre 가 요구하는
  **WebGL2 전용 API 다수가 미구현(IDL `[Unimplemented]`)** 이었음. (WebGL1 은 완전 구현)

탐침 페이지(`webgl_probe.html`)로 실측한 초기 상태:
- `getContext('webgl2')` 성공, `WebGL 2.0` / GLSL ES 3.00 / NVIDIA RTX 3050
- 단색 삼각형 드로우 성공 (`centerPixel=[255,0,0,255]`, glError 0)
- 그러나 `vertexAttribDivisor`, `drawElementsInstanced`, `getUniformBlockIndex`,
  `uniformBlockBinding`, `texStorage2D`, `drawBuffers` … 등이 `typeof === 'undefined'`
- WebGL2 IDL 의 `[Unimplemented]` 표시: **69줄(고유 메서드 55개)**

## 2. 구현 구조 (레이어)

각 WebGL2 진입점은 5개 레이어를 모두 거친다:

```
JS  →  ① IDL (WebGL2RenderingContext.idl)            // [Unimplemented] 제거 → 바인딩 생성됨
       ② 생성 바인딩 (cmake configure 시 자동 생성)
       ③ WebGL2RenderingContext.h / .cpp              // gl()->xxx() 호출 + 검증/형변환
       ④ GL.h                                          // 가상 함수 선언(추상 인터페이스)
       ⑤ GenericGL.cpp (데스크톱) + EvasGL.cpp (Tizen) // 실제 glXxx / m_evasGLAPI->glXxx
```

- 바인딩 생성은 **cmake configure 시점**에 IDL/생성기 mtime 의 MD5 시그니처가 바뀌면 실행
  (`build/starfish.cmake`). IDL 수정 후에는 `cmake -Bout/webgl2 ...` 재실행 필요.
- `GL` 은 순수가상 인터페이스라 `GenericGL` + `EvasGL` **둘 다** 구현해야 컴파일됨
  (빌드에 둘 다 포함).

## 3. Batch 1 구현 내역 (완료, 검증됨)

IDL `[Unimplemented]` 제거 + 5레이어 구현한 메서드:

| 분류 | 메서드 |
|------|--------|
| 인스턴스 드로잉 | `vertexAttribDivisor`, `drawArraysInstanced`, `drawElementsInstanced` |
| Uniform Block (UBO) | `getUniformBlockIndex`, `uniformBlockBinding`, `getActiveUniformBlockParameter`, `getActiveUniformBlockName` |
| MRT / 읽기버퍼 | `drawBuffers`, `readBuffer` |
| 프레임버퍼 | `blitFramebuffer`, `framebufferTextureLayer`, `renderbufferStorageMultisample`, `invalidateFramebuffer` |
| 불변 텍스처 스토리지 | `texStorage2D` |

변경 파일:
- `src/core/dom/canvas/webgl/WebGL2RenderingContext.idl` (−14 `[Unimplemented]`)
- `src/core/dom/canvas/webgl/WebGL2RenderingContext.h` / `.cpp` (+선언/+구현)
- `src/core/dom/canvas/webgl/WebGLRenderingContext.h` (`completePendingJobs()` private→protected)
- `src/platform/canvas/gl/GL.h` (+15 가상함수, `invalidateFramebuffer` 는 기존재)
- `src/platform/canvas/gl/GenericGL.cpp`, `src/platform/canvas/gl/EvasGL.cpp` (+구현)

구현 시 주의했던 점:
- 인스턴스 드로우는 base `drawArrays/drawElements` 와 동일하게 `completePendingJobs()` +
  `canvas()->setNeedsComposite()` 호출. (그래서 base 의 `completePendingJobs()` 를 protected 로)
- `drawElementsInstanced` 의 `GLintptr offset` 은 `reinterpret_cast<void*>(offset)`.
- `sequence<GLenum>` / `sequence<GLuint>` 인자는 생성기가 `GCAtomicVector<uint32_t>` 로 매핑
  (IDL `GLenum`/`GLuint` 모두 `unsigned long` → C++ `uint32_t` ≡ `GLenum`).
- `getActiveUniformBlockParameter` 는 pname 별로 GLuint / Uint32Array / GLboolean 반환.
- 새 cpp 에서 `HTMLCanvasElement`, `WebGLTexture` 완전형이 필요 → include 추가.

### 검증 결과

`webgl_probe.html` 재실행: 위 메서드 전부 `typeof === 'function'` 확인.

`maplibre_top.html` (MapLibre v4.7.1, **raster** 스타일, 키 불필요) 실행:
- 이전: `webglcontextcreationerror` 즉시 발생
- **현재: 에러 없음, 타일 텍스처 업로드 4회, `onload` + `enter idle mode` → 래스터 지도 정상 렌더**

즉 **WebGL2 의 핵심 경로(UBO + 인스턴싱 + FBO)는 동작**한다.

## 4. 추가 발견: OSM(벡터)은 WebGL 외의 Web API 도 필요

OSM 임베드는 MapLibre 의 **벡터 타일** 경로를 쓴다. 이 경로는 WebGL 외에 추가 Web 플랫폼 API 에
의존하며, 키워보면 블로커가 WebGL 에서 **일반 Web API** 로 이동한다:

| 단계 | 블로커 | 상태 / 조치 |
|------|--------|-------------|
| 1 | WebGL2 전용 API 미구현 | ✅ Batch 1 구현 완료 (raster 렌더 확인) |
| 2 | `Worker is not defined` | ✅ 빌드가 `WORKER=0` 이었음 → **`-DWORKER=1` 로 재빌드** 하여 해결 (Starfish 에 Worker 구현은 이미 존재) |
| 3 | `AbortController is not defined` | ❌ Starfish 에 **미구현** (`AbortSignal` 도 `Request.idl` 에 주석 처리된 `[Unimplemented]` 만 존재) — 다음 작업 대상 |
| 4+ | (이후 추가 가능) | `fetch`/`XMLHttpRequest` 는 구현되어 있음. AbortController 이후 추가 누락 API 가 더 나올 수 있음 |

빌드 플래그 메모: `-DWORKER=1` → `STARFISH_ENABLE_WORKER` + `STARFISH_ENABLE_THREADING`
(`build/config.cmake`). 전역 define 이라 전체 재컴파일.

## 5. 현재 상태 요약 (업데이트)

구현/조치 누적: WebGL2 Batch1 ✅ · Worker 활성화(`-DWORKER=1`) ✅ ·
`AbortController`/`AbortSignal` 구현 ✅ · `replaceChildren()` 구현 ✅.

각 단계의 가시적 변화(스크린샷, `xwd -id` + PIL 로 캡처):

- **래스터 지도 (Leaflet / MapLibre-raster)**: **정상 렌더**.
- **OSM 임베드 (MapLibre vector)**:
  - 이전: 전체 검정.
  - 현재: **검정 아님** — 페이지 배경(흰색) + **줌 컨트롤(+/−)** + **OSM attribution** 이 정상 표시.
    JS 에러 0개. 단, **지도 타일 이미지(캔버스 내용)는 아직 비어 있음**.
- **최상위 벡터 지도 (demotiles)**:
  - **WebGL 캔버스가 그려짐** — `background` 레이어(바다색 연한 파랑)가 렌더되고 MapLibre
    attribution 표시. 에러 0개.
  - 단, **벡터 타일 지오메트리(국경/면)는 미표시**. 즉 단색 fill 레이어는 그려지나
    벡터 타일 데이터가 화면에 안 나옴.

### 벡터 타일 파이프라인(Worker) 디버깅 결과

격리 테스트(`worker_test*.html`)로 워커 서브시스템을 단계별로 검증:

1. **외부 `.js` 워커**: 정상 (script 실행 + main↔worker postMessage 왕복 OK).
2. **`blob:` URL 워커**(= MapLibre 가 쓰는 방식): **생성은 되나 스크립트가 로드/실행 안 됨**.
   - 원인: 워커는 별도 스레드에서 **자신만의 빈 blob-URL 스토어**로 동작
     (`WebWorker::createGlobalScope()` 가 `clearBlobURLStore()` 호출). blob 은 부모(메인)
     WebBase 스토어에만 등록되어 있어 워커 스레드가 `blob:` 스크립트 URL 을 못 받음.
   - **수정**: `WorkerThread(WebBase*, ResourceURL*)` 생성자(메인 스레드, blob 유효)에서
     scriptURL 이 blob 이면 blob 바이트를 읽어 `data:application/javascript;base64,...`
     로 치환. 추가로 blob URL 에 박혀있는 문서 URL 을 추출해 baseURL 로 사용
     (data: 를 blob: base 에 resolve 하면 invalid → 워커가 자기 스크립트를 거부했었음).
   - 검증: 수정 후 blob 워커가 **script 로드 + postMessage 왕복 + 워커 내 fetch(.pbf)
     status=200, 101,760 bytes** 까지 정상.
   - 파일: `src/core/modules/worker/WorkerThread.cpp`.

### 워커 프리미티브 전수 검증 (격리 테스트) — 모두 정상

`worker_*.html` 로 MapLibre 가 의존하는 워커 기능을 하나씩 검증한 결과 **전부 동작**:

| 기능 | 결과 |
|------|------|
| 외부 `.js` 워커 script 실행 + postMessage 왕복 | ✅ |
| blob: 워커 (수정 후) | ✅ script 로드 + 왕복 |
| 워커 내 `fetch(.pbf)` | ✅ status=200, 101,760 bytes |
| transferable ArrayBuffer (main↔worker) | ✅ 데이터 정확 전송 (단, 원본 버퍼 neutering 은 미구현 — 비치명) |
| 복잡/중첩 구조화 클론 (배열+객체+다수 TypedArray+transfer) | ✅ 완전 일치 |
| 워커 글로벌 API | ✅ TextDecoder/TextEncoder/performance/fetch/atob/ImageData/createImageBitmap/Response/Promise 등 존재 (OffscreenCanvas·WebAssembly·caches 는 없음 — MapLibre v4 벡터파싱엔 불필요) |

### 현재 상태: 프리미티브는 다 되는데 MapLibre 타일이 완료되지 않음

- `map.on('data')` 기준 `srcData=4, tiles=0, errs=0, sourceLoaded=false`, `load`/`idle`
  이벤트 미발생. 즉 **타일 로드가 완료되지도, 에러를 내지도 않음** (조용히 안 끝남).
- 워커 프리미티브가 전부 동작하므로 원인은 **MapLibre 내부 Actor 프로토콜의 특정 지점**
  (loadTile 메시지 라우팅/응답 등)으로 좁혀지며, 블랙박스(격리) 테스트로는 재현·관측 불가.
- 다음 단계(비용 큼): 엔진 측 워커 메시지 디스패치(`WorkerObjectProxy`/postMessage 경로)에
  임시 로깅을 넣어 MapLibre 의 loadTile 요청이 워커에 도달하고 응답이 돌아오는지 추적.

### 결론(현 시점)
- 검정 → OSM 임베드가 **컨트롤·attribution 렌더 + WebGL 캔버스 배경 렌더**까지 도달.
- 엔진에 **실질 수정 5건**(WebGL2 Batch1 / Worker 활성화 / AbortController·AbortSignal /
  replaceChildren / blob 워커) 반영·검증 완료.
- 벡터 지오메트리 최종 렌더는 MapLibre Actor 내부 이슈로 남아 있으며, 추가 진행 시
  엔진측 워커 메시지 추적이 필요.

## 6. 작업 현황 (OSM 벡터까지)

### 완료 (검증됨)
- ✅ WebGL2 Batch1 (인스턴싱 + UBO + FBO + texStorage2D) — §3. 래스터 MapLibre 렌더.
- ✅ Worker 활성화 (`-DWORKER=1`).
- ✅ `AbortController` / `AbortSignal` 구현 + 전역(Window/Worker) 노출.
- ✅ `ParentNode.replaceChildren()` — OSM 컨트롤 렌더.
- ✅ blob: URL 워커 (부모 스레드에서 data: URL 로 치환) — 워커 script 로드 + fetch 정상.
- ✅ (별도) 동적 모듈 import 실패 크래시 방어 — §8.

### 남음 (OSM 벡터 지오메트리)
1. **핵심**: OSM/MapLibre 벡터 **지오메트리(국경/면)가 아직 미표시**. WebGL 캔버스는 그림
   (배경 fill 렌더). 워커 프리미티브(blob 로드/fetch/postMessage/transferable/구조화 클론/
   워커 API)는 §5 에서 전수 검증돼 **전부 정상**인데, 타일이 완료(`sourceLoaded`)되지 않고
   에러도 없음.
   → 다음 단계: 엔진측 워커 메시지 디스패치(`WorkerObjectProxy`/postMessage 경로)에 임시
     로깅을 넣어 MapLibre Actor 의 `loadTile` 요청 도달/응답을 추적 (블랙박스로는 관측 불가).
     ※ 편집 가능한(비압축) MapLibre dev 빌드를 로컬 서빙하면 워커 내부 지점에 로그를 심어
       분석하기 쉬움.
2. (선택) `EXT_color_buffer_float` 확장 등록 — DEM/terrain/hillshade/heatmap 레이어용.
3. (선택) WebGL2 잔여 `[Unimplemented]` (queries, samplers, transform feedback, texImage3D,
   clearBuffer*, getInternalformatParameter 등) — MapLibre 가 실제로 호출할 때 추가.
4. (선택) transferable 소스 버퍼 neutering(detach) 미구현 — 현재 데이터 전송은 정상이라
   비치명. 스펙 준수 필요 시 구현.

## 7. 테스트 자산 (repo 루트 `2026-06-30/`)

http 로 서빙해서 사용: repo 루트에서 `python3 -m http.server 8000` →
`http://127.0.0.1:8000/2026-06-30/<파일>` (동적 import/워커 테스트는 file:// 로 동작 안 함).

- `2026-06-30/webgl_probe.html` — WebGL2 메서드/확장/드로우 탐침 (결과를 throw 로 stdout 출력)
- `2026-06-30/maplibre_top.html` — 최상위 MapLibre 테스트(raster→vector 전환하며 사용),
  에러는 `setTimeout` 안에서 throw 하여 stdout 으로 surface (MapLibre 가 핸들러 throw 를 삼키므로)
- `2026-06-30/maplibre_diag.html` — 타일/`isSourceLoaded` 추적 진단 (§5 벡터 블로커용)
- `2026-06-30/map_osm.html` — 키 없는 래스터 지도(Leaflet) — 정상 동작
- `2026-06-30/iframe_osm.html` — OSM 임베드(벡터) — 진행 중
- `2026-06-30/worker_*.html`(+`*_child.js`) — 워커 프리미티브 격리 하네스 (§5 전수 검증에 사용)
- `2026-06-30/crash/module_import_crash_manual.html` — §8 모듈 import 크래시 수동 테스트
  (http 로 열면 초록 "PASS" 표시; `not-a-module.js` 를 import)

### 실행/디버깅 메모
- 엔진: `DISPLAY=:1 ./out/webgl2/bin/lightweight-web-engine <URL>` (인자로 URL, X11 창)
- 셸 `sleep` 이 막혀 있어 포그라운드 대기는 실패(exit 144) → 엔진은 background 실행 후
  로그 파일을 `until grep` 로 폴링.
- `console.log` 는 인스펙터 빌드에서만 stdout 으로 가므로, 진단은 `throw new Error(...)` 의
  `Uncaught` 로그(ScriptWrappable)를 이용.

## 8. 별도 버그: 동적 모듈 import 실패 시 크래시 (수정 완료)

위 렌더링 작업과 **무관한 별개 버그**. `https://m.map.naver.com/search2/search.naver?query=...`
를 (iframe 이 아니라) Starfish 로 **직접** 열면 크래시(SIGABRT)가 났다.

### 원인 (worker/WebGL 아님 — 모듈 로더 널 언랩)
- 네이버 페이지가 로드하는 ES 모듈 의존성 중 하나(`https://m.map.naver.com/_`)가 **JS 가 아니라
  HTML 을 반환** → 모듈 파싱 실패(`initModule`: "Line 2: Unexpected token <").
- 파싱 실패한 모듈의 컴파일 핸들은 빈 `Optional<Escargot::ScriptRef*>`.
- `Document::executeModule()` 의 **동적 import() 프로미스 처리 루프**가 이 빈 Optional 을
  `hasValue()` 확인 없이 `data->module.value()` 로 언랩 → `StarfishBase.h:743` assertion →
  `abort()`.
- gdb 백트레이스: `Resource::didLoadFinished` → `DeferredScriptDownloadClient::didScriptLoaded`
  → `Document::executeModule (Document.cpp:734)` → `Optional<ScriptRef>::value()`.
- **Escargot 는 정상**(파싱 실패를 올바르게 보고). Starfish 가 그 실패 결과를 방어 안 한 것.
  → 수정도 Starfish 측만.

### 수정
- 파일: `src/core/dom/Document.cpp` (`executeModule`).
- 모듈이 `hasLoadingError` 이거나 값이 없으면 `data->module.value()` 대신
  `notifyDynamicLoadedModuleError()` 로 import() 프로미스를 **reject** (스펙상 실패한 dynamic
  import 의 정상 동작).
- 커밋: `bac34b4b` "Reject failed dynamic module imports instead of crashing".
- 검증: 네이버 URL 재실행 시 이전 `exit 134 (SIGABRT)` → `exit 124 (정상 타임아웃, 크래시 0)`,
  onload 정상 발생.

### 테스트
- **수동**: `2026-06-30/crash/module_import_crash_manual.html` (+ `not-a-module.js`, repo 루트).
  http 로 열면 JS mime + HTML 본문 모듈을 import → 크래시 없으면 초록 "PASS" 표시.
  (동적 import() 는 http 문서에서만 fetch 하므로 file:// 로는 재현 불가.)
- **자동 (test 서브모듈)**:
  `test/cairo/internal-test/served-resources/crash/js-module-dynamic-import-fail.html` +
  `.../not-a-module.js`, `tool/reftest/cairo/internal_with_remote_resource.res` 에
  `http://localhost:11011/crash/js-module-dynamic-import-fail.html` 로 등록.
  (`internal_test()` 가 `served-resources` 를 http 11011 로 서빙하는 목록. 문서가 http 여야
  동적 import 이 동작하므로 이 목록에 둠.) 살아남으면 `testEnd()` 가 `[PASS]`, 크래시 시
  러너가 `[STARFISH_TEST] Got signal` 로 FAIL 감지.
- 회귀 검출 확인: 가드 임시 제거+재빌드 → 테스트가 SIGABRT 로 FAIL; 수정 복원 → `[PASS]`
  (3회 결정적, `parse_err=1` 로 크래시 경로 실행 확인).
- 커밋: 서브모듈 `d0307f58` (테스트 파일), 메인 `d065e381` (등록 + 서브모듈 포인터).
