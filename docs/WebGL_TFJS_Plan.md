# TFJS toxicity WebGL 구현 계획

작성일: 2026-09-17

검토 대상: `starfish_f_claude`의 `indigo/2025/webgl2/0375`,
`5ebefdb0c2` (`Add WebGL plan for the TFJS toxicity demo`).
아래 보완 사항은 Codex의 검토 제안이며 Claude와의 최종 합의 전이다.

## 목적과 완료 기준

Starfish에서 다음 원본 데모를 실행하고, WebGL1과 WebGL2를 각각 이용한
추론을 지원한다.

https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html

- 원본 페이지에서 모델 로딩, 초기 추론, 사용자 입력 분류가 완료된다.
- 별도 검증에서는 WebGL1과 WebGL2를 각각 강제하고 실제 선택된 TFJS
  backend와 WebGL 버전을 기록한다. CPU fallback만으로 성공 처리하지 않는다.
- 같은 모델과 입력에 대해 CPU 참조 결과와 분류 결과 및 확률을 비교한다.
  모델·TFJS 버전, 입력, 오차 허용 기준을 구현 시작 시 고정하고 기록한다.
- 소프트웨어 GL과 실제 GPU 사용을 구분한다. GPU 검증은 renderer 정보와
  가능한 장치별 실행 증거를 확보하고, 소프트웨어 fallback을 실패로 처리한다.
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

이 계획의 순서는 사용자와 합의되었으며, 이 문서를 바탕으로 Claude Code와
추가 검토한다. 구현 중 의존성이나 새로운 원인이 확인되면 순서와 범위 변경을
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

## 제안 커밋 순서

아래는 이 계획 문서 커밋 이후의 기능 커밋 순서다.

| 순서 | 변경 내용 | 핵심 검증 |
| --- | --- | --- |
| 1 | TFJS 검증 도구 및 변경 전 기준 결과 확보 | WebGL1·2 강제 선택, CPU 참조 결과, GL renderer 기록, 현재 실패 재현 |
| 2 | GL 컨텍스트가 current인 상태에서 확장 목록 초기화 | 첫 컨텍스트 및 반복 생성, 확장 조회, backend별 초기화 |
| 3 | float·half-float 텍스처 크기 계산, 업로드·부분 업로드·초기화 수정 | 데이터 보존, 영 초기화, 작은 버퍼 및 잘못된 입력, 기존 byte 텍스처 |
| 4 | WebGL1 float 렌더 타깃 지원 | ES3 저장 형식 변환, framebuffer 완전성, float 연산 및 읽기 |
| 5 | WebGL2 `EXT_color_buffer_float` 노출 | 드라이버 지원과 WebGL 버전에 따른 노출, float 렌더 타깃 |
| 6 | WebGL2 PBO·TypedArray 오프셋 `readPixels` 구현 및 관련 범위 검사 | pack 상태, 정렬·오프셋·버퍼 경계, `getBufferSubData`, fence 이후 결과 회수 |
| 7 | 종합 검증 절차 및 결과 문서화 | 아래 8조합에서 WebGL1·2, 원본 데모, CPU 결과 비교 및 회귀 검사 |

특히 텍스처 초기화와 readback은 메모리 접근 범위에 영향을 주므로
빈 데이터, 경계 오프셋, 작은 버퍼, 큰 크기, 잘못된 타입 및 상태도 검증한다.
WebGL 버전 및 native GL 버전의 차이, 확장 지원·노출·활성화의 차이를
구분하고 필요한 기능만 노출한다.

### Claude 계획에서 반영할 구현 세부 사항

- 검증 도구는 `github/envia/2026/devel/0730`의 probe, runner 및 CPU 참조
  파일을 검토해 재사용한다. 원본 URL 실행과 버전·입력을 고정한 재현 검증을
  구분한다. 과거 CPU 참조 파일은 현재 자산과 일치하는지 확인한 뒤 사용한다.
- 확장 초기화는 실제 current context 안으로 옮긴다. 해당 커밋 안에
  current context가 없는 시작 조건을 재현하는 테스트를 넣는다.
  동기 HTML 테스트만으로 그 조건이 보장되지 않으면
  `origin/claude/2026/tfjs/0002`의 native 회귀 테스트를 검토해 사용한다.
  null 조회 재시도는 원인 수정의 대체 수단으로 사용하지 않는다.
