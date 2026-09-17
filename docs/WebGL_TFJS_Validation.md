# TFJS WebGL 검증 기록

2026-09-17, Codex 작업 브랜치 `indigo/2025/webgl2/0376`.
이번 범위는 검증 도구와 current GL context에서의 확장 registry 초기화까지다.
텍스처·float 렌더 타깃·PBO·확장 노출은 아직 구현하지 않았다.
이 문서와 검증 도구는 `0377`에 반영하지 않는다.

## 환경 및 재현 자료

- 시작 엔진: `13c4ffd576` (1.5.6). 도구 커밋: `94077b9531`.
- 초기화 수정 커밋: `0c89103775`. 수정 후 측정한 소스와 동일하다.
  기존 기능의 초기화 시점 수정이므로 새 IDL/API 노출이나 `Spec.md` 변경은 없다.
- `out/webgl2`: Linux x86_64, X11, `uv_cairo_gl`, Debug, `WEBGL=1`.
  기존 설정은 `IDB=0`, `WORKER=0`이다.
- 소프트웨어: Mesa llvmpipe (LLVM 20.1.2, 256 bits), `LP_NUM_THREADS=4`.
- GPU: NVIDIA GeForce RTX 3050 OEM, 드라이버 595.91.07, `DISPLAY=:1`.
- 로그: `out/tfjs-baseline/`, 수정 후 `out/tfjs-initialization/`.
  실행 명령·바이너리/도구 해시는 각 toxicity 실행의 `metadata.json`에 있다.
  검사 도중 도구의 threshold 검증이 정정되었으므로 아래 설명과 함께 읽는다.
- 테스트 자산: `c287446a858ae76200128f37848e1569fbed267d` (최초 추가
  `785d6576e`와 선택 확장의 드라이버 조건 보완), 테스트 fork
  `jh1984-hwang/web_tc_new`의 `indigo/2025/webgl2/0376`에 push했다.
  본 저장소의 gitlink는 계획대로 갱신하지 않는다.

## 기준선과 발견 사항

원본 demo bundle의 SHA-256은
`02b18cf1dfa88aa263f427d2980b99d744fe2db0985b90ee47e674c2845a35cd`이다.
이 번들은 `load()`를 인자 없이 호출하며 모델 생성자의 기본 threshold는
**0.85**다. 계획의 0.9는 잘못된 가정이었다. 참조 JSON과 검사기를 원본에
맞춰 정정했으며 페이지나 모델의 계산을 바꾸지 않았다.

CPU 기준선은 TFJS 1.2.2, 4문장, 7 labels의 판정 28개가 모두 일치하고
기존 CPU 참조와 최대 확률 절대 오차가 **0.0**이었다. 첫 실행의 `result.json`은
계획에 있던 0.9 검사 때문에 실패로 남겨 보존했다. 동일 payload를 정정된
검사기로 재판정한 결과는 `([], 0.0)` (실패 없음, 오차 0)이다.
CPU 실행은 초기 추론을 observer 주입 전에 마쳐 초기 3문장을 재실행했고,
페이지의 원래 입력 handler로 추가 문장을 분류했다. 총 약 470초는 이 재실행을
포함하므로 순수 추론 성능 수치가 아니다.

| 수정 전 실행 | 결과 |
| --- | --- |
| CPU, llvmpipe 환경 | 28판정 일치, 오차 0.0; threshold 정정 후 재판정 통과 |
| WebGL1, llvmpipe | `getBytesPerPixelWebGL1`에서 `HALF_FLOAT_OES` assertion으로 종료 |
| WebGL1, NVIDIA | 같은 assertion으로 종료 |
| WebGL2, llvmpipe | CPU fallback, GL 실행으로는 실패; 확률 오차 0.0 |
| WebGL2, NVIDIA | CPU fallback, GL 실행으로는 실패; 확률 오차 0.0 |

WebGL1 assertion은 다음 텍스처 구현 단계의 대상이다. CPU fallback의 수치가
맞더라도 GPU 성공으로 계산하지 않는다. 두 WebGL2 결과 파일에는 정정 전
threshold 검사 실패도 포함되어 있으나, 이를 제외해도 CPU fallback 때문에
실패다. 이번 단계에서 toxicity 가속 완료를 주장하지 않는다.

## 초기화 회귀

`webgl-extension-registry.html`은 파싱 중 WebGL1·2 context를 생성하고
검증 드라이버가 제공하는 anisotropic 확장, 반복 조회 및 객체 identity를 검사한다.
native `WebContainerTest.InitializeWebGLExtensionsWithoutCurrentGLContext`는
드라이버의 실제 지원 확장을 선택하고 current context를 비운 뒤 동기 생성한다.
process-wide registry가 미리 채워져 실패를 숨기지 않도록 별도 프로세스에서 실행했다.

| 검사 | llvmpipe 수정 전 → 후 | NVIDIA 수정 전 → 후 |
| --- | --- | --- |
| HTML 동기 생성·반복 생성 | 실패 → 통과 | 실패 → 통과 |
| native current-context 제거 | 실패 → 통과 | 실패 → 통과 |

