# Starfish 개발 도구 인벤토리

Starfish(lightweight-web-engine) 레포 및 서브모듈 개발 환경에서 사용되는 개발 도구 목록.
레포는 CMake+Ninja 기반 C++ 웹엔진으로 Linux·Tizen·Windows·Android 4개 플랫폼을 지원하며,
테스트는 WPT/픽셀테스트 중심, CI는 사내 GitHub(CODE) Actions + Docker 이미지로 구성된다.

조사 범위: 레포 루트/빌드 스크립트, `.github/workflows/*`(14개), `.gitlab-ci.yml`,
`packaging/*.spec`, `tool/`, `test/`, `docs/`, `binding_generator`, `third_party/escargot`.
(리눅스 기본 도구는 제외. 조사일: 2026-07-10)

## 빌드 시스템 / 패키징

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| CMake | 메인 빌드 설정 도구 (`-G Ninja`로 빌드 스크립트 생성) | `apt install cmake` (CI는 사내 Docker 이미지에 포함) |
| Ninja | 실제 컴파일을 수행하는 빌드 실행기 (`ninja starfish.executable`) | `apt install ninja-build` |
| GNU Make | 구 GitLab CI의 테스트 타깃 실행용 (레거시) | `apt install build-essential` |
| GYP | `build.gyp`→ninja 파일 생성하는 구 메타빌드 (레거시) | `tool/gyp` 서브모듈 (사내 미러) |
| GBS | Tizen RPM 패키지 빌드 도구 (`gbs build -A armv7l`) | Tizen 도구 apt 저장소 (download.tizen.org/tools) |
| MSBuild / Visual Studio 2019·2022 | Windows 포트 빌드 (`.sln`, MSVC 툴체인 포함) | Visual Studio 설치 (CI는 셀프호스트 Windows 러너에 사전 설치) |
| Gradle | Android APK/AAR 빌드 (`build/android/apk`) | gradle 설치 + `ANDROID_HOME` 설정 |
| Docker | 재현 가능한 빌드/크로스빌드 환경 (빌드 이미지 4종) | 사내 레지스트리 `lws-docker-local.bart.sec.samsung.net`에서 pull |
| patchelf | 빌드 산출물의 ELF rpath 수정 | `apt install patchelf` |
| hash-signer / app-signer | Tizen TPK 패키지 서명 | Tizen 빌드환경 BuildRequires (GBS가 자동 설치) |

CI Docker 이미지: `starfish-build:20.04`(GCC/Clang x64), `starfish-build:20.04_python3.9`(WPT),
`starfish-build:gbs`(Tizen RPM), `starfish-cross-build:24.04`(aarch64/arm/x86 크로스 + `/opt/sysroot/*`).

## 컴파일러 / 툴체인

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| GCC/G++ | 기본 네이티브(x64) 컴파일러 | `apt install build-essential` |
| 크로스 GCC 3종 | aarch64(RPi5)/arm32/x86 크로스 빌드 (`aarch64-linux-gnu-gcc` 등) | `apt install gcc-aarch64-linux-gnu …` + sysroot (`/opt/sysroot/*`, `mk-sysroot.sh`) |
| Clang/Clang++ | 대체 컴파일러 빌드 검증 (`x64_test_clang.yml`) | `apt install clang` |
| Android NDK (r16b) | Android용 크로스 툴체인 | Android 개발자 사이트에서 다운로드 |

## 코드 생성

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| binding_generator | WebIDL(`.idl`) → C++ 바인딩 코드 자동 생성기 | 사내 서브모듈 `binding_generator` (의존 wheel 동봉) |
| Jinja2 | 바인딩 생성기의 템플릿 엔진 | `apt install python3-jinja2` 또는 동봉 wheel (`binding_generator/pip_archive/`) |
| PLY (Python Lex-Yacc) | IDL 파서 | binding_generator에 번들됨 |
| js2c.py | JS 소스를 C++ 헤더 문자열로 임베드 (ServiceWorker용) | 레포 내 `tool/js2c.py` (Python 표준lib만 사용) |

## 테스트

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| test_runner.py | 전체 테스트 오케스트레이터 (internal/dom/wpt/reftest/vendor) | 레포 내 `tool/test_runner.py` |
| WPT + wpt CLI | W3C 표준 테스트 스위트, `wpt serve`/`manifest`로 서빙 | `third_party/wpt` 서브모듈 (shallow) + **python3.9** 필요 |
| Google Test | C++ 단위 테스트 프레임워크 (`./Starfish unit-test`) | `third_party/googletest` 서브모듈 |
| imgdiff | 픽셀 비교 도구 — reftest 합격/불합격 판정 | `ninja install_pixel_test_dep`로 인트리 소스 빌드 |
| image_diff (Chromium) | 픽셀테스트 실패 시 시각적 diff PNG 생성 | `test` 서브모듈에 바이너리 커밋됨 (`test/tools/image_diff/`) |
| NW.js | 픽셀테스트 기준(golden) PNG를 뜨는 레퍼런스 렌더러 | v0.31.6 바이너리가 `test` 서브모듈에 동봉 |
| Xvfb | CI에서 GUI 렌더링용 가상 X 서버 (`xvfb-run`) | `apt install xvfb` |
| http_server.py | 테스트/벤치 페이지 로컬 서버 | Python 표준 라이브러리 (레포 내 스크립트) |
| test262 / Octane / SunSpider 등 | Escargot(JS엔진) 컨포먼스·벤치 스위트 | `third_party/escargot/tools/run-tests.py`가 자동 다운로드 |

