# Code2Spec SDD 챕터 구조 (IEEE 1016 Enhanced)

W1(code2spec-discovery) 에서 생성하는 SDD 문서의 목차 구조.
**모든 챕터 필수.** 해당 정보가 없으면 `"코드 내 식별 불가"` 기재.

---

## 필수 챕터 목록

| 파일                             | 챕터            | IEEE 1016 관점    |
| -------------------------------- | --------------- | ----------------- |
| `01-introduction.md`             | 시스템 개요     | Context View      |
| `02-architecture.md`             | 시스템 아키텍처 | Architecture View |
| `03-design-patterns.md`          | 설계 패턴       | Design Patterns   |
| `04-data-layer.md`               | 데이터 계층     | Information View  |
| `05-external-interfaces.md`      | 외부 인터페이스 | Interface View    |
| `06-configuration-deployment.md` | 설정 및 배포    | Deployment View   |
| `07-resources.md`                | 리소스          | Resource View     |
| `08-security-quality.md`         | 보안 및 품질    | Quality View      |
| `09-ipc-enum-catalog.md`         | IPC 상수 및 ENUM 카탈로그 | Interface View |

> `04-core-modules.md` 없음 — W2 에서 `modules/<name>.md` (Module Design Card) 로 분리 생성.

---

## 01-introduction.md — 시스템 개요

```
## 시스템 목적
[코드 및 README 에서 확인된 목적만. Source 필수.]

## 시스템 범위
- 포함: [확인된 기능 목록]
- 제외: [명시적으로 제외된 것]

## 사용자 및 액터 정의
[코드에서 식별된 사용자 유형 / 시스템 액터]
| 액터 | 유형 (사람/시스템) | 역할 | Source |

## 시스템 컨텍스트
[사용자 / 외부 시스템과의 상호작용 흐름]
[code-to-diagram → system-context.mmd]

## 기술 스택
| 레이어 | 기술 | 버전 | 라이선스 | Source |
[dependency-audit + package.json / pyproject.toml 등에서 확인된 것만]

## 문서 개요
[본 SDD 의 각 챕터가 다루는 내용 요약]

## 참조 문서
[코드에서 참조된 외부 문서, API 스펙, 관련 규격 등]
| 문서명 | 유형 | Source |
```

---

## 02-architecture.md — 시스템 아키텍처

```
## 아키텍처 패턴
[코드 구조에서 확인된 패턴: 레이어드 / 이벤트 기반 / 마이크로서비스 등]
[Source 필수]

## 레이어 구조
[ASCII 또는 Mermaid 다이어그램]
[code-to-diagram → architecture.mmd]

## 핵심 컴포넌트 설명
[각 컴포넌트의 책임과 역할 — AST + 디렉토리 구조에서 확인]
| 컴포넌트 | 책임 | 주요 진입점 | Source |
|---|---|---|---|
| MCPServer | 요청 라우팅 | `start()` | [`MCPServer`](src:src/MCPServer.ts#L46) |   <!-- Source = 심볼+라인 deep-link (파일 단위 아님) -->

## 컴포넌트 간 의존성 방향
[AST IMPORTS_FROM 엣지 기반]

## 컴포넌트 간 인터페이스
[컴포넌트 간에 주고받는 데이터/이벤트 — AST 함수 시그니처 및 호출 그래프 기반]
| 송신 컴포넌트 | 수신 컴포넌트 | 인터페이스 (함수/이벤트) | 데이터 | Source |
|---|---|---|---|---|
| ToolManager | MCPServer | `registerTool(name, handler)` | ToolSpec | [`registerTool`](src:src/ToolManager.ts#L23) |
```

---

## 03-design-patterns.md — 설계 패턴

```
## 설계 원칙
[코드에서 관찰 가능한 설계 원칙: DRY, SRP, SoC 등 — 코드 구조에서 추론 가능한 것만. Source 필수.]

## 모듈화 방식
[레이어 분리 방식, 디렉토리 구조 기반 모듈 경계]

## 주요 설계 패턴
[AST + 코드에서 확인된 패턴: Repository, Factory, Observer 등]
| 패턴명 | 적용 위치 | 구현 방식 | Source |

## 의존성 관리 방식
[DI 컨테이너, 모듈 임포트 전략 등 — 코드에서 확인된 것만]

## 명명 규칙
[코드에서 관찰되는 네이밍 컨벤션]
| 대상 | 규칙 | 예시 | Source |
[파일명, 클래스명, 함수명, 변수명, 상수명 등]

## 상속·구조 패턴
[클래스 계층, Mixin, Composition — AST 에서 추출]
| 패턴 유형 | 관련 클래스/모듈 | Source |

## 에러 처리 패턴
[커스텀 예외 계층, 에러 전파 방식, 복구 전략 — AST + 코드에서 확인]
| 예외 타입 | 발생 위치 | 처리 방식 | Source |
```

---

## 04-data-layer.md — 데이터 계층

