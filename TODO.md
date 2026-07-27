# TODO — Bixby Selection Prompt 레이아웃 디버깅 (issue #4925)

대상: `http://10.113.113.207:8777/weather2.html` (tc=weather2, 위치 권한 PermissionPrompt)
작업 브랜치: `claude/2026/bixby/0003`

## 현재 상태 (다음 주 재개용)

- 브랜치: `claude/2026/bixby/0003` (체크아웃됨)
- 로컬 커밋:
  - `5fc8b9e86 Add flexbox auto-min-size regression test`  ← **로컬만, push 안 함**
  - `d80a840af Apply automatic minimum size to flex items`  ← remote와 동일
- remote `origin`(fork `jh1984-hwang/starfish`): `0001`·`0003` 둘 다 `d80a840af`로 push됨.
  `5fc8b9e86`는 돌고 있던 CI 재실행을 피하려 push 보류. **PR 미생성**(올리면 CI가 회귀 검증).
- 미커밋/untracked: `Makefile`(staged, 내가 만든 것 아님), `TODO.md`, `test_manual/flexbox/_wip/`(보존용).
- 빌드: `out/webgl2` (uv_cairo_gl, WEBGL, 수정 포함). reftest용 `glib_cairo_gl`은 EFL 없어 불가.
- 도구: `tool/imgdiff/imgdiff` 빌드됨, `/tmp/sfvenv`(python-xlib/XTEST).

## 완료

