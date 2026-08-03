# TODO — Bixby Selection Prompt 레이아웃 디버깅 (issue #4925)

대상: `http://10.113.113.207:8777/weather2.html` (tc=weather2, 위치 권한 PermissionPrompt)
작업 브랜치: `claude/2026/bixby/0001`

## 완료

- [x] **flex 버튼 겹침 + 과도한 간격 버그 수정** — 커밋 `d80a840af`
  - 원인 1 (겹침): `flex-basis:0` 아이템이 indefinite main-size(auto-height column) 컨테이너에서
    0으로 collapse. CSS Flexbox §4.5 automatic minimum size(min-content) 미적용.
  - 원인 2 (간격): content size suggestion 측정 시 stretch 아이템의 definite cross size를
    반영하지 않아 fit-content(좁은 폭)로 측정 → 텍스트 wrap → 높이 과대 → grow로 균등 분배.
  - 수정: `FrameFlexibleBox::automaticMinimumMainSize()` 추가 + `computeMainSize()`에서
    indefinite main-size일 때 floor. stretch면 definite cross size로 측정.
  - 검증: Firefox(http 원본)와 동일하게 컴팩트 렌더 확인.

## 진행 중 / 막힘

- [ ] **self-contained 재현 파일** (정적 DOM 스냅샷 방식)
  - 생성됨: `/tmp/sc/weather2_selfcontained_static.html` (40KB, 단일 파일)
    - 렌더된 최종 DOM + renderer CSS 인라인, script/MutationObserver 제거, 외부 의존 0
  - **문제: Starfish `file://`에서 검은 화면(카드/버튼 안 보임).** 원인 조사 필요.
    - 후보 (a): renderer CSS가 초기 `opacity:0`/`visibility:hidden`이고 fade-in을 JS가
      수행 → script 제거로 hidden 유지? → 정적화 시 visible 상태로 강제 필요.
    - 후보 (b): `data:` iframe이 Starfish `file://`에서 미로드.
    - 후보 (c): device-frame `fit()` 스크립트/iframe 스케일 문제.
  - 추출 파이프라인은 동작 확인됨(로컬 http 서버 + fetch POST로 Firefox에서 최종 DOM 추출).
  - 저장 위치 미정 (`test/`는 submodule이라 제외 — `test_manual/flexbox/` 또는 `regression/` 후보).

## 대기 (남은 일)

- [ ] **회귀 검증**: flexbox 관련 WPT 서브셋 실행 (flex 코어를 건드렸으므로).
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
          max-content(width 고정 시 height는 단일 값)라 결과 동일하지만, row(inline main)에선
          min-content ≠ max-content라 부정확.
          - **①의 선결조건**: 현재 범위(column·indefinite)에서는 결과에 영향 없음. 하지만 ①로
            적용 범위를 row(inline main) / definite로 넓히는 순간 max-content가 노출되어 automatic
            minimum size가 과대 계산됨. 따라서 **① 확장 전에 (2d)를 반드시 함께 처리**해야 함.
- [ ] **별개 버그 기록**: `file://`/`data:` 로컬 로드 시 MutationObserver microtask crash.
  - `Assertion 'instance->engineInstance()->macroTaskCounter()' failed` @ `ScriptWrappable.cpp:2197`
  - 경로: `HTMLConstructionSite::flush → parserAppendChild → MutationObserver::enqueueMutationRecord → enqueueMicrotask`
  - http 로드는 정상(매크로태스크 안 파싱), 로컬 동기 로드만 crash. flex 수정과 무관.

## 환경 메모

- Starfish를 background/`nohup`으로 띄우면 이 세션에서 불안정(로그 0바이트, 즉시 종료) → 자동 검증 어려움.
  사용자가 `! DISPLAY=:1 ./Starfish <url>` 로 직접 실행하는 게 안정적.
- Firefox는 안정적 (`http://`/`file://` 모두). 단 레이아웃 버그가 없으므로 회귀 검증용은 아님(ground truth/추출용).
- 입력 자동화: `/tmp/sfvenv` (python-xlib, XTEST) 사용 가능.