수정 후 두 드라이버 모두 기존 registry의 확장 8개를 반환한다. 새 확장을
추가한 것이 아니라 기존 지원 목록이 초기화 시점 때문에 사라지던 문제를 고쳤다.
native 테스트는 첫 엔진 변경 전에 추가해 기존 엔진의 실패도 확인했다.

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env \
  LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=4 \
  ./Starfish unit-test \
  --gtest_filter=WebContainerTest.InitializeWebGLExtensionsWithoutCurrentGLContext
```

NVIDIA는 같은 wrapper 안에서 `DISPLAY=:1` 및
`__EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json`을
사용하며 `LIBGL_ALWAYS_SOFTWARE`를 지정하지 않는다.

## 스위트 비교

아래 기준선은 기능 구현 전 엔진으로 측정했다. 내부 테스트는 IDB 테스트의
실패로 첫 `internal.res` 이후 하위 suite 실행을 중단한다. 이를 전체 내부
suite 통과로 보고하지 않는다.

| 검사 | 수정 전 | 수정 후 |
| --- | --- | --- |
| internal.res | 918 통과 / 1 실패 | 919 통과 / 동일한 1 실패 |
| Khronos WebGL1 | 491 / 491 통과 | 491 / 491 통과 |
| Khronos WebGL2 | 57 / 57 통과 | 57 / 57 통과 |
| Khronos SDK | 2 / 2 통과 | 2 / 2 통과 |
| Canvas WPT | 589 / 589 통과 | 전체 재실행 589 / 589 통과 (첫 실행 TIMEOUT 2건은 아래 기록) |
| C++ tidy | 1749 files / 0 errors (native 테스트 추가 포함) | 1749 files / 0 errors |
| 검증 도구 판정 단위 테스트 | 3 / 3 통과 | 동일 도구 |

관련 `WebContainerTest.*` 11개도 수정 후 모두 통과했다.
내부 통과 목록의 증가분은 `canvas/webgl-extension-registry.html` 한 항목이다.
수정 후 WebGL1(llvmpipe) toxicity는 기준선과 동일한 half-float assertion으로
종료했다. 초기화 수정만으로 가속이 완료되지는 않는다.
수정 후 WebGL2(NVIDIA 환경)는 CPU fallback으로 약 459초에 추론을 마쳤고,
28개 판정 일치·최대 확률 오차 0.0이었다. 원본 threshold 0.85 검사도 통과했지만
GL backend가 아니므로 가속 검사 결과는 의도대로 실패다.

Canvas WPT의 첫 수정 후 실행은 587/589 통과, 다음 두 항목의 TIMEOUT이었다.
둘 다 같은 20초 제한의 개별 재실행에서는 통과했다. 두 테스트는 WebGL을
생성하지 않는 2D canvas 검사이므로 변경 경로와 직접 관련이 없어 보이지만,
최초 타임아웃의 원인을 확정하지는 않는다. 같은 8-way·20초 조건의 전체
재실행에서는 589/589가 통과했고 기준선과 결과 집합이 일치했다.
전체 재실행 결과도 `canvas-wpt-repeat.results`와 로그에 보존했다.

- `fill-and-stroke-styles/2d.fillStyle.parse.css-color-4-hsl-9.html`
- `line-styles/2d.line.cap.square.html`

해당 WPT CLI는 실패가 있어도 exit 0을 반환하므로 결과 파일과 summary를
직접 판정했다. 실패 목록을 삭제하거나 타임아웃을 늘리지 않았다.

내부 기존 실패는 `idb/idb_put_object.html`이며 개발 빌드의 `IDB=0`에서
발생했다. 목록을 숨기거나 빌드 옵션을 바꾸지 않고 전후 비교한다.

WPT는 호스트에 `web-platform.test` 매핑이 없어 처음에는 서버 시작에 실패했다.
시스템 `/etc/hosts`를 수정하지 않고 공식 `wpt make-hosts-file` 출력과 기존
hosts를 합친 `out/tfjs-baseline/wpt-hosts`를 생성했다. `bwrap`으로 테스트
프로세스에만 이 파일을 읽기 전용 bind하여 기준선과 수정 후를 실행한다.
WPT 기준선을 위해 두 engine source 파일을 원래 내용으로 일시 복원하고
재빌드한 뒤 측정하고, 초기화 수정을 다시 적용했다.

```sh
bwrap --bind / / --dev-bind /dev /dev \
  --ro-bind "$PWD/out/tfjs-baseline/wpt-hosts" /etc/hosts \
  xvfb-run -s '-screen 0 1920x1080x24' -a env \
  LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=4 \
  python3 tool/wpt/scripts/wpt_runner.py tool/wpt/testharness_lists/2dcontext.res \
  --wpt-root "$PWD/third_party/wpt" -j8 --timeout 20 \
  --results out/tfjs-baseline/suites/canvas-wpt.results
```

이 환경에는 `python` 명령이 없어 tidy는 `python3 tool/lint/check_tidy.py
--clang-format /usr/bin/clang-format`으로 실행한다.

## 남은 범위

최종 8조합 검증, GLib·Release 검증 및 `0377` 통합 검증은 아직 수행하지 않았다.
이번 실행은 `uv_cairo_gl` Debug의 기준선 및 초기화 수정 검증이다.
float 관련 전체 확장 규격의 잔여 제약은 계획 문서에 기록된 그대로 남는다.