- [x] **self-contained minimal 재현 테스트** — 커밋 `5fc8b9e86`
  - `test_manual/flexbox/flex-auto-min-size.html` (정적, JS 없음 → file:// crash 없음).
  - 핵심 구조만: auto-height column flex + `flex:1 1 0` + `align-self:stretch` wrapper + 텍스트.
  - 시각 확인됨(버튼 3개 정상 쌓임). reference 블록 포함.

- [x] **flex 버튼 겹침 + 과도한 간격 버그 수정** — 커밋 `d80a840af`
  - 원인 1 (겹침): `flex-basis:0` 아이템이 indefinite main-size(auto-height column) 컨테이너에서
    0으로 collapse. CSS Flexbox §4.5 automatic minimum size(min-content) 미적용.
  - 원인 2 (간격): content size suggestion 측정 시 stretch 아이템의 definite cross size를
    반영하지 않아 fit-content(좁은 폭)로 측정 → 텍스트 wrap → 높이 과대 → grow로 균등 분배.
  - 수정: `FrameFlexibleBox::automaticMinimumMainSize()` 추가 + `computeMainSize()`에서
    indefinite main-size일 때 floor. stretch면 definite cross size로 측정.
  - 검증: Firefox(http 원본)와 동일하게 컴팩트 렌더 확인.

## 진행 중 / 막힘

- [ ] **full self-contained 재현 파일 (원본 weather2 충실)** — 미완. 두 접근 모두 막힘.
  - 작업 파일은 `test_manual/flexbox/_wip/` 에 보존됨 (untracked, /tmp 휘발 대비 복사).

  - **접근 A — 정적 DOM 스냅샷** (`<script>` 전부 제거): `_wip/weather2_selfcontained_static.html`
    - file:// crash는 없으나 **검은 화면**(카드/버튼 안 보임).
    - 가장 유력 원인: renderer가 초기 `opacity:0`/`visibility:hidden` 상태이고 visible 전환을
      JS(애니메이션)가 하는데 script를 제거해서 hidden 유지 → 정적화 시 visible 강제 필요.
    - 다른 후보: device-frame `fit()` 스크립트/스케일, data: iframe 미로드.

  - **접근 B — 동적** (시나리오·fetch 인라인, VivRenderer 실제 동작): `_wip/renderer_inlined.html`,
    `_wip/weather2_local.html`
    - file://에서 **MutationObserver microtask crash** (= 아래 "별개 버그" 항목).
    - 회피 시도: iframe을 `setTimeout`(매크로태스크)에서 지연 로드 → `_wip/weather2_deferred.html`
      → **"잘 안 됨"(미해결)**. iframe 파싱이 여전히 task 밖에서 동기 처리되는 듯.
    - **다음 시도 후보**:
      - iframe을 `document.createElement('iframe')`로 JS 생성 후 append (task 컨텍스트)
      - renderer 내부 React 부트스트랩을 `setTimeout`으로 감싸 MutationObserver 등록을 파싱 이후로
      - 또는 근본 해결 = 아래 "별개 버그"(엔진에서 file:// crash 수정)부터

  - **추출/조립 재생성 방법** (원본 서버나 /tmp 입력이 없을 때, `_wip/`에 스크립트 보존):
    1. `cd test_manual/flexbox/_wip && python3 server.py`  (GET 서빙 + POST `/dump` 저장, :8899)
    2. Firefox로 `http://127.0.0.1:8899/weather2_dump.html` → 9초 후 최종 DOM이 `dump.html`로 POST됨
       (원본 `http://10.113.113.207:8777` 가 살아있으면 거기서 직접 추출도 가능)
    3. `python3 build_selfcontained.py` 로 renderer(`renderer.html`) + 시나리오
       (`tc_init.txt`/`tc_weather2.txt`) 조립
  - **검증**: harness Bash에서 Starfish GUI가 안 뜸 → `! DISPLAY=:1 ./Starfish file://...` 직접.

## 대기 (남은 일)

- [~] **회귀 검증**: 로컬 자동 reftest는 환경 제약으로 **보류 → CI(`test_reftest_all`)에 위임**.
  - 로컬이 막힌 이유 (모든 백엔드 경로):
    - `glib_cairo_gl`: EFL(elementary/ecore/...) 패키지 없음 — CI는 docker에서 보유.
    - `glib_headless`: screenshot이 stub (`RendererHeadless.cpp` `STARFISH_UNSUPPORTED`).
    - `uv_cairo_gl`(현 `out/webgl2`): `--hide-window` offscreen 캡처가 png를 안 만듦
      (실제 X `:1` · `xvfb-run` 둘 다 실패, onload/GL 캡처 트리거 미동작 추정).
  - CI(`.github/workflows/x64_test.yml`의 `test_reftest_all`)가 docker+xvfb로 flexbox 포함
    reftest(blink_css3 등) 수행 → **PR 올리면 자동 회귀 검증**됨.
  - `tool/imgdiff/imgdiff`는 로컬 빌드 완료(직접 `g++ -lpng`). pixel reftest 파이프라인 자체는
    `./tool/test_runner.py wpt_css_flexbox` / `vendor_pixel ... blink_css3.res cairo` 로 동작
    (screenshot 가능한 백엔드만 갖춰지면).
- [ ] **스펙 완전성 — CSS Flexbox §4.5 automatic minimum size 완전 구현** (이번 버그 범위 밖)

  현재 구현: `computeMainSize()`에서 `m_availableMainSize == intMaxForLayoutUnit`(indefinite)
  일 때만 `automaticMinimumMainSize()`로 floor. 이 헬퍼는 content size suggestion 하나만 계산.

  - **① 적용 범위: indefinite → definite main-size 포함**
    - [ ] definite main-size 컨테이너에서도 적용 (현재 미적용 → `flex-shrink`로 content보다
          작게 줄어들 수 있음, 스펙 위반).
    - [ ] 단순 게이트 해제로는 부족 — definite에서는 `resolveFlexibleLengths`의 grow/shrink가
          `computeMainSize`의 floor를 덮어씀. automatic minimum size를 **flex item의 used min
          main size(= clamp 단계의 하한)로 주입**해야 함 (구조 변경). 현재
          `setContentHeightConsideringMinMaxHeights`는 CSS min/max만 적용, min:auto면 하한 없음.

  - **② automatic minimum size 공식 완성** (현재 content size suggestion 하나만)
    - 스펙: `min(content size suggestion, specified size suggestion, transferred size suggestion)`
      → **max main size로 clamp**
    - [ ] (2a) **max main-size clamp** — content suggestion이 `max-height/max-width`보다 크면 clamp.
    - [ ] (2b) **specified size suggestion** — definite preferred main size(`height:120px` 등)가
          있으면 `min(content, specified)`.
    - [ ] (2c) **transferred size suggestion** — aspect-ratio + definite cross size일 때 cross를
          비율로 변환한 main size (replaced / `aspect-ratio`).
    - [ ] (2d) **content size suggestion 자체** — 스펙은 **min-content** size인데 현재
          `basisSize(Content)` 경로라 사실상 **max-content**. column(block main)에선 min-content =
          max-content라 결과 동일하지만, row(inline main)에선 min-content ≠ max-content라 부정확.
          - **①의 선결조건**: 현재 범위(column·indefinite)에서는 결과에 영향 없음. 하지만 ①로
            적용 범위를 row(inline main) / definite로 넓히는 순간 max-content가 노출되어 automatic
            minimum size가 과대 계산됨. 따라서 **① 확장 전에 (2d)를 반드시 함께 처리**해야 함.

          - **배경: min-content vs max-content, 그리고 width/height 비대칭**
            - max-content width = 콘텐츠를 **줄바꿈 없이** 펼쳤을 때의 너비("원하는 만큼 넓게").
            - min-content width = 가능한 **모든 줄바꿈 기회를 다 사용**했을 때의 너비("더는 못 줄임").
            - 둘이 다른 경우: 줄바꿈 기회가 있는 콘텐츠. 예) `Hello wonderful world` →
              max-content는 한 줄 전체, min-content는 가장 긴 단어 `wonderful` 폭.
              둘이 같은 경우: 단어 하나, `white-space:nowrap`, 고정폭 요소 등.
            - **비대칭의 근원**: height는 width의 함수(width를 정하면 줄 수 → height가 단일 값으로
              결정)지만, width는 height의 함수가 아님(줄바꿈 정도에 따라 min~max 범위). 그래서
                - column(main=height): width 고정 → height 단일 → min-content = max-content. 무해.
                - row(main=width): width 자체가 본질적으로 범위 → min-content ≠ max-content. 부정확.
            - 이번 디버깅의 33.5px가 실제 사례: 한글(CJK)은 글자 단위 줄바꿈이 허용돼 min-content가
              거의 한 글자 폭까지 줄어듦. 측정 시 wrapper 폭이 이 값으로 떨어져 텍스트가 세로로
              쌓이며 높이가 76/90/132px로 부풀었음(겹침→간격 버그). 단 그건 cross size(입력) 문제로
              이미 수정됨. (2d)는 그와 별개로, row에서 suggestion(=main=width) 자체를 min-content로
              구해야 한다는 이야기.
          - **수정 전 / 현재 / 스펙 (3단계)**
            - 수정 전: automatic minimum 자체가 없음 → min:auto를 0으로 취급 → flex-basis:0이 0으로
              붕괴(겹침 버그의 원인). 측정 자체가 없었음.
            - 현재: indefinite main일 때만 적용, suggestion = max-content (column은 정확, row는 부정확).
            - 스펙: 항상 적용 + suggestion = **min-content** + (2a)/(2b)/(2c).
          - **구현 부담**: row에서 min-content width를 산출하려면 min intrinsic / preferred minimum
            width 측정 경로가 필요. Starfish에 그 메커니즘이 있는지 확인이 선행돼야 함.
            (cross=height 고정은 width의 min-content에 거의 무관 — row에선 핵심이 아님.)
- [ ] **별개 버그 기록**: `file://`/`data:` 로컬 로드 시 MutationObserver microtask crash.
  - `Assertion 'instance->engineInstance()->macroTaskCounter()' failed` @ `ScriptWrappable.cpp:2197`
  - 경로: `HTMLConstructionSite::flush → parserAppendChild → MutationObserver::enqueueMutationRecord → enqueueMicrotask`
  - http 로드는 정상(매크로태스크 안 파싱), 로컬 동기 로드만 crash. flex 수정과 무관.

## 환경 메모

- Starfish를 background/`nohup`으로 띄우면 이 세션에서 불안정(로그 0바이트, 즉시 종료) → 자동 검증 어려움.
  사용자가 `! DISPLAY=:1 ./Starfish <url>` 로 직접 실행하는 게 안정적.
- Firefox는 안정적 (`http://`/`file://` 모두). 단 레이아웃 버그가 없으므로 회귀 검증용은 아님(ground truth/추출용).
- 입력 자동화: `/tmp/sfvenv` (python-xlib, XTEST) 사용 가능.