```
## 데이터 저장소
[DB 종류, ORM, 연결 방식 — dependency-audit + 설정 파일]

## 핵심 데이터 모델
[AST 에서 추출된 타입/인터페이스/스키마]
[code-to-diagram → er-diagram.mmd]

## 데이터 액세스 패턴
[Repository 패턴, 쿼리 방식 등 — 코드 직접 확인]

## 데이터 무결성 규칙
[validation 로직, constraints — 코드 확인된 것만]
```

---

## 05-external-interfaces.md — 외부 인터페이스

```
## API 엔드포인트
[라우트 데코레이터 / 핸들러에서 추출된 엔드포인트 목록]
| Method | Path | 설명 | Source |

## API 통신 규격
[HTTP/REST/WebSocket — fetch/axios/http 패턴에서 확인]

## 외부 서비스 연동
| 서비스 | 연동 방법 | 인증 | Source |
[dependency-audit + 코드 직접 확인]

## 인터페이스별 에러 처리
[try/catch 패턴, 에러 타입 — 코드 확인]
```

---

## 06-configuration-deployment.md — 설정 및 배포

```
## 런타임 환경
[실행에 필요한 런타임 요구사항]
| 항목 | 요구사항 | Source |
[Python 버전, Node 버전, 시스템 패키지 등 — pyproject.toml/Dockerfile 에서]

## 환경변수
[.env.example, process.env 사용처 — 코드 직접 확인]
| 변수명 | 용도 | 필수 여부 | Source |

## 빌드 파이프라인
[package.json scripts, Dockerfile, CI 파일에서 확인]

## 인프라 구조
[docker-compose, k8s 파일 등에서 확인. 없으면 "코드 내 식별 불가"]
```

---

## 07-resources.md — 리소스

```
## 정적 에셋 구조
[public/, assets/ 디렉토리 구조]

## 파일 I/O 패턴
[코드에서 확인되는 파일 읽기/쓰기 경로 및 패턴]
| 경로 | 용도 | 읽기/쓰기 | Source |

## 다국어/i18n
[i18n 라이브러리, 언어 파일 위치 — 없으면 "해당 없음"]

## 디자인 시스템
[공통 UI 컴포넌트, 테마 파일 — 없으면 "해당 없음"]
```

> 해당 개념이 없으면 섹션에 `"해당 없음"` 기재 후 진행.

---

## 08-security-quality.md — 보안 및 품질

```
## 보안 아키텍처
[인증 방식, XSS/CSRF 방어 — 미들웨어·인증 코드에서 확인]

## 사용자 인증 및 권한
[RBAC, 토큰 처리 방식 — 코드 직접 확인]

## 에러 핸들링 전략
[전역 에러 핸들러 패턴 — 코드 확인]

## 테스트 전략
[테스트 프레임워크, 커버리지 설정, 테스트 구조 — 설정 파일 + 테스트 코드에서 확인]
| 항목 | 내용 | Source |

## 코드 품질 도구
[linter, formatter, type checker 등 — 설정 파일에서 확인]
| 도구 | 용도 | 설정 파일 | Source |

## 로깅 및 모니터링
[logger 사용 방식, 모니터링 도구 — 코드/설정 확인]

## 성능 목표
[코드에서 확인된 캐싱·최적화 전략. 없으면 "코드 내 식별 불가"]
```

---

## 09-ipc-enum-catalog.md — IPC 상수 및 ENUM 카탈로그

> 이 챕터는 `.ipc_enum_template.md` 템플릿 구조를 그대로 사용합니다.
> 상세 테이블 구조는 `.ipc_enum_template.md`를 참조하세요.

> IPC 메커니즘 값은 IpcMechanism enum 에서 필수: socket, grpc, message_queue, pipe, shared_memory, signal, broadcast_receiver, binder, dbus, named_pipe, wcf, rmi, xpc, http_client, subprocess

> **Zero-Inference + deep-link 준수**:
> - **본문·표의 `Source` 열은 심볼+라인 deep-link** ``[`Sym`](src:path#L<n>)``를 쓴다 — 코드 심볼(함수·클래스·상수·enum·엔드포인트 핸들러 등)을 가리키는 인용은 **반드시 `#L<라인>`까지** 붙인다(라인은 `.ast/api.json`에서 가져오고, host 접두사는 렌더 시 `repo.json.deepLink.base`가 붙는다). 파일만 가리키는 링크(라인 없음)로 때우지 않는다 — 그래야 grounding이 라인 정합을 검증한다.
> - **파일 단위 링크(라인 없음)는 H1 아래 `> **Relevant source files**` 블록에만** 쓴다(페이지 scope).
> - 심볼이 없는 순수 파일/문서 참조(예: 스펙 문서·매니페스트)만 예외적으로 파일 단위 링크 허용.
> - 코드에서 값을 결정할 수 없으면 "코드에서 확인 불가". (상세: `code2spec-doc-generation` 스킬의 grounding-and-deep-links.md)

---

## 코딩 시 참조 지침

새 기능 추가·코드 수정 시 `code2spec/code2spec-quick-reference.md`를 참조하세요.
코드 수정 전 확인 순서가 포함된 통합 참조서입니다.
