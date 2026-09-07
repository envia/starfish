# Quick Reference (code2spec)

> **코드 수정 전 반드시 확인.** 시스템 아키텍처 일관성 유지 필수.
> 이 파일은 `code2spec-finalize` 단계에서 생성된 통합 진입점입니다.

## 시스템 개요
- **목적:** Lightweight Web Engine (Starfish) - C++11 기반의 모바일 및 임베디드 웹 렌더링 엔진.
- **아키텍처 패턴:** 다계층 마이크로 컴포넌트 아키텍처 (Rendering, Script Bindings, Platform Window Managers 분리).
- **기술 스택:** C++11, Escargot JS, Cairo 2D, cURL, libuv/glib (이벤트 루프).

### 주요 설계 결정
1. JavaScript 실행과 DOM 접근 간 브릿지(ScriptWrappable)를 통한 Memory/GC 효율화.
2. 다양한 운영체제 및 플랫폼(Android, Tizen, Flutter, Windows)를 지원하기 위한 추상화 계층(Abstract Interface) 구축.
3. cURL 기반의 멀티 스레드 캐싱 및 다운로드 관리 최적화.

## 핵심 모듈 위치

| 모듈 | 파일 | 역할 |
|---|---|---|
| `compat-tizen` | `compat/tizen_5.0/inc/LWEWebView.h` | Tizen 5.0 호환 계층 및 헤더 |
| `engine-core` | `src/Starfish.h`, `src/Starfish.cpp` | Starfish 엔진 코어 초기화 및 시스템 구성 |
| `bindings` | `src/binding/ScriptBindingInstance.cpp` | 웹 DOM 요소와 JavaScript (Escargot) 컨텍스트 바인딩 |
| `platform-canvas` | `src/platform/canvas/CompositorGL.cpp` | Cairo, WebGL, EGL을 활용한 캔버스 그래픽 가속 및 드로잉 |
| `platform-network` | `src/platform/network/curl/...` | HTTP 프로토콜 관리 및 리소스 다운로드 스레딩 |
| `public-bridge` | `src/public/bridge/android/AndroidBridge.cpp` 등 | Android, Flutter, Tizen 애플리케이션 임베딩 브릿지 |
| `shell` | `src/shell/MiniBrowser.cpp` | 테스트 러너와 디버깅을 위한 미니브라우저 셸 구현 |

> 자세한 내용은 `modules/README.md`에서 각 카드를 참조하십시오.

## 아키텍처 원칙
1. **Thread Affinement**: 플랫폼의 주 이벤트 루프를 따르며, DOM API의 호출은 Main Thread로 격리.
2. **Zero Inference**: JavaScript 바인딩의 타입 변환과 예외 관리는 명시적이고 안전하게 선언.
3. **Decoupling**: 운영체제별 의존성 코드는 `public-bridge` 내에서 분리되어야 함.

## 코드 수정 전 확인 순서
1. 본 Quick Reference에서 관련 논리 모듈을 파악합니다.
2. 변경할 대상 모듈의 **Module Design Card** (`modules/<name>.md`)를 읽고 부작용(Side Effects)을 파악합니다.
3. `02-architecture.md`를 통해 레이어 의존성 위반 여부를 확인합니다.
4. `09-ipc-enum-catalog.md`에서 사용하는 에러 코드 및 통신 시그널이 정확하게 명명되었는지 확인합니다.
