---
name: code2spec-functional-requirement
metadata:
  code-skills:
    id: code2spec/code2spec-functional-requirement
description: "코드베이스에서 기능 요구사항을 추출하여 모듈별 functional-requirement.md 파일 생성. AST in-degree 기반 핵심 모듈 우선 처리. Zero-Inference 원칙 준수."
---

# Skill: Functional Requirement Extraction

> **실행 시점 — W2 전용.** 이 스킬은 **W2(`code2spec-modules`)에서만** 실행한다. W1(discovery)은
> `functional-requirements/` 디렉토리·`index.md`·개별 `<module>-fr.md`를 **일절 생성하지 않는다**.
> 디렉토리 생성 → 개별 FR 문서 → **`functional-requirements/index.md` 인덱스**까지 전부 W2 소관이다.
> (W1에서 이 스킬을 호출하지 말 것 — 인덱스만 만들려다 모듈별 FR을 과생성하는 원인이 된다.)

## Objective

코드에서 직접 확인되는 기능만 추출하여 템플릿 구조로 모듈별 FR 문서를 생성한다.

추측/유추 절대 금지. 모든 항목에 출처 필수.

**모든 외부 소스 인용은 백틱 deep-link ``[`Sym`](src:path#L<n>)`` 로 한다.**
인용할 심볼이 없으면 백틱 **파일명** 라벨 ``[`file.ext`](src:path#L<n>)``를 쓴다 —
**`[출처]`처럼 백틱 없는 라벨은 금지**(검증기가 스킵하므로 틀린 라인이 그대로 남는다).
라인은 `.ast/api.json`에서 가져온다. host 접두사는 적지 않는다 — 렌더 시
`repo.json.deepLink.base`가 붙는다(이슈 #54). 문서 H1 바로 아래에 `> **Relevant source files**`
블록을 둔다. 상세는 [code2spec-doc-generation/references/grounding-and-deep-links.md](../code2spec-doc-generation/references/grounding-and-deep-links.md).
이로써 FR 트리도 시스템 챕터와 동일한 deep-link 검증 파이프라인으로 검증된다.

## 도구 경로

```bash
TOOL_DIR=".code2spec-tools"
```

---

## Step 1: 모듈 우선순위 결정

`<output-dir>/.analysis/analysis-notes/module-priority.md` 읽기 (ast_analyzer.py 결과):
- **Core modules** (in-degree 상위 20%): 우선 처리
- **Peripheral modules**: 이후 처리

```bash
PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
${PYTHON} .code2spec-tools/code2spec_progress.py init \
  --modules-file "<output-dir>/.analysis/analysis-notes/module-priority.md" \
  --output-dir "<output-dir>/.analysis"
```

---

## Step 2: 청크 단위 FR 생성 (10 개씩)

```bash
PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
${PYTHON} .code2spec-tools/code2spec_progress.py next-chunk --output-dir "<output-dir>/.analysis"
```

위 명령으로 다음 10 개 모듈 목록 확인 후, **각 모듈에 대해** 아래 수행:

### 2-1. 파일 분석

1. 소스 파일 Read
2. `<output-dir>/.analysis/cache/code-to-ast/graph-raw.md`에서 해당 파일의 노드 추출
3. CALLS 엣지에서 호출자/피호출자 추출
4. IMPORTS_FROM 엣지에서 의존성 추출
5. 모듈 소스 파일에서 ENUM 정의 및 값 추출
6. 에러 코드 상수 및 예외 정의 추출
7. 모듈에서 사용하는 IPC 메시지 ID 및 프로토콜 상수 추출
8. 신호/이벤트 연결 매핑 (BroadcastReceiver 액션, LiveData observations, callbacks)
9. Error Code Definitions 테이블 채우기: `llm-constant-results.json` 에서 모듈 파일 필터링 (type="error_code")
10. Constant Definitions 테이블 채우기: `llm-constant-results.json` 에서 모듈 파일 필터링 (error_code 및 enum 값 제외)
11. IPC Dependencies 테이블 채우기: `llm-ipc-results.json` 에서 모듈 파일 필터링
12. Message Protocol 테이블 채우기: `llm-ipc-results.json` message_ids 에서 모듈 파일 필터링
13. Signal/Event mappings 테이블 채우기: `llm-ipc-results.json` signal_events 에서 모듈 파일 필터링

LLM 추출 결과 위치: `<output-dir>/.analysis/llm-extraction/llm-{enum,constant,ipc}-results.json`

### 2-2. FR 문서 작성 구조

```markdown
# Functional Requirement: <ModuleName>

> **Relevant source files**
>
> - [path/to/file.ts](src:path/to/file.ts)

**Source**: [`file.ts`](src:path/to/file.ts#L1)
**분석 기준**: AST 파싱 결과 + 코드 직접 분석

## Given Factors
- Module/Package / Class / Function / Variable / External

## 개요
[코드에서 직접 확인된 동작만. 추측 금지.]

## 기능 요구사항
- FR-XXX-001: ... ``[`Sym`](src:path#L<n>)``

## 의존성
### 내부 모듈
### 외부 API/DB/서비스

## Code Factors
### Module/Package / Class / Function / Variable / External

## 품질
- 에러 핸들링 / 로깅 / 보안

## ENUM 정의

| ENUM 이름 | 값 | 사용처 | Source |
|-----------|-----|--------|--------|

## 에러 코드 정의

| 에러 코드 | 값 | 심각도 | 트리거 조건 | 복구 액션 | Source |
|-----------|-----|--------|-------------|-----------|--------|

## 메시지 프로토콜

| 메시지 ID | 방향 | 페이로드 타입 | 핸들러 | IPC 메커니즘 | Source |
|-----------|------|--------------|--------|-------------|--------|

## 제약사항

## Class Diagram (mermaid)

## Sequence Diagram (mermaid, CALLS 체인 기반, 최대 5 depth)

## Test Cases
### Positive / Negative / Edge
```

저장: `<output-dir>/functional-requirements/<module-name>-fr.md`

### 2-3. 완료 마킹

```bash
PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
${PYTHON} .code2spec-tools/code2spec_progress.py update \
  --output-dir "<output-dir>/.analysis" \
  --module "<module-name>" \
  --status done \
  --fr-doc "functional-requirements/<module-name>-fr.md"
```

### 2-4. 청크 완료 후 컨텍스트 저장

10 개 완료 시:

```bash
PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
${PYTHON} .code2spec-tools/code2spec_progress.py append-context \
  --output-dir "<output-dir>/.analysis" \
  --pattern "청크 완료: [모듈 목록]"
```

---

## Step 3: 반복

`next-chunk` 가 `ALL_DONE` 반환 시까지 Step 2 반복.

---

## Step 4: FR 인덱스 생성

`<output-dir>/functional-requirements/index.md`:

| File | Module | FR Document |
|------|--------|-------------|
| ...  | ...    | [link]      |

**데이터 출처**: `code2spec/.analysis/cache/code-to-ast/graph-raw.md` (분석 중간산출; 코드 인용은 본문에서 백틱 deep-link 사용)
