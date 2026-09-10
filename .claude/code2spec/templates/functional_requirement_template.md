# Functional Requirements: <ModuleName>

> **Relevant source files**
>
> - [path/to/file.ts](src:path/to/file.ts)

<!-- H1 바로 아래에 'Relevant source files' blockquote 블록을 둔다(모든 .md 필수, wikiStructure 검증). -->
<!-- 인용은 code2spec deep-link 규율을 따른다: 코드 심볼은 백틱 deep-link [`Sym`](src:path#L<n>) 로, -->
<!-- 라인은 .ast/api.json 에서 가져온다. host 접두사는 적지 않는다 — 렌더 시 repo.json.deepLink.base 가 붙는다. -->

**모듈**: [`file.ts`](src:path/to/file.ts)   <!-- 파일 포인터(라인 없음) -->
**버전**: YYYY-MM-DD
**연결 Design Card**: [modules/<name>.md](../modules/<name>.md)

---

## Overview

<!-- 이 모듈이 제공하는 기능의 목적과 범위를 1-3 문장으로 기술. 각 사실 문장에 deep-link 출처를 붙인다. -->
<!-- 라벨은 반드시 백틱 코드 인용: 심볼이 있으면 [`Symbol`], 없으면 [`file.ext`]. [출처] 같은 백틱 없는 라벨은 검증에서 스킵된다. -->
이 모듈은 [`Symbol`](src:path/to/file.ts#L<n>) 를 통해 …를 제공한다.

---

## Functional Requirements

### FR-001: <기능명>

| 항목            | 내용                                    |
| --------------- | --------------------------------------- |
| **설명**        | 기능에 대한 명확한 설명 (WHAT, not HOW) |
| **입력**        | 입력 데이터/파라미터                    |
| **출력**        | 반환값/부작용                           |
| **전제 조건**   | 이 기능이 동작하기 위한 조건            |
| **후처리 조건** | 기능 완료 후 보장되는 상태              |
| **출처**        | [`symbol`](src:path/to/file.ts#L10) |

**수락 기준**:

- [ ] 조건 1
- [ ] 조건 2

---

### FR-002: <기능명>

| 항목            | 내용                                      |
| --------------- | ----------------------------------------- |
| **설명**        |                                           |
| **입력**        |                                           |
| **출력**        |                                           |
| **전제 조건**   |                                           |
| **후처리 조건** |                                           |
| **출처**        | [`symbol`](src:path/to/file.ts#L40) |

**수락 기준**:

- [ ] 조건 1

---

## Non-Functional Requirements

| 항목      | 요구사항 | 출처                                        |
| --------- | -------- | ------------------------------------------- |
| 성능      |          | [`symbol`](src:path/to/file.ts#L##)   |
| 보안      |          | [`symbol`](src:path/to/file.ts#L##)   |
| 에러 처리 |          | [`symbol`](src:path/to/file.ts#L##)   |

---

## Constraints

<!-- 코드에서 식별된 제약사항. 없으면 "코드에서 확인 불가" -->

---

## Module Design Card Linkage

| FR     | 구현 위치                                    | Design Card 섹션 |
| ------ | -------------------------------------------- | ---------------- |
| FR-001 | [`file.ts`](src:path/to/file.ts#L10)   | Key Flow         |
| FR-002 | [`file.ts`](src:path/to/file.ts#L40)   | Public Interface |

---

## LLM Extraction Data Reference (Optional)

<!-- LLM 추출 결과를 FR 에 반영할 때 사용. Source 열은 백틱 deep-link [`Sym`](src:path#L<n>) 로. -->

### ENUM Definitions (from llm-enum-results.json)
<!-- 모듈 소스 파일에서 추출된 ENUM 정의 -->
| ENUM 이름 | 값 | Source |
|-----------|-----|--------|

### Error Code Definitions (from llm-constant-results.json where type="error_code")
<!-- 모듈에서 사용되는 에러 코드 상수 -->
| 에러 코드 | 값 | Source |
|-----------|-----|--------|

### Constant Definitions (from llm-constant-results.json, excluding error_code)
<!-- 모듈에서 사용되는 프로토콜/설정 상수 -->
| 상수명 | 값 | 용도 | Source |
|--------|-----|------|--------|

### IPC Dependencies (from llm-ipc-results.json)
<!-- 모듈이 사용하는 IPC 메커니즘 -->
| IPC 메커니즘 | 소스 | 타겟 | 데이터 | Source |
|-------------|------|------|--------|--------|

### Message Protocol (from llm-ipc-results.json message_ids)
<!-- 모듈이 사용하는 메시지 ID/프로토콜 -->
| 메시지 ID | 값 | 방향 | 페이로드 | 핸들러 | Source |
|-----------|-----|------|---------|--------|--------|

### Signal/Event Mappings (from llm-ipc-results.json signal_events)
<!-- 모듈이 사용하는 신호/이벤트 -->
| 신호/이벤트 | 이미터 | 리스너 | 데이터 타입 | Source |
|------------|--------|--------|------------|--------|
