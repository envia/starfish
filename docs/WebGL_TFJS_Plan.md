# TFJS toxicity WebGL 구현 계획

작성일: 2026-09-17

검토 대상: `starfish_f_claude`의 `indigo/2025/webgl2/0375`,
`22a49cdca7` (8판, `Record the tool hash used to validate 0377`).
계획 합의 완료. 두 작업 브랜치는 표현과 언어가 달라도 아래 요구사항을 공유한다.
계획 합의는 구현 코드의 승인이나 검증 완료를 뜻하지 않는다.

## 목적과 완료 기준

Starfish에서 다음 원본 데모를 실행하고, WebGL1과 WebGL2를 각각 이용한
추론을 지원한다.

https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html

- 원본 페이지에서 모델 로딩, 초기 추론, 사용자 입력 분류가 완료된다.
- 별도 검증에서는 WebGL1과 WebGL2를 각각 강제하고 실제 선택된 TFJS
  backend와 WebGL 버전, `WEBGL_RENDER_FLOAT32_ENABLED`를 기록한다.
  WebGL2는 `WEBGL_BUFFER_SUPPORTED`도 기록한다. CPU fallback은 실패다.
- 같은 모델과 입력에 대해 CPU 참조 결과와 분류 결과 및 확률을 비교한다.
  TFJS 1.2.2, threshold 0.9, 아래의 고정 입력과 오차 기준을 사용한다.
- 소프트웨어 GL과 실제 GPU 사용을 구분한다. GPU 검증은 renderer 정보와
  Starfish 자체 GL context의 renderer 문자열과 해당 Starfish PID의
  `nvidia-smi` 프로세스 항목을 확보하고, 소프트웨어 fallback을 실패로 처리한다.
- 변경 전후 회귀 결과를 비교한다. 기존 실패와 신규 실패를 구분하고,
  신규 실패는 원인 확인 및 해결 없이 검증 완료로 처리하지 않는다.

TFJS에 필요한 경로를 우선 구현한다. WebGL 및 관련 확장 전체 구현은
이번 범위에 포함하지 않는다. 구현한 부분은 규격에 맞추고, 남은 제약은
명시한다. 검증 통과를 전체 규격 준수나 모든 회귀 부재의 증명으로 해석하지 않는다.

## 작업 및 협업 방식

- 개발 저장소: `starfish_f_codex`
- 개발 브랜치 및 push 대상: `origin/indigo/2025/webgl2/0376`
- Claude 검토 브랜치: `origin/indigo/2025/webgl2/0375`
- 시작 코드: `13c4ffd576` (`Bump version to 1.5.6`)
- 개발 환경: Linux x86_64, X11, `uv_cairo_gl`, Debug, `WEBGL=1`
- 통합 저장소 및 브랜치: `starfish_f`, `indigo/2025/webgl2/0377`
- Codex 작업을 Claude Code와 검토하고 합의한 변경을 통합 저장소에 반영한다.
  이 문서의 push만으로 통합 코드가 합의되었다고 간주하지 않는다.
- 기존 untracked `Makefile`, `web_tc_new_/`는 보존하고 임의로 커밋하지 않는다.
- 기능별 커밋에 관련 테스트와 필요한 문서 변경을 함께 포함한다.
  DCO 및 AI 기여자 trailer는 저장소 지침을 따른다.

### 0377에 반영할 범위 (사용자 확정)

- 검증 runner·probe·CPU 참조 데이터와 계획·검증 절차·결과 문서는 작업
  브랜치 `0375`·`0376`에 커밋해 보존한다. untracked 도구로만 남기지 않는다.
- 통합 브랜치 `0377`에는 합의한 구현 코드와 회귀 테스트·활성 목록을 반영한다.
  문서 변경은 `docs/Spec.md`만 반영한다.