## 디버깅

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| CDP 서버 + Chrome DevTools/Puppeteer | 엔진 내장 Chrome DevTools Protocol 서버(49개 도메인)로 원격 디버깅·자동화 | 서버는 `-DSTARFISH_ENABLE_CDP=1` 빌드에 내장, 클라이언트는 npm(`puppeteer`, `chrome-remote-interface`) 또는 Chrome |
| Escargot 원격 디버거 | 내장 JS 엔진 디버깅 (기본 포트 6501) | escargot 동봉 `tools/debugger/debugger.py` 또는 [escargot-vscode-extension](https://github.com/Samsung/escargot-vscode-extension) |
| TRACE 매크로 | `TRACE=ID1,ID3` 환경변수로 켜는 엔진 내장 로그/콜그래프 추적 | 레포 내장 (`src/core/util/debug/Trace.h`), 디버그 빌드 기본 활성 |
| API Record & Replay | 공개 API 호출을 JSONL로 기록·재생해 버그 재현 | 레포 내장, `ENABLE_TEST=1` 빌드 + `STARFISH_API_RECORD` 환경변수 |
| StarfishInspector | nanomsg 기반 구 인스펙터 프론트엔드 (NW.js 앱) | `inspector/setup_nwjs.sh` (dl.nwjs.io에서 v0.17.0 wget + `npm install nanomsg-browser`) |
| GDB | 네이티브 디버깅 (레포 전용 스크립트는 없음) | `apt install gdb` |

## 프로파일링 / 메모리 / 커버리지

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| AddressSanitizer | 메모리 오류 검출 (TSAN은 주석 처리 상태) | `-DASAN=1` 빌드 옵션 (컴파일러 내장 `-fsanitize=address`) |
| gcov | 코드 라인 커버리지 측정 | `-DCOVERAGE=1` 빌드 옵션 (GCC 내장; lcov 연동 스크립트는 없음) |
| perf_tools | 인하우스 마이크로벤치 (measure-bench, mse-smoke, style-smoke 등) | 레포 내 `tool/perf_tools/` (Python 서버 + Starfish 바이너리) |
| matplotlib | GC vs RSS 메모리 추이 차트 생성 (`tool/reftest/draw_mem_chart.py`) | `pip install matplotlib` |
| Escargot 힙 시각화 | Boehm GC 힙 사용량 시각화 | escargot 동봉 `tools/visualize_heap_usage.py` |
| 스펙 커버리지 도구 | DOM/CSS 스펙 메서드별 TC 커버리지 표 생성 (`TC=1` 빌드 + Node.js) | 레포 내 `tool/coverage/` (Node.js 필요) |

## 코드 품질

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| clang-format (기본 clang-format-8) | `.clang-format` 스타일 검사 — PR CI 필수 게이트 (`tool/check_tidy.py`) | `apt install clang-format-8` (없으면 `clang-format`으로 폴백) |
| black | 레포 내 Python 도구 스크립트 포맷터 | `pip install black` |

## Tizen 디바이스 / 기타 장비

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| sdb | Tizen 기기/에뮬레이터에 바이너리 push·원격 셸 (reftest, record&replay) | Tizen Studio에 포함 (`$TIZEN_SDK_HOME/tools/`) |
| mic | Tizen 플랫폼 이미지 생성 | Tizen 도구 저장소 (download.tizen.org/tools) |
| qemu-user / binfmt | GBS 크로스 아키텍처 빌드 시 타깃 바이너리 실행 | `apt install qemu-user-static binfmt-support` (GBS Docker 이미지 포함) |
| sd_fusing_rpi3.sh | RPi SD카드에 Tizen 이미지 플래싱 | tizen.org (git.tizen.org u-boot 스크립트)에서 wget |
| minicom (+pv) | RPi 시리얼 콘솔 접속 | `apt install minicom pv` |

## CI 인프라

| 도구 | 설명 | 획득/설치 |
|---|---|---|
| GitHub Actions (사내 CODE) | PR/푸시/나이틀리 CI — 워크플로 14개, 셀프호스트 러너 (code-linux, Windows 등) | github.sec.samsung.net 제공 (CODE-Actions/checkout 등 사내 미러 액션) |
| GitLab CI | 구 파이프라인 (레거시, `.gitlab-ci.yml`) | 자체 GitLab + 러너 이미지 |

## 주의할 점

- `tool/check_tidy.py`는 이름과 달리 **clang-format만** 실행한다 — clang-tidy/cppcheck는 이 레포에서
  사용되지 않는다 (SVACE 정적분석은 `.github/gbs-configuration/` 쪽에만 존재).
- **ccache/icecc, lcov/gcovr는 레포·CI 어디에도 연결돼 있지 않다.**
- WPT 관련 잡(`wpt serve`, 상태 대시보드)은 **python3.9** 인터프리터를 요구한다.
- pip 설치와 서브모듈 fetch는 사내 프록시(`http://10.112.1.184:8080`)를 경유한다.