- 내부 `webGLVersion()` 구분과 native float capability 추적은 최초로
  필요한 기능 커밋에 포함한다. WebGL2 확장 노출 전에도 WebGL1 ES3 저장
  형식 변환에서 이 정보가 필요할 수 있다.
- 텍스처 검증은 FLOAT/HALF_FLOAT의 typed array 종류와 확장 활성화,
  크기·level·border, null 초기화, unpack 상태 보존을 포함한다.
  WebGL2 client-memory 업로드와 `PIXEL_UNPACK_BUFFER` 바인딩의 충돌도 확인한다.
- readback은 TypedArray의 element offset과 PBO의 byte offset을 구분한다.
  pack 상태, subview, 빈 범위, overflow, 버퍼 크기를 검사한다.
  NVIDIA의 마지막 행 padding 우회는 현재 드라이버에서 재현한 뒤 도입 여부를
  결정하고, 적용 시 기존 상태 복원과 다른 드라이버의 동작도 검증한다.
- 후보 내부 테스트는 `webgl-extension-version.html`,
  `webgl-float-texture-upload.html`, `webgl1-float-render-target.html`,
  `webgl2-pixel-readback.html`이다. 기존 자산 유무를 먼저 확인한다.
- 후보 Khronos 테스트는 `texture-size.html`, `oes-texture-float.html`,
  `oes-texture-half-float.html`, `get-buffer-sub-data.html`,
  `read-pixels-into-pixel-pack-buffer.html`, `read-pixels-pack-parameters.html`이다.
  실제 경로와 baseline을 확인하고 지원 대상 환경에서 통과한 항목을 활성화한다.

### 규격 및 수치 비교 기준