- 작업용 검증 도구와 `docs/WebGL_TFJS_Plan.md`를 포함한 기타 문서는
  `0377`에 반영하지 않는다. TFJS 종합 검증 도구와 제품 회귀 테스트는
  구분하며, 이 제한 때문에 구현에 필요한 회귀 테스트를 제외하지 않는다.
- 작업용 도구·문서는 별도 커밋으로 분리해 통합 시 선택할 수 있게 한다.
  `Spec.md`와 회귀 테스트는 해당 기능 변경에 포함한다. 테스트 submodule의
  최종 gitlink에는 통합에 필요한 회귀 테스트가 포함되도록 확인한다.
- `0377` 검증에 사용한 작업 브랜치 도구의 commit hash와 실행 대상
  `0377` revision은 작업 브랜치의 결과 문서에 함께 기록한다.

이 계획의 순서는 사용자 및 Claude Code와 합의되었다.
구현 중 의존성이나 새로운 원인이 확인되면 순서와 범위 변경을
문서에 반영하고 공유한다.

## 참고 브랜치

`github` remote: `git@github.com:envia/lightweight-web-engine.git`

- `github/envia/2026/devel/0022`
- `github/envia/2026/devel/0730`
- `github/envia/2026/devel/0750`
- `origin/claude/2026/tfjs/0002`
- `origin/indigo/2025/webgl2/0171`
- `origin/indigo/2025/webgl2/0372`
- `origin/indigo/2025/webgl2/0373`
- `origin/indigo/2025/webgl2/0374`

브랜치 전체를 그대로 병합하지 않고 필요한 변경을 현재 코드 및 규격과 비교한다.
참고 브랜치에 기록된 성공 결과는 이번 작업의 검증 결과로 재사용하지 않는다.
구현 시 실제 참고한 commit hash를 기록해 이후 브랜치 이동과 구분한다.

## 확정 커밋 순서

아래는 이 계획 문서 커밋 이후의 기능 커밋 순서다.

| 순서 | 변경 내용 | 핵심 검증 |
| --- | --- | --- |
| 1 | `tool/tfjs_toxicity/` 검증 도구 커밋 | WebGL1·2 강제 선택, CPU 참조 비교, GL renderer 기록 |
| 2 | GL 컨텍스트가 current인 상태에서 확장 목록 초기화 | 첫 컨텍스트 및 반복 생성, 확장 조회, backend별 초기화 |
| 3 | float·half-float 텍스처 크기 계산, 업로드·부분 업로드·초기화 수정 | 데이터 보존, 영 초기화, 작은 버퍼 및 잘못된 입력, 기존 byte 텍스처 |
| 4 | WebGL1 float 렌더 타깃 지원 | ES3 저장 형식 변환, framebuffer 완전성, float 연산 및 읽기 |
| 5 | WebGL2 PBO·TypedArray 오프셋 `readPixels` 구현 및 관련 범위 검사 | pack 상태, 정렬·오프셋·버퍼 경계, `getBufferSubData`, fence 이후 결과 회수 |
| 6 | WebGL2 `EXT_color_buffer_float` 노출 및 core 승격 확장 숨기기 | 버전별 노출, float 렌더 타깃, `conformance2/extensions/promoted-extensions.html` 활성화 |
| 7 | `docs/WebGL_TFJS_Validation.md` 결과 문서화 | 아래 8조합에서 WebGL1·2, 원본 데모, CPU 결과 비교 및 회귀 검사 |

확장 노출은 PBO 구현 뒤에 배치한다. `0373`의 `614c9a3c15`에 기록된
다운로드 정지를 중간 커밋에서 유발하지 않기 위한 순서다.

커밋 1은 `run.py`, `toxicity-probe.js`, `toxicity-reference.json`, `README.md`를
`tool/tfjs_toxicity/`에 추가한다. 출처는 `0730`의 `02094e8638`, `ca3fb940ee`,
`7818039497`이며 runner는 backend·빌드 종류·GL 환경을 인자로 받는다.
사용법은 도구 README에 기록하며 저장소 루트 README는 변경하지 않는다.
이 도구 커밋은 `0377`에 반영하지 않는다.

