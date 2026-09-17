# TFJS toxicity WebGL 구현 계획

작성일: 2026-09-17

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
- 시작 코드: `13c4ffd576` (`Bump version to 1.5.6`)
- 개발 환경: Linux x86_64, X11, `uv_cairo_gl`, Debug, `WEBGL=1`
- 통합 저장소 및 브랜치: `starfish_f`, `indigo/2025/webgl2/0377`
- Codex 작업을 Claude Code와 검토하고 합의한 변경을 통합 저장소에 반영한다.
  이 문서의 push만으로 통합 코드가 합의되었다고 간주하지 않는다.
- 기존 untracked `Makefile`, `web_tc_new_/`는 보존하고 임의로 커밋하지 않는다.
- 기능별 커밋에 관련 테스트와 필요한 문서 변경을 함께 포함한다.
  DCO 및 AI 기여자 trailer는 저장소 지침을 따른다.

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

## 테스트 운영

- 구현 전 현재 코드의 관련 테스트 결과를 확보한다.
- 각 기능은 가장 가까운 내부 테스트와 Khronos 테스트부터 실행한다.
- 관련 WPT가 있으면 저장소의 `.res` 절차에 따라 활성화한다.
  WPT에 대응 항목이 없으면 내부 테스트를 추가하고 Khronos 테스트로 보완한다.
- 알려진 실패를 숨기거나 테스트 기대값을 구현에 맞춰 완화하지 않는다.
- `test/`는 submodule이므로 테스트 자산 커밋과 본 저장소 gitlink의 관계를
  명시한다. 기존 `web_tc_new_/`와의 중복·통합 방식은 내용을 확인한 뒤 정한다.
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

현재 명령 실행 환경에서 `/dev/dri`와 `/dev/nvidia*`가 보이지 않았고,
`glxinfo -B`는 `DISPLAY=:1`에 연결하지 못했다. 이는 현재 환경의 관찰이며
호스트 자체에 GPU가 없다는 결론은 아니다. GPU 검증 전에 실행 가능한
호스트·컨테이너·display 및 접근 방법을 확인해야 한다.

GPU 환경 확보가 지연되면 가능한 개발 및 소프트웨어 검증은 진행하되,
GPU 항목은 미검증으로 남긴다. 8조합 완료 전에는 종합 검증 완료로 보고하지 않는다.

Claude Code와 검토할 항목은 참고 변경의 선택, 커밋 경계, 수치 오차 기준,
테스트 자산 통합 방식, GPU 검증 환경이다.