WebGL2 core로 이동한 WebGL1 확장 목록은 테스트 통과 여부가 아니라
[WebGL2 규격](https://registry.khronos.org/webgl/specs/latest/2.0/#extensions)의
버전별 규칙을 기준으로 필터링한다. `getSupportedExtensions()`와
`getExtension()`은 일관되어야 하며 기존에 잘못 노출된 항목의 수정도 테스트한다.

WebGL1 float 렌더 타깃의 우선 검증 대상은 TFJS가 사용하는 RGBA 계열이다.
RGB 저장 형식으로의 변환과 RGB의 렌더 가능 여부를 동일시하지 않는다.
특히 [EXT_color_buffer_float 규격](https://registry.khronos.org/webgl/extensions/EXT_color_buffer_float/)
상 `RGB16F`는 color-renderable이 아니다. native 지원, WebGL 버전,
확장 활성화별로 허용 여부를 검토한다. RGB/half-float의 모든 조합을 무조건
framebuffer complete로 기대하는 테스트를 만들지 않는다.

수치 비교 기준 제안은 분류 결정 21개 일치 및 확률의 최대 절대 오차
`1e-3` 이하이다. 이는 Claude 계획의 허용값을 검토용으로 채택한 것이며,
동일 TFJS·모델·입력·threshold의 CPU 재측정 후 구현 전에 확정한다.
NaN/Infinity, 결과 누락 및 shape 불일치는 허용 오차와 무관하게 실패다.
작은 행렬 연산은 TFJS CPU forwarding을 끈 상태에서도 검사해 실제 GL
연산 경로를 검증한다. 과거 실행 시간은 성능 합격 기준으로 사용하지 않는다.

## 테스트 운영

- 구현 전 현재 코드의 관련 테스트 결과를 확보한다.
- 각 기능은 가장 가까운 내부 테스트와 Khronos 테스트부터 실행한다.
- 관련 WPT가 있으면 저장소의 `.res` 절차에 따라 활성화한다.
  WPT에 대응 항목이 없으면 내부 테스트를 추가하고 Khronos 테스트로 보완한다.
- 알려진 실패를 숨기거나 테스트 기대값을 구현에 맞춰 완화하지 않는다.
- `test/`는 submodule이므로 테스트 자산 커밋과 본 저장소 gitlink의 관계를
  명시한다. 기존 `web_tc_new_/`와의 중복·통합 방식은 내용을 확인한 뒤 정한다.
  Claude의 `/home/hwang/work/web_tc_new_`와 checkout 내부 `web_tc_new_/`는
  경로가 다르므로 동일 저장소로 가정하지 않는다. 담당 브랜치와 push 대상을
  확정한 후 테스트를 공유한다. 각 기능 커밋은 대응 테스트 commit hash 및
  적용 방법을 기록한다. 통합 브랜치에서는 최종 gitlink를 반영해 새 checkout만으로
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

각 행마다 WebGL1과 WebGL2를 별도로 검증한다. 빌드는 서로 다른 출력
디렉터리로 분리하고, 원본 데모의 자동 선택 경로도 확인한다.

| Backend | 빌드 | GL 실행 환경 | 상태 |
| --- | --- | --- | --- |
| `uv_cairo_gl` | Debug | 소프트웨어 GL | 미실행 |
| `uv_cairo_gl` | Debug | GPU 가속 | 미실행 |
| `uv_cairo_gl` | Release | 소프트웨어 GL | 미실행 |
| `uv_cairo_gl` | Release | GPU 가속 | 미실행 |
| `glib_cairo_gl` | Debug | 소프트웨어 GL | 미실행 |
| `glib_cairo_gl` | Debug | GPU 가속 | 미실행 |
| `glib_cairo_gl` | Release | 소프트웨어 GL | 미실행 |
| `glib_cairo_gl` | Release | GPU 가속 | 미실행 |

## 미확정 사항 및 현재 검증 상태

계획 작성 시점에는 구현·빌드·추론 테스트를 수행하지 않았다.

초기 sandbox 내부 확인에서는 장치와 display에 접근하지 못했으나,
2026-09-17 sandbox 밖의 읽기 전용 확인에서 아래 정보를 확인했다.

- `/dev/dri/card1`, `/dev/dri/renderD128`, PCI `0000:01:00.0`
- `DISPLAY=:1`, direct rendering 활성화
- NVIDIA GeForce RTX 3050 OEM, 드라이버 `595.91.07`, OpenGL ES 3.2

별도 GPU 호스트 확보는 현재 blocker가 아니다. 실제 Starfish의 EGL context가
이 GPU를 사용하는지는 아직 검증하지 않았다. GPU 테스트는 필요한 sandbox 밖
실행 권한을 사용하고 Starfish 자체의 renderer 및 실행 증거를 기록한다.
8조합 완료 전에는 종합 검증 완료로 보고하지 않는다.

Claude Code와 검토할 항목은 참고 변경의 선택, 커밋 경계, 수치 오차 기준,
테스트 자산 통합 방식, Starfish GPU 실행 확인 방법이다.

## Claude Code 문서에 요청하는 수정

1. 최종 검증에 두 backend × Debug/Release × 소프트웨어/GPU의 8조합을
   명시하고, 각 조합에서 WebGL1·2와 원본 페이지의 자동 선택 경로를 확인한다.
   회귀 목록에는 Khronos SDK 및 영향받는 Canvas/WPT도 포함한다.
2. baseline·CPU 참조·검증 도구 준비를 구현 전에 배치하고 초기화 회귀 테스트는
   초기화 수정과 같은 커밋에 넣는다. 다음 기능 커밋의 테스트에 의존하지 않는다.
3. WebGL2에서 core로 이동한 확장 필터링의 기본값을 규격 기준으로 변경한다.
   테스트가 요구할 때만 수정한다는 조건을 제거한다.
4. native float 지원과 WebGL 확장 활성화, RGB와 RGBA 렌더 가능 여부를
   구분한다. 부분 구현의 알려진 제약은 기록하되 새 규격 위반을 허용하는 근거로
   사용하지 않는다.
5. CPU 참조의 버전·입력·threshold 및 오차 정의를 명시한다. 이전 성능 수치와
   테스트 성공 기록은 이번 검증 결과나 예상 성능 보장과 분리한다.
6. 테스트 저장소의 정확한 경로·브랜치·commit hash와 최종 gitlink 갱신을
   명시한다. 테스트가 어느 저장소에도 없다는 단정은 확인한 범위로 한정하고,
   기존 자산을 확인한 후 재사용 또는 재작성한다.
7. 검증 도구를 untracked로 둔다는 기본안을 제거한다. 도구와 작업 문서는
   `0375`·`0376`에 커밋하되 `0377`에는 가져가지 않는다. `0377`의 문서 변경은
   사용자 결정에 따라 `docs/Spec.md`로 제한한다.

위 항목은 Claude checkout을 직접 수정한 결과가 아니다. Codex 문서에 반영한
검토 의견이며 사용자와 Claude가 비교·합의한 뒤 통합한다.