기준선 확보는 별도 커밋이 아니라 커밋 1 이후, 첫 엔진 변경 전에 수행하는
단계다. 아래 매트릭스에서 비교할 스위트의 변경 전 결과를 같은 환경별로
확보하고, 양 WebGL 버전의 실패 양상과 CPU 참조 재측정 결과를 보관한다.

커밋 7은 행별 코드 revision, 빌드 옵션, 드라이버·renderer, 선택된 TFJS
backend·WebGL 버전, 입력별 판정, 최대 확률 절대 오차, 기준선 대비 suite diff
(기존/신규 실패), 참고용 시간, 미검증 항목 및 기준선 관찰을 기록한다.
`0377` 검증 시 도구 commit hash와 실행한 `0377` revision을 함께 기록한다.

특히 텍스처 초기화와 readback은 메모리 접근 범위에 영향을 주므로
빈 데이터, 경계 오프셋, 작은 버퍼, 큰 크기, 잘못된 타입 및 상태도 검증한다.
WebGL 버전 및 native GL 버전의 차이, 확장 지원·노출·활성화의 차이를
구분하고 필요한 기능만 노출한다.

### 합의한 구현 세부 사항

- 검증 도구는 `github/envia/2026/devel/0730`의 probe, runner 및 CPU 참조
  파일을 검토해 재사용한다. 원본 URL 실행과 버전·입력을 고정한 재현 검증을
  구분한다. 과거 CPU 참조 파일은 현재 자산과 일치하는지 확인한 뒤 사용한다.
- 확장 초기화는 실제 current context 안으로 옮긴다. 해당 커밋 안에
  current context가 없는 시작 조건을 재현하는 테스트를 넣는다.
  동기 HTML 테스트만으로 그 조건이 보장되지 않으면
  `origin/claude/2026/tfjs/0002`의 native 회귀 테스트를 검토해 사용한다.
  null 조회 재시도는 원인 수정의 대체 수단으로 사용하지 않는다.
- 내부 `webGLVersion()` 구분은 커밋 3에, native float capability 추적은
  커밋 4에 포함한다. native capability 추적만으로 확장을 노출하지 않는다.
- 텍스처 검증은 FLOAT/HALF_FLOAT의 typed array 종류와 확장 활성화,
  크기·level·border, null 초기화, unpack 상태 보존을 포함한다.
  WebGL2 client-memory 업로드와 `PIXEL_UNPACK_BUFFER` 바인딩의 충돌도 확인한다.
- readback은 TypedArray의 element offset과 PBO의 byte offset을 구분한다.
  pack 상태, subview, 빈 범위, overflow, 버퍼 크기를 검사한다.
  NVIDIA의 마지막 행 padding 우회는 현재 드라이버에서 재현한 뒤 도입 여부를
  결정하고, 적용 시 기존 상태 복원과 다른 드라이버의 동작도 검증한다.
- 커밋 2의 `webgl-extension-registry.html`은 페이지 로드 중 동기 생성한
  WebGL1·2 context의 확장 목록을 확인한다. `webgl-extension-version.html`은
  커밋 6에 배치한다. 나머지 후보 내부 테스트는
  `webgl-float-texture-upload.html`, `webgl1-float-render-target.html`,
  `webgl2-pixel-readback.html`이다. 기존 자산 유무를 먼저 확인한다.
- 후보 Khronos 테스트는 `texture-size.html`, `oes-texture-float.html`,
  `oes-texture-half-float.html`, `get-buffer-sub-data.html`,
  `read-pixels-into-pixel-pack-buffer.html`, `read-pixels-pack-parameters.html`,
  `conformance2/extensions/promoted-extensions.html`이다.
  실제 경로와 baseline을 확인하고 지원 대상 환경에서 통과한 항목을 활성화한다.

### 규격 및 수치 비교 기준

WebGL2 core로 이동한 WebGL1 확장 목록은 테스트 통과 여부가 아니라
[WebGL2 규격](https://registry.khronos.org/webgl/specs/latest/2.0/#extensions)의
버전별 규칙을 기준으로 필터링한다. `getSupportedExtensions()`와
`getExtension()`은 일관되어야 하며 기존에 잘못 노출된 항목의 수정도 테스트한다.
현재 레지스트리에서 WebGL2에 숨길 항목은 `OES_texture_float`,
`OES_texture_half_float`, `OES_standard_derivatives`, `OES_vertex_array_object`,
`WEBGL_depth_texture`, `EXT_blend_minmax`이다. `OES_texture_float_linear`와
`EXT_texture_filter_anisotropic`은 양 버전에 남긴다.

WebGL1 float 렌더 타깃의 우선 검증 대상은 TFJS가 사용하는 RGBA 계열이다.
RGB 저장 형식으로의 변환과 RGB의 렌더 가능 여부를 동일시하지 않는다.
특히 [EXT_color_buffer_float 규격](https://registry.khronos.org/webgl/extensions/EXT_color_buffer_float/)
상 `RGB16F`는 color-renderable이 아니다. native 지원, WebGL 버전,
확장 활성화별로 허용 여부를 검토한다. RGB/half-float의 모든 조합을 무조건
framebuffer complete로 기대하는 테스트를 만들지 않는다.

수치 비교는 TFJS 1.2.2, 원본 데모의 toxicity 모델, threshold 0.9를 사용한다.
입력은 데모 초기 3문장과 `Thank you for helping me.`의 4문장이다.
실제 입력 문자열과 모델 자산 식별 정보는 참조 데이터에 기록한다.
7 labels × 4문장의 판정 28개가 모두 일치하고 확률의 최대 절대 오차가
`1e-3` 이하여야 한다. 초기 3문장만의 판정은 21개다.
CPU 참조를 현재 빌드에서 재측정해 `0730` JSON과 비교하고 차이가 있으면
원인을 규명한 뒤 진행한다. 원본 페이지의 버전이 바뀌면 고정 참조와 혼용하지 않는다.
NaN/Infinity, 결과 누락 및 shape 불일치는 허용 오차와 무관하게 실패다.
작은 행렬 연산은 TFJS CPU forwarding을 끈 상태에서도 검사해 실제 GL
연산 경로를 검증한다. 과거 실행 시간은 성능 합격 기준으로 사용하지 않는다.

## 테스트 운영

- 구현 전 현재 코드의 관련 테스트 결과를 확보한다.
- 각 기능은 가장 가까운 내부 테스트와 Khronos 테스트부터 실행한다.
- 관련 WPT가 있으면 저장소의 `.res` 절차에 따라 활성화한다.
  WPT에 대응 항목이 없으면 내부 테스트를 추가하고 Khronos 테스트로 보완한다.
- 알려진 실패를 숨기거나 테스트 기대값을 구현에 맞춰 완화하지 않는다.
- 테스트는 `<checkout>/test`에 커밋한 뒤 동일 commit 객체를
  `<checkout>/web_tc_new_`로 가져와 fork `jh1984-hwang/web_tc_new`의
  `indigo/2025/webgl2/0376`으로 푸시한다. Claude는 `0375`를 사용한다.
  `/home/hwang/work/web_tc_new_`는 사용하지 않는다. Claude는 네 clone이 같은
  remote와 `254715162`에 있음을 확인했으며, 실행 시 대상 clone의 상태를 재확인한다.
- `0376`에서는 gitlink를 갱신하지 않고 각 기능 커밋에 테스트 commit hash와
  활성화 목록·적용 방법을 기록한다. `0377`에서는 최종 테스트 commit이
  submodule URL에서 접근 가능한 ref에 올라온 뒤 gitlink를 갱신해 새 checkout에서
  테스트를 재현할 수 있게 한다.
- IDL 변경 후에는 CMake를 다시 실행해 바인딩을 재생성한다.
- C++ 변경에는 tidy를 실행한다. 최종 회귀 검증은 WebGL1·2·SDK의 활성
  Khronos 목록 및 영향받는 Canvas 내부 테스트와 WPT를 포함한다.
- 테스트 실행은 저장소 지침에 따라 `xvfb-run -s '-screen 0 1920x1080x24' -a`로
  감싼다. GPU 테스트는 실제 GPU에 연결된 display/context를 사용하는지
  확인하고, 필요한 실행 설정을 재현 절차에 기록한다.
- 로그에는 코드 revision, 빌드 옵션, 드라이버·renderer, TFJS 및 모델 버전,
  테스트 결과, 수치 오차, 실패·제약 사항을 기록한다.

## 최종 검증 매트릭스

8행 모두 필수이며 각 행마다 WebGL1과 WebGL2를 별도로 검증한다.
빌드는 `out/<backend>-<type>`으로 분리하고 원본 데모의 자동 선택 경로도 확인한다.
전체 5개 suite는 `internal_test`, `vendor_test_khronos`, `vendor_test_khronos2`,
`vendor_test_khronossdk`, `wpt_serve_testharness_canvas`이며 아래 '앞의 3개'는
이 목록의 첫 세 suite다. 실행한 suite는 같은 환경의 기준선과 비교한다.
Release는 `testEnd` 바인딩이 없어 데모 probe로 결과를 판정한다.

| Backend | 빌드 | GL 실행 환경 | 회귀 suite | 상태 |
| --- | --- | --- | --- | --- |
| `uv_cairo_gl` | Debug | llvmpipe | 전체 5개 | 미실행 |
| `uv_cairo_gl` | Debug | NVIDIA | 활성화한 테스트 | 미실행 |
| `uv_cairo_gl` | Release | llvmpipe | 없음, 데모 검증 | 미실행 |
| `uv_cairo_gl` | Release | NVIDIA | 없음, 데모 검증 | 미실행 |
| `glib_cairo_gl` | Debug | llvmpipe | 앞의 3개 | 미실행 |
| `glib_cairo_gl` | Debug | NVIDIA | 활성화한 테스트 | 미실행 |
| `glib_cairo_gl` | Release | llvmpipe | 없음, 데모 검증 | 미실행 |
| `glib_cairo_gl` | Release | NVIDIA | 없음, 데모 검증 | 미실행 |

## 현재 검증 상태

계획 작성 시점에는 구현·빌드·추론 테스트를 수행하지 않았다.

초기 sandbox 내부 확인에서는 장치와 display에 접근하지 못했으나,
2026-09-17 sandbox 밖의 읽기 전용 확인에서 아래 정보를 확인했다.

- `/dev/dri/card1`, `/dev/dri/renderD128`, PCI `0000:01:00.0`
- `DISPLAY=:1`, direct rendering 활성화
- NVIDIA GeForce RTX 3050 OEM, 드라이버 `595.91.07`, OpenGL ES 3.2

별도 GPU 호스트 확보는 현재 blocker가 아니다. 실제 Starfish의 EGL context가
이 GPU를 사용하는지는 아직 검증하지 않았다. GPU 테스트는 필요한 sandbox 밖
실행 권한을 사용하고 Starfish 자체 GL context의 renderer와 해당 PID의
`nvidia-smi` 프로세스 항목으로 확인한다. 절차 확정과 검증 성공을 구분한다.
8조합 완료 전에는 종합 검증 완료로 보고하지 않는다.

참고 변경, 커밋 경계, 수치 비교 기준, 테스트 자산 통합 방식, GPU 실행 확인
절차는 합의 완료다. 기존 Claude 수정 요청 목록은 8판에 반영되어 제거했다.
한국어 문서와 `Codex <codex@ai.local>` trailer는 유지한다.
