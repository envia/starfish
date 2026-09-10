---
name: code2spec-discovery
description: "Run W1 discovery: AST parsing, core selection, and system-level spec generation."
metadata:
  code-skills:
    id: code2spec/code2spec-discovery
---

# Claude Code Skill: code2spec-discovery

> This skill is generated from the code2spec workflow markdown for Claude Code.
> Shared templates are installed under `.claude/code2spec/templates/`; Python tools are installed under `.code2spec-tools/`.
> Installed tool build metadata is recorded at `.code2spec-tools/build-info.json`.

# Workflow: code2spec-discovery (W1)

**Workflow format**: 1
**Tool version**: install/runtime resolved (`.code2spec-tools/build-info.json`)
**마지막 수정**: 2026-08-04

AST 파싱 → Core 모듈 목록 확정 → 시스템 레벨 SDD 문서 생성.
**컨텍스트 소비가 적어 완주 보장.** 모듈 심층 분석은 W2 에서 수행.

**실행 순서**: `code2spec-discovery` (W1) → `code2spec-modules` (W2) → `code2spec-finalize` (W3)

---

## 🚀 AI 자동 실행 지침 — 워크플로우 제공 시

> **CRITICAL**: 사용자가 이 워크플로우 문서를 제공하고 /code2spec-discovery 또는 W1 실행을 요청하면:
>
> 1. **질문 없이 즉시 Step 1 부터 시작** — "What would you like me to do?" 같은 질문 금지
> 2. **Step 2에서 기존 결과를 먼저 확인** — 출력 경로 확정 → AX Artifact 후보 조회 → 미복원 시에만 문서 언어 선택
>    - snapshot 후보가 있을 때만 다운로드 여부를 Human-in-the-Loop로 확인
> 3. **AX Artifact 복원 성공 시 즉시 W1 종료** — 복원된 `${ANALYSIS_TARGET}/code2spec`을 그대로 사용하며 Step 3-7을 실행하지 않음
> 4. **새 분석 분기에서는 W1 완전 완료 지침 준수** — 복원하지 못했거나 사용자가 건너뛴 경우 모든 Step(1-7) 을 한 번에 완료
>
> ```text
> 잘못된 예 (금지):
>   "You've provided the code2spec-discovery workflow documentation but haven't specified a task..."
>   "Would you like me to: 1. Execute W1... 2. Analyze..."
> ```
>
> ```text
> 올바른 예:
>   "[W1 시작] code2spec-discovery 워크플로우를 실행합니다."
>   "[Step 1/7] 사전 요구사항 확인 중..."
> ```

---

## Path Variable Contract

`<analysis-target-path>`는 실제 분석할 프로젝트 루트 또는 하위 디렉토리입니다.
전체 프로젝트 분석이면 설치 프로젝트 루트를, `src`만 분석하면 `<workspace-root>/src`를 지정합니다.

```bash
WORKSPACE_ROOT="<installed-project-root>"      # .code2spec-tools, .code2spec-venv 위치
ANALYSIS_TARGET="<analysis-target-path>"       # 예: /repo 또는 /repo/src
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
AST_DIR="${ANALYSIS_DIR}/cache/code-to-ast"
```

상대 경로(`src`, `packages/foo`)를 받은 경우 현재 설치 프로젝트 루트 또는 현재 작업 디렉토리 기준으로 절대화합니다.
산출물은 항상 `${ANALYSIS_TARGET}/code2spec` 아래에 생성되며, scoped 분석은 대상 밖 소스를 자동 포함하지 않습니다.

### Path Safety Check

문서 생성 전에 아래를 반드시 확인합니다.

```bash
test -d "${WORKSPACE_ROOT}/.code2spec-tools"
test -d "${ANALYSIS_TARGET}"
case "${OUTPUT_DIR}" in
  "${ANALYSIS_TARGET}"/code2spec) ;;
  *) echo "[STOP] OUTPUT_DIR must be ANALYSIS_TARGET/code2spec"; exit 1 ;;
esac
case "${ANALYSIS_DIR}" in
  "${OUTPUT_DIR}"/.analysis) ;;
  *) echo "[STOP] ANALYSIS_DIR must be OUTPUT_DIR/.analysis"; exit 1 ;;
esac
```

`"${WORKSPACE_ROOT}/code2spec"`가 이미 존재하고 `"${OUTPUT_DIR}"`와 다르면
기존 full-build 산출물일 수 있습니다. 이 경우 절대 `${WORKSPACE_ROOT}/code2spec`를 갱신하지 말고,
현재 실행의 모든 SDD/FR/modules/diagrams/history/progress 파일을 `${OUTPUT_DIR}` 아래에만 저장합니다.

---

## 🚨 전역 AI 동작 원칙 — ⭐️ 필독 ⭐️

1. **약어 유추 절대 금지**: 코드·README 에 정의 없으면 원문 그대로
2. **코드 밖 상상 금지**: 폴더명·클래스명만 보고 목적·기능 추측 금지
3. **출처 표기 강제**: 모든 주장에 `[Source: /path/file.ts:L#]` 필수
4. **정보 없으면**: `"코드 내 식별 불가"` 기재

---

## 🤖 AI 출력 행동 규칙 — W1 워크플로우 전용

> **중요**: 이 규칙은 W1 워크플로우 실행 중 AI 의 출력 빈도를 제어합니다.

### W1 완전 완료 지침

**CRITICAL**: 사용자가 W1 워크플로우를 앵커하면:

- **모든 Step(1-7) 을 한 번에 완료** — 중간에 중지 금지
- **모든 SDD 챕터 (01-09) 생성** — 누락 금지
- **다이어그램 생성 (Step 3-6b)** — `diagrams/architecture.mmd` + `diagrams/dependency-heatmap.mmd` 필수 (빈 폴더 금지)
- **FR index 생성** — W1 의 필수 완료 조건
- **최종 요약만 출력** — "To Continue W1" 출력 금지

```text
올바른 예:
  [W1 완료] 시스템 문서 생성 완료
  - SDD 챕터: 01-09 (9 개)
  - FR index: 생성됨
  - 분석 노트: module-priority.md 등
  - 소요시간: 30 분
```

```text
잘못된 예 (금지):
  01-introduction.md 생성 완료 → 요약 출력 ❌
  "To Continue W1, run the next command..." ❌
  02-architecture.md 생성 완료 → 요약 출력 ❌
```

### Step 5 문서 생성 지침

Step 5(시스템 문서 생성) 에서:

- 01-08 챕터: 순차적으로 생성 (각 챕터별로 한 번의 LLM 호출)
- 09-ipc-enum-catalog: LLM 추출 결과 (llm-\*.json) 를 우선 사용
- FR index: 모든 Core 모듈의 FR 문서 목록 생성
- **중간 요약 금지** — 9 개 챕터 모두 생성 후 최종 요약만 출력

---

## 단계 개요

| Step | 내용                        | 유형                     |
| ---- | --------------------------- | ------------------------ |
| 1    | 사전 요구사항 확인          | 자동                     |
| 2    | 출력 경로·기존 결과·새 분석 언어 확정 | 자동 + Human-in-the-Loop |
| 3    | Discovery Pipeline 실행     | 자동 + Human-in-the-Loop |
| 4    | Core 모듈 목록 검토 및 확정 | Human-in-the-Loop        |
| 5    | 시스템 문서 생성            | 자동                     |
| 6    | W1 검증 및 종료 기록        | 자동                     |
| 7    | W2 handoff                  | 자동                     |

---

## 워크플로우 개요

### 실행 순서

```text
W1: code2spec-discovery  →  W2: code2spec-modules  →  W3: code2spec-finalize
   (AST + 시스템 문서)         (모듈 심층 분석)           (링킹 + Quick Reference 생성)
```

각 워크플로우는 독립 실행 가능. W2는 중단 후 재개 지원.

### 워크플로우 역할

| Workflow | 파일                     | 역할                                                      | 토큰 부담        | Human-in-the-Loop                  |
| -------- | ------------------------ | --------------------------------------------------------- | ---------------- | ---------------------------------- |
| **W1**   | `code2spec-discovery.md` | AST 파싱 + 모듈 목록 확정 + 시스템 문서(01~09) + FR index | 낮음             | 언어·저장 위치·분석 범위·모듈 목록 |
| **W2**   | `code2spec-modules.md`   | Core 모듈 심층 분석 + Module Design Card + FR 문서        | 높음 (청크 재개) | 없음                               |
| **W3**   | `code2spec-finalize.md`  | Interlinking + Quick Reference + History                  | 낮음             | 없음                               |

> AX Artifact MCP를 사용할 수 있는 환경에서는 W1의 AX Artifact restore와 W3의 AX Artifact upload가 추가됩니다.

### 결과물 구조

```text
<analysis-target>/code2spec/
├── history.md
├── README.md

├── 01-introduction.md
├── 02-architecture.md
├── 03-design-patterns.md
├── 04-data-layer.md
├── 05-external-interfaces.md
├── 06-configuration-deployment.md
├── 07-resources.md
├── 08-security-quality.md
├── 09-ipc-enum-catalog.md
├── functional-requirements/
│   ├── index.md
│   └── <module>-fr.md
├── modules/
│   └── <module-name>.md
├── diagrams/
│   ├── architecture.mmd
│   └── dependency-heatmap.mmd
└── .analysis/
    ├── code2spec-config.json
    ├── runtime-stats.json
    ├── analysis-progress.json
    ├── modules-traceability.md
    ├── analysis-notes/
    │   ├── module-priority.md
    │   ├── module-priority-reviewed.md
    │   ├── dead-code.md
    │   ├── entry-points.md
    │   └── dependency-heatmap.mmd
    ├── llm-extraction/
    │   ├── llm-enum-prompt.md
    │   ├── llm-enum-results.json
    │   ├── llm-constant-prompt.md
    │   ├── llm-constant-results.json
    │   ├── llm-ipc-prompt.md
    │   ├── llm-ipc-results.json
    │   └── llm-extraction-results.json
    └── code-to-ast/
        ├── graph-raw.md
        └── graph-mermaid/
```

> **04-core-modules.md 없음**: 각 Core 모듈은 W2에서 `modules/<name>.md` (Module Design Card)로 분리 생성됨.

---

## Step 1: 사전 요구사항 확인

### 필수 Skill 목록

| #   | Skill                            | 설명                                           |
| --- | -------------------------------- | ---------------------------------------------- |
| 1   | code2spec-code-to-ast            | tree-sitter AST 추출 (`cli.py export`)         |
| 2   | code2spec-structure-discovery    | 디렉토리 구조·아키텍처 패턴 분석               |
| 3   | code2spec-dependency-audit       | 외부 라이브러리·SOUP 분석                      |
| 4   | code2spec-doc-generation         | Zero-Inference·표준 템플릿 문서 생성           |
| 5   | code2spec-code-to-diagram        | Mermaid.js 다이어그램 생성                     |
| 6   | code2spec-functional-requirement | FR index 생성                                  |
| 7   | code2spec-ipc-discovery          | LLM 기반 IPC 패턴 발견 (`cli.py discover-ipc`) |

### 완료 조건

- 7개 Skill 목록 확인 완료
- 의존성 미설치 시 code-to-ast 실행 시점에 STOP 처리됨을 이해하고 진행

---

## Step 2: 출력 경로·기존 결과·새 분석 설정 확정

> **⚠️ 중요: 각 선택 항목은 반드시 개별적으로 사용자에게 질문하고 응답을 받은 후 다음 항목으로 진행합니다.
> 여러 항목을 한 번에 묻거나 동시에 선택하게 하면 안 됩니다.**

### 실행 순서

1. **출력 경로 확정**
2. **AX Artifact 기존 snapshot 후보 조회**
3. **복원되지 않은 경우에만 문서 언어 선택**

### 2-1. 출력 경로 확인

- `${ANALYSIS_TARGET}/code2spec/`
- 작업 디렉토리: `${ANALYSIS_TARGET}/code2spec/.analysis/`

```bash
WORKSPACE_ROOT="<installed-project-root>"
ANALYSIS_TARGET="<analysis-target-path>"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
AST_DIR="${ANALYSIS_DIR}/cache/code-to-ast"
```

### 2-2. AX Artifact 기존 snapshot 조회 및 복원

> 저장 위치가 확정된 뒤, 초기 디렉토리를 만들거나 AST export를 실행하기 전에 수행합니다.
> MCP 서버 이름은 `ax-artifacts`, download 도구의 논리 이름은 `ax_artifacts_download`로 고정합니다. 입력 필드는 도구가 현재 노출하는 schema를 따릅니다.
> download 목적지는 반드시 `${OUTPUT_DIR}`, 즉 `${ANALYSIS_TARGET}/code2spec`입니다. 별도의 임시 또는 대체 output 디렉토리를 사용하지 않습니다.

`AX_ARTIFACT_RESTORE_STATUS`의 시작 상태는 `skipped`입니다.

#### MCP 도구 가용성 확인

1. 사용 가능한 MCP 도구 목록에서 `ax-artifacts` 서버의 `ax_artifacts_download` 도구를 찾습니다.
   - 서버 이름과 도구의 논리 이름은 정확히 일치시킵니다.
   - 클라이언트가 서버/도구 이름을 조합해 생성한 긴 qualified alias는 워크플로에 하드코딩하지 않습니다.
   - MCP 설정이나 인증 token 값을 읽거나 출력하지 않습니다.
2. download 도구가 없으면 이유를 한 줄로 알리고 MCP 호출 없이 Step 2-3 문서 언어 선택으로 진행합니다.

#### Git/Gerrit context 추출 (MCP 호출 전 필수)

download 도구가 확인되면 MCP를 호출하기 전에 설치된 공통 CLI로 현재 분석 대상의 저장소 정보를 추출합니다.

```bash
GIT_CONTEXT_JSON=$(${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/git_context.py" \
  --repo "${ANALYSIS_TARGET}" \
  --format json)
```

- JSON의 `lookup_status`가 `ok`이고 credential이 제거된 `remote_url`이 존재하면 snapshot 후보 조회를 수행합니다. `branch`와 `commit_id`는 조회를 좁히는 선택 값입니다.
- `status=incomplete`이더라도 `lookup_status=ok`이면 detached HEAD처럼 branch가 없는 경우에도 MCP 후보 조회를 수행합니다.
- `not_git`, `error`, 또는 `lookup_status=incomplete`이면 `AX_ARTIFACT_RESTORE_STATUS="skipped-no-git-context"`로 기록하고 MCP를 호출하지 않습니다.
- CLI가 반환한 remote URL은 credential이 제거된 값이며 원본 credential이나 token을 다시 수집하지 않습니다.
- `GIT_CONTEXT_JSON`을 파일, history, telemetry에 저장하지 않습니다.

`lookup_status=incomplete`로 remote URL을 확인할 수 없을 때만 누락 필드를 표시하되 빈 값이나 credential을 추정하지 않고 다음과 같이 안내한 뒤 Step 2-3으로 진행합니다.

```text
[W1 Step 2-2] Git 저장소 정보를 완전하게 확인할 수 없어
잘못된 AX Artifact를 조회하지 않도록 기존 결과 확인을 건너뜁니다.

- 누락 정보: <git_context.py의 missing 목록>
- 결과: 로컬 Code2Spec 새 분석 계속
```

#### 언어 선택 전 snapshot 후보 조회

download 도구와 `lookup_status=ok`인 remote URL이 확인되면 문서 언어를 묻기 전에 다음을 수행합니다.

1. `ax-artifacts` 서버의 `ax_artifacts_download` 도구가 현재 노출하는 schema를 사용하여 snapshot 후보 또는 ready-to-run 명령을 조회합니다.
   - 이 호출 단계에서는 download/extract 명령을 실행하거나 `${OUTPUT_DIR}` 내부 파일을 변경하지 않습니다.
   - AI assistant가 표시하는 MCP 도구 실행 승인 절차는 그대로 유지합니다.
   - destination/output directory 필드가 있으면 `${OUTPUT_DIR}`을 사용합니다.
   - `remote_url`: `GIT_CONTEXT_JSON.remote_url`
   - `channel`: `code2spec` (항상 이 고정값 사용)
   - `coding_agent`: `claude-code` (설치 시 확정된 고정값)
   - `branch`와 `commit_id`는 값이 있고 현재 schema가 해당 선택 필드를 지원할 때만 전달합니다. 빈 값, `null`, 추정 branch는 전달하지 않습니다.
   - 현재 schema가 `vcs_host`, `vcs_org`, `vcs_repo`를 지원하면 같은 JSON의 값을 함께 전달합니다.
   - `working_dir` 필드가 필수이면 `${WORKSPACE_ROOT}`도 전달하되 저장소 식별을 대신하는 값으로 사용하지 않습니다.
   - `coding_agent`는 실행 중에 LLM이 다시 추론하거나 변경하지 않고, 설치된 workflow에 렌더링된 값을 그대로 사용합니다.
2. 응답 상태에 따라 분기합니다:
   - `status=ok` (snapshot 존재) → 아래 Snapshot 확인과 HITL 진행
   - `status=not_found` (등록된 artifact 없음) → `skipped`, Step 2-3 문서 언어 선택으로 진행
   - `status=error` (인증/서비스 오류) → `failed-continued`, Step 2-3 문서 언어 선택으로 진행
   - `status=forbidden` / `auth_error` → `failed-continued`, Step 2-3 문서 언어 선택으로 진행
3. snapshot 탐색 우선순위는 MCP 동작에 맡기며, `remote_url`은 `git_context.py` 결과를 사용하고 branch·commit은 확인된 경우에만 보조 식별값으로 전달합니다.

다음 상황은 W1 실패가 아니라 정상적인 degradation입니다. 이유를 한 줄로 알리고 Step 2-3 문서 언어 선택으로 계속합니다.

- `ax-artifacts` 서버 또는 `ax_artifacts_download` 도구 미설치·비활성
- 인증 실패(토큰 미설정 포함) 또는 서비스 일시 오류
- MCP가 지원하지 않는 저장소로 판단
- Git context가 없거나 remote URL이 누락됨
- matching snapshot 없음(`not_found`)
- 사용자가 MCP 도구 실행을 승인하지 않음

인증 실패 시 토큰 값을 검사하거나 출력하지 않고 사용 중인 AI assistant의 MCP 서버 설정에서 `CODE_GITHUB_TOKEN`, `CODE_BART_TOKEN`, `AX_ARTIFACTS_API_KEY` 중 설정한 인증 키를 확인하라고 안내합니다.

#### Snapshot 확인과 HITL

download 도구가 후보 snapshot 또는 ready-to-run 명령을 반환하면 다음 정보를 사용자에게 표시합니다.

```text
[W1 Step 2-2] 이전에 분석한 Code2Spec 결과가 있습니다.

AX Artifact에 저장된 기존 분석 결과를 발견했습니다.
새로 분석하는 대신 이 결과를 ${OUTPUT_DIR}에 내려받아 재활용할까요?

- Repository: <MCP가 반환한 경우 실제 값>
- 분석 기준 branch/commit: <MCP가 반환한 실제 값>
- 생성 시각/version: <반환된 경우 표시>
- 복원 위치: ${OUTPUT_DIR}

⚠ 기존 ${OUTPUT_DIR}가 있으면 snapshot이 병합되며 동일 경로 파일은 덮어써질 수 있습니다.
기존 디렉토리를 자동 삭제하지는 않습니다.

1) 기존 분석 결과 재활용 (다운로드)
2) 새로 분석하기 (건너뛰기)
```

사용자가 `1) 기존 분석 결과 재활용`을 선택한 경우에만 MCP가 반환한 download/extract 명령을 실행합니다.

- 명령의 추출 목적지가 `${OUTPUT_DIR}`인지 먼저 확인합니다.
- `${OUTPUT_DIR}` 밖을 삭제하거나 추출하는 명령이면 실행하지 말고 올바른 destination으로 도구를 다시 호출합니다.
- bearer token, signed URL 등 일회성 인증 정보는 사용자 메시지, history, telemetry에 기록하지 않습니다.
- 명령 종료 코드가 0인지, 실행 후 `${OUTPUT_DIR}`이 존재하는지 확인합니다.
- 성공하면 `AX_ARTIFACT_RESTORE_STATUS="restored"`, 사용자가 건너뛰면 `"user-skipped"`, 실패하면 `"failed-continued"`로 기록합니다.

#### 복원 성공 시 terminal branch

`AX_ARTIFACT_RESTORE_STATUS="restored"`이면 다음 내용을 출력하고 **현재 W1 workflow를 즉시 종료합니다.**

```text
[W1 Step 2-2] AX Artifact에서 기존 Code2Spec을 복원했습니다.

- 복원 경로: ${OUTPUT_DIR}
- 결과: 기존 Code2Spec snapshot 사용

복원된 산출물을 그대로 사용하므로 Discovery Step 3-7은 실행하지 않습니다.
소스 변경분을 반영해야 한다면 별도로 code2spec-delta를 실행하세요.
```

- 초기 디렉토리 생성, AST export, 문서 재생성, W2/W3 handoff를 수행하지 않습니다.
- 복원된 `${OUTPUT_DIR}` 내부 파일을 현재 W1에서 추가로 수정하지 않습니다.
- 복원이 실패했거나 사용자가 건너뛴 경우에만 아래 Step 2-3으로 계속합니다.

### 2-3. 새 분석 문서 언어 선택 (복원되지 않은 경우에만)

> **AX Artifact 복원 성공 시 이 질문을 표시하지 않습니다.**
> 새 분석이 필요한 경우 반드시 이 항목만 단독으로 질문합니다.

```text
[W1 Step 2-3] 새로 생성할 문서 언어를 선택하세요:

  🇰🇷 한국어
  🇺🇸 English

선택하세요 (기본값: 한국어):
```

선택한 언어: **DOC_LANG=\*\***\_\_\_\_**\*\***

### 복원되지 않은 경우 초기 디렉토리 생성

```bash
mkdir -p "${ANALYSIS_DIR}/analysis-notes"
mkdir -p "${STATE_DIR}"
mkdir -p "${AST_DIR}"
mkdir -p "${OUTPUT_DIR}/functional-requirements"
mkdir -p "${OUTPUT_DIR}/modules"
mkdir -p "${OUTPUT_DIR}/diagrams"
```

### 완료 조건

- 문서 언어 확정
- 저장 위치 확정
- AX Artifact restore가 `skipped`, `user-skipped`, `failed-continued` 중 하나로 종료
- 작업 디렉토리 생성 완료

---

## Step 3: Discovery Pipeline 실행

### 목표

하나의 Discovery step 안에서 아래를 끝냅니다.

1. AST export
2. 분석 범위 선택
3. runtime / progress 초기화
4. Core 후보 분석
5. 구조 / 의존성 / 초기 시각화 확보

### 3-1. AST export (Initial)

First, run an initial AST export to collect the code structure:

```bash
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" export \
  --repo "${ANALYSIS_TARGET}" \
  --format both \
  --output-dir "${AST_DIR}"
```

결과:

- `${AST_DIR}/` 생성 확인
- `${AST_DIR}/.cache/parse-cache.json` 생성/갱신 확인

### 3-1b. IPC Pattern Discovery (REQUIRED - Optimized for Speed)

> **⚠️ CRITICAL STEP**: This step is MANDATORY. Do NOT skip.
>
> **Optimized**: Uses `--max-files 5` for fast execution (1-2 min instead of 5-10 min).
>
> **Purpose**: Discovers custom IPC mechanisms not in static patterns (ContentProvider, AIDL, custom protocols, etc.)

```bash
# OPTIMIZED: Use max-files=5 for faster execution (1-2 min instead of 5-10 min)
# For each language with IPC communication:
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"

# Step 1: Collect unmatched calls and generate LLM prompt (OPTIMIZED)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" discover-ipc \
  --source-dir "${ANALYSIS_TARGET}" \
  --language <language> \
  --output-dir "${ANALYSIS_DIR}/ipc-discovery" \
  --step prompt \
  --max-files 5

# ⏱️ Expected time: ~30-60 seconds for max-files=5

# Step 2: Send the generated prompt (${ANALYSIS_DIR}/ipc-discovery/llm-prompt.md) to Cline LLM and save response

# Step 3: Apply the LLM response to update IPC patterns
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" discover-ipc \
  --source-dir "${ANALYSIS_TARGET}" \
  --language <language> \
  --output-dir "${ANALYSIS_DIR}/ipc-discovery" \
  --step apply \
  --llm-response "${ANALYSIS_DIR}/ipc-discovery/llm-response.md"
```

**Why REQUIRED**:

- Static patterns only catch known IPC (binder, socket, pipe, etc.)
- Custom IPC (ContentProvider, AIDL, proprietary protocols) need dynamic discovery
- Without this step, 09-ipc-enum-catalog.md will miss project-specific IPC mechanisms
- Essential for Android projects with Binder/AIDL/ContentProvider

**Results**:

- `${ANALYSIS_DIR}/ipc-discovery/discovered-ipc-patterns.json` — Custom IPC patterns for this codebase
- Applied to AST export in Step 3-1d for accurate IPC extraction

### 3-1d. Final AST Export with Discovered IPC Patterns

Re-run AST export with all discovered configurations:

```bash
# Step 4: Re-run AST export after IPC discovery
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" export \
  --repo "${ANALYSIS_TARGET}" \
  --format both \
  --output-dir "${AST_DIR}" \
  --workers 1
```

Results:

- Confirm `${ANALYSIS_DIR}/ipc-discovery/discovered-ipc-patterns.json` creation
- AST export uses the canonical cache path and static parser patterns
- Constant nodes, Enum values, and other language-specific constructs are now properly extracted
- IPC patterns dynamically discovered and applied (new mechanisms like ContentProvider, AIDL, etc.)

### 3-1e. LLM-Based ENUM/Constant/IPC Extraction (REQUIRED - CLINE NATIVE LLM ONLY)

> **⚠️ CRITICAL STEP**: This step is MANDATORY. Do NOT skip. The workflow will fail validation if extraction is incomplete.
>
> **CLINE NATIVE LLM MODE**: This step uses ONLY Cline's NATIVE LLM - NO stub LLMClient is used.
>
> **IMPORTANT**: Do NOT use `--hybrid-auto` or any CLI mode that calls `LLMClient.generate()` or `LLMClient.stream()`.
> Those methods are stubs that return prompts verbatim (0 results). Instead, Cline MUST process prompts
> directly using its NATIVE LLM through the conversation.
>
> **How It Works**:
>
> 1. CLI generates prompts ONLY (file I/O, no LLM call)
> 2. **CLINE (YOU) MUST read each prompt and use YOUR NATIVE LLM to extract JSON**
> 3. CLINE saves JSON responses to result files
> 4. CLI merges rule-based + Cline's JSON results
>
> **Time**: ~5-10 min total (depends on codebase size and Cline's LLM processing)

#### Step 3-1e.1: Generate LLM Extraction Prompts (CLI - File I/O Only)

```bash
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"

# Generate prompts ONLY - NO LLM CALL (just saves markdown files)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/llm_extract_cli.py" \
  --ast-json "${AST_DIR}/graph-raw.json" \
  --output-dir "${ANALYSIS_DIR}/llm-extraction" \
  --extract all \
  --generate-prompts-only

# Expected output:
# Generated prompts saved to:
#   - ${ANALYSIS_DIR}/llm-extraction/llm-enum-prompt.md
#   - ${ANALYSIS_DIR}/llm-extraction/llm-constant-prompt.md
#   - ${ANALYSIS_DIR}/llm-extraction/llm-ipc-prompt.md
```

#### Step 3-1e.2: CLINE MUST Process Prompts with NATIVE LLM (NO STUB)

> **⚠️ ATTENTION CLINE (AI Assistant): THIS IS YOUR TASK TO COMPLETE NOW**
>
> **USE SKILL**: Execute `code2spec-llm-extraction` skill to process all prompts.
>
> You MUST process each of the three prompt files below using YOUR NATIVE LLM.
> Do NOT call any CLI command that uses `LLMClient.generate()` - those are stubs.
> Instead, read each prompt file and extract the JSON response yourself.

**CLINE ACTION REQUIRED - Process ALL THREE prompts:**

```text
┌─────────────────────────────────────────────────────────────────┐
│  CLINE TASK: Extract LLM Data Using YOUR NATIVE LLM             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FOR EACH prompt file, you MUST:                                │
│  1. Read the prompt file content                                │
│  2. Analyze and extract data using YOUR NATIVE LLM              │
│  3. Return ONLY valid JSON (following prompt's output format)   │
│  4. Save JSON to the corresponding result file                  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Prompt 1: ${ANALYSIS_DIR}/llm-extraction/llm-enum-prompt.md │  │
│  │   → Extract ENUM definitions                               │  │
│  │   → Save to: ${ANALYSIS_DIR}/llm-extraction/llm-enum-results.json │  │
│  │                                                           │  │
│  │ Prompt 2: ${ANALYSIS_DIR}/llm-extraction/llm-constant-prompt.md │  │
│  │   → Extract constant definitions                           │  │
│  │   → Save to: ${ANALYSIS_DIR}/llm-extraction/llm-constant-results.json │  │
│  │                                                           │  │
│  │ Prompt 3: ${ANALYSIS_DIR}/llm-extraction/llm-ipc-prompt.md │  │
│  │   → Extract IPC patterns                                   │  │
│  │   → Save to: ${ANALYSIS_DIR}/llm-extraction/llm-ipc-results.json │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ⚠️ CRITICAL: Do NOT use CLI commands with --hybrid-auto       │
│  or any mode that calls LLMClient.generate() - those are stubs  │
│  that return 0 results. Use YOUR NATIVE LLM directly!           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Output Format Requirements (for each result file):**

- Each result file MUST contain a valid JSON array
- Each entry MUST include `[Source: file:line]` citation
- ENUM entries: `{"name": "...", "values": [...], "type": "...", "source": "[Source: ...]"}`
- Constant entries: `{"name": "...", "value": "...", "type": "...", "source": "[Source: ...]"}`
- IPC entries: `{"mechanism": "...", "name": "...", "source": "[Source: ...]"}`

**Example ENUM Response:**

```json
[
  {
    "name": "MyClass.State",
    "values": ["ACTIVE", "INACTIVE", "PENDING"],
    "type": "kotlin_enum",
    "source": "[Source: src/main/java/com/example/MyClass.kt:45]"
  }
]
```

#### Step 3-1e.3: Merge and Validate Results (After CLINE Completes Step 3-1e.2)

> **Note**: Only run this step AFTER Cline has processed all three prompts and saved the JSON result files.

```bash
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"

# Merge rule-based and Cline's LLM results
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/llm_extract_cli.py" \
  --ast-json "${AST_DIR}/graph-raw.json" \
  --load-results "${ANALYSIS_DIR}/llm-extraction" \
  --output "${ANALYSIS_DIR}/llm-extraction/llm-extraction-results.json" \
  --merge-only

# Validate extraction completeness (blocks if below thresholds)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/llm_extract_cli.py" \
  --validate \
  --ast-json "${AST_DIR}/graph-raw.json" \
  --load-results "${ANALYSIS_DIR}/llm-extraction" \
  --min-enum 5 \
  --min-constant 20 \
  --min-ipc 10
```

**Expected Results:**

- ENUMs: 10-50+ items (rule-based + LLM gap-fill)
- Constants: 50-200+ items (rule-based + LLM gap-fill)
- IPC Patterns: 20-100+ items (rule-based + LLM gap-fill)

**Validation Gate**: If validation fails, DO NOT proceed to Step 4. Fix the extraction first.

Common failure modes:

- **Too few ENUMs (< 5)**: Check if codebase has enums; if not, document as "No enums in codebase"
- **Too few Constants (< 20)**: Check if rule-based missed patterns; may need to adjust CONSTANT_NAME_PATTERNS
- **Too few IPC (< 10)**: Check if IPC-heavy codebase; if yes, consider running Step 3-1c (IPC Pattern Discovery)

**Validation Gate**: If validation fails, DO NOT proceed to Step 4. Fix the extraction first.

Common failure modes:

- **Too few ENUMs (< 5)**: Check if codebase has enums; if not, document as "No enums in codebase"
- **Too few Constants (< 20)**: Check if rule-based missed patterns; may need to adjust CONSTANT_NAME_PATTERNS
- **Too few IPC (< 10)**: Check if IPC-heavy codebase; if yes, consider running Step 3-1c (IPC Pattern Discovery)

Results:

- `${ANALYSIS_DIR}/llm-extraction/llm-extraction-results.json` — Combined extraction results
- `${ANALYSIS_DIR}/llm-extraction/llm-extraction-summary.md` — Human-readable summary
- `${ANALYSIS_DIR}/llm-extraction/validation-report.md` — Validation report (if --validate run)

These results are used in Step 5-9 for `09-ipc-enum-catalog.md` generation.

**Skip Impact** (if this step is skipped):

- ENUMs: Only basic `enum` keyword declarations detected (misses sealed classes, union types)
- Constants: Only `static final` fields detected (misses protocol constants, error codes)
- IPC: Only static patterns detected (misses custom protocols, dynamic channels)
- **Result**: 09-ipc-enum-catalog.md will have incomplete data (5-10 items vs. 50-100+)

### 3-1-b. Interface/Protocol Candidate Scan

> AST export 직후, Module Discovery 이전에 실행.
> 스캐너 실패 시 fail-soft 정책 적용 (strict 모드가 아니면 워크플로우 계속).

```bash
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
PYTHONPATH="${WORKSPACE_ROOT}/.code2spec-tools" ${PYTHON} -m interface_scanner.cli \
  --repo "${ANALYSIS_TARGET}" \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}" \
  --families message \
  --targets android,node,react
```

> **실행 전제**: install 후 `.code2spec-tools/interface_scanner/`가 존재해야 합니다.
> repo 개발 환경에서 직접 실행할 때는 `python -m tools.interface_scanner.cli ...`도 사용할 수 있습니다.

결과 (필수):

- `${ANALYSIS_DIR}/interface-candidates.json` — 후보 스키마 JSON (source of truth)
- `${ANALYSIS_DIR}/message-contract-candidates.md` — 인간 리뷰용 마크다운

결과 (선택):

- `${ANALYSIS_DIR}/interface-candidate-metrics.json` — 메트릭

실패 시:

- `${ANALYSIS_DIR}/interface-candidate-scan-error.json` — 진단 파일
- strict 모드가 아니면 W1 계속 진행
- **W2 대비**: 후보 파일이 없어도 W2는 정상 진행됨
  - `interface-candidates.json` 미생성 → W2의 A-IPC 단계에서 파일 없음으로 감지
  - Module Design Card의 IPC 섹션 작성 시 LLM이 코드를 직접 읽고 식별
  - 템플릿의 지시어에 "정적 분석 결과가 없으면" 경로 포함됨

> **중요**:
>
> - 스캐너 결과로 기존 SDD 챕터(01~08)를 직접 수정하지 않음
> - interface-candidates.json은 W2에서만 사용되며, W1에서는 생성만 담당함

### 3-2. Module Discovery

AST export 결과를 기반으로 모듈 그룹핑을 수행합니다.

#### 3-2-a. Module Discovery 실행

```bash
mkdir -p "${ANALYSIS_DIR}/module-discovery"

# Module Discovery 실행 (프롬프트 생성)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" discover \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}/module-discovery" \
  --prompt A
```

생성된 프롬프트 (`${ANALYSIS_DIR}/module-discovery/llm-prompt.md`) 를 LLM 에게 전송하고 응답을 받습니다.

LLM 응답을 YAML 파일로 저장한 후 review 실행:

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" review \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}/module-discovery" \
  --llm-response "${ANALYSIS_DIR}/module-discovery/llm-response.yaml" \
  --output "module-groups-proposed.yaml"
```

#### 3-2-b. 모듈 후보군 검토 (Human-in-the-Loop)

`module-groups-proposed.yaml`의 내용을 사용자에게 테이블 형태로 표시합니다:

```text
[W1 Step 3-2] 🔍 LLM Module Discovery 결과

LLM이 식별한 모듈 경계 후보:

| # | 모듈 이름 | 파일 수 | 포함 파일 | Confidence | 근거 |
|---|----------|--------|----------|-----------|------|
| 1 | task-management | 6 | TaskContext.tsx, TaskProvider.tsx, TaskItem.tsx, ... | 0.92 | Task 관련 Context, Component, Page가 응집된 도메인 |
| 2 | user-management | 2 | UserContext.tsx, UserProvider.tsx | 0.88 | User Context/Provider로 구성된 사용자 관리 도메인 |
| 3 | navigation | 3 | App.tsx, router.tsx, MainLayout.tsx | 0.85 | App 진입점, 라우팅, 레이아웃 셸 |
| ... | ... | ... | ... | ... | ... |

총 N개 모듈 후보 식별됨

검토 옵션:
  1) 승인 — 제안된 모듈 경계 그대로 사용
  2) 수정 — module-groups-proposed.yaml 편집 후 다시 로드
  3) 재실행 — Module Discovery 다시 실행 (다른 프롬프트/설정)

선택: __________
```

- **승인(1)**: `group_cli.py save` 실행
- **수정(2)**: 사용자가 `module-groups-proposed.yaml`을 직접 편집 후 `group_cli.py save` 실행
- **재실행(3)**: 3-2-a부터 다시 실행

#### 3-2-c. 모듈 그룹 확정

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" save \
  --config "${ANALYSIS_DIR}/module-discovery/module-groups-proposed.yaml" \
  --output-dir "${STATE_DIR}"
```

**결과:** `${STATE_DIR}/module-groups.yaml` 생성

### 3-3. Core 후보 분석 (모듈 단위)

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/ast_analyzer.py" \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}/analysis-notes" \
  --granularity module \
  --module-groups "${STATE_DIR}/module-groups.yaml"
```

결과: `${ANALYSIS_DIR}/analysis-notes/module-priority.md` 생성

- 각 모듈 그룹이 하나의 모듈로 표시됨 (파일 목록 포함)

> **module-review 스킬이 생략되므로 `module-priority-reviewed.md`가 생성되지 않습니다.**
> 하위 도구(`save-core-manifest`, `init` 등)가 `module-priority-reviewed.md`를 참조하므로,
> `module-priority.md`를 `module-priority-reviewed.md`로 복사합니다.

```bash
cp "${ANALYSIS_DIR}/analysis-notes/module-priority.md" \
   "${ANALYSIS_DIR}/analysis-notes/module-priority-reviewed.md"
echo "[W1] module-priority.md → module-priority-reviewed.md 복사 완료"
```

### 3-4. Core 목록 출력 (Human-in-the-Loop)

> **⚠️ 이 단계는 Core 목록을 표시만 합니다. 분석 범위 선택은 3-5에서 별도로 진행합니다.
> 목록 표시와 범위 선택을 함께 묻지 마세요.**

#### 모듈 경계 승인 결과

사용자가 HITL 리뷰에서 승인한 모듈 경계이므로
Core/Peripheral 분류를 생략합니다. 모든 논리 모듈이 Core로 분류됩니다.

`module-groups.yaml`과 `module-priority.md` 내용을 사용자에게 표시:

```text
[W1 Step 3-4] 🔍 Module Discovery 결과

LLM이 식별하고 HITL이 승인한 모듈 경계:

| 모듈 | 파일 수 | Confidence | 근거 |
|------|--------|-----------|------|
| task-management | 6 | 0.92 | Task 관련 Context, Component, Page가 응집된 도메인 |
| user-management | 2 | 0.88 | User Context/Provider로 구성된 사용자 관리 도메인 |
| navigation | 3 | 0.85 | App 진입점, 라우팅, 레이아웃 셸 |
| ... | ... | ... | ... |

총 N개 논리 모듈 식별됨 (모두 Core로 분류)

⚠️ 모든 모듈이 Core로 분류됩니다.
   (사용자가 승인한 모듈 경계이므로 Core/Peripheral 분류 생략)
```

### 3-5. 분석 범위 확정

사용자가 HITL 리뷰에서 승인한 모든 모듈이 Core로 분류되므로,
별도의 분석 범위 선택이 필요하지 않습니다. 자동으로 전체 모듈에 대해 상세 분석을 수행합니다.

**ANALYSIS_SCOPE=3** (Detail)로 자동 설정됨.

### 3-6. Core 재분석 + config 저장

```bash
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/ast_analyzer.py" \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}/analysis-notes" \
  --granularity module \
  --module-groups "${STATE_DIR}/module-groups.yaml"

cat > "${STATE_DIR}/code2spec-config.json" << 'EOF'
{
  "analysis_scope": ANALYSIS_SCOPE_VALUE,
  "doc_lang": "DOC_LANG_VALUE",
  "workspace_root": "WORKSPACE_ROOT_VALUE",
  "analysis_target": "ANALYSIS_TARGET_VALUE",
  "output_root": "OUTPUT_DIR_VALUE"
}
EOF
```

### 3-6b. 초기 다이어그램 생성 (diagrams/) — REQUIRED

> ⚠️ 이 단계를 건너뛰면 `${OUTPUT_DIR}/diagrams/`가 빈 폴더로 산출됩니다.
> 반드시 두 산출물(`architecture.mmd`, `dependency-heatmap.mmd`)을 `diagrams/` 아래에 생성해야 W1이 완료됩니다.

**(1) dependency-heatmap.mmd 배치 (자동 실행)**

3-6의 최종 재분석에서 `ast_analyzer.py`가 이미 생성한 히트맵을 최종 산출 폴더로 복사합니다.
(히트맵은 피의존 노드 + import 카운트에 더해, hotspot 노드로 향하는 `source → target` 관계 엣지와 가중치를 포함합니다.)

```bash
mkdir -p "${OUTPUT_DIR}/diagrams"
cp "${ANALYSIS_DIR}/analysis-notes/dependency-heatmap.mmd" \
   "${OUTPUT_DIR}/diagrams/dependency-heatmap.mmd"
```

**(2) architecture.mmd 생성 (`code2spec-code-to-diagram` skill 사용)**

`code2spec-code-to-diagram` skill을 실행하여 **초기 아키텍처·시스템 컨텍스트 다이어그램**을
`${OUTPUT_DIR}/diagrams/architecture.mmd`에 작성합니다. 히트맵과 달리 이 다이어그램은
**노드 + 관계 엣지**를 모두 포함해야 합니다.

- **노드 출처**: `${ANALYSIS_DIR}/analysis-notes/module-priority-reviewed.md`의 확정 Core 모듈
- **엣지 출처**: `${AST_DIR}/graph-raw.json` (또는 `${AST_DIR}/graph-mermaid/00-summary.md`)의
  실제 import/call 의존 관계. 엣지는 반드시 AST 의존 데이터로 뒷받침되어야 하며(Zero-Inference),
  방향은 원본 의존 방향을 유지합니다. AST에 없는 외부 노드는 `:::external`로 명시합니다.
- **형식**: Mermaid `graph TD` + 논리 그룹은 `subgraph`. 노드 ID는 실제 AST 토큰(파일 basename 등),
  사람이 읽을 이름은 quoted label로 표기합니다. (상세 규칙: `code2spec-code-to-diagram` skill 참고)

```
code2spec-code-to-diagram skill
  → 입력: ${ANALYSIS_DIR}/analysis-notes/module-priority-reviewed.md
          ${AST_DIR}/graph-raw.json, ${AST_DIR}/graph-mermaid/
  → 출력: ${OUTPUT_DIR}/diagrams/architecture.mmd   (노드 + 관계 엣지)
```

완료 조건:

- `${OUTPUT_DIR}/diagrams/architecture.mmd` 존재 (노드 + 엣지 포함)
- `${OUTPUT_DIR}/diagrams/dependency-heatmap.mmd` 존재

### 3-7. runtime / workflow 초기화

```bash
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
SESSION_MODE="detail"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" session-init \
  --output-dir "${ANALYSIS_DIR}" \
  --target-path "${ANALYSIS_TARGET}" \
  --workspace-root "${WORKSPACE_ROOT}" \
  --analysis-target "${ANALYSIS_TARGET}" \
  --output-root "${OUTPUT_DIR}" \
  --mode "${SESSION_MODE}" \
  --coding-agent "claude-code"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-start \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W1 \
  --coding-agent "claude-code"
```

### 3-8. Core manifest 저장

`module-priority-reviewed.md` 확정 후 W-DELTA가 Core 승격/강등을 감지할 수 있도록
현재 Core 목록을 `.analysis/state/delta/core-manifest.json`에 저장합니다.

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" save-core-manifest \
  --output-dir "${ANALYSIS_DIR}" \
  --priority-file "${ANALYSIS_DIR}/analysis-notes/module-priority-reviewed.md" \
  --workspace-root "${ANALYSIS_TARGET}" \
  --analysis-scope "${ANALYSIS_SCOPE}" \
  --mode "${SESSION_MODE}" \
  --module-groups "${STATE_DIR}/module-groups.yaml"
```

### 3-9. W2 progress 초기화 및 W1 종료

확정된 Core 목록을 기준으로 W2 가 바로 이어서 실행될 수 있도록
`analysis-progress.json`과 `modules-traceability.md`를 초기화합니다.

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" init \
  --modules-file "${ANALYSIS_DIR}/analysis-notes/module-priority-reviewed.md" \
  --output-dir "${ANALYSIS_DIR}"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-end \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W1 \
  --coding-agent "claude-code"
```

완료 조건:

- `${STATE_DIR}/analysis-progress.json` 생성
- `${STATE_DIR}/modules-traceability.md` 생성
- W1 runtime 기록 종료
- `${STATE_DIR}/module-groups.yaml` 생성

---

## Step 5: System Document Generation

### 5-1 ~ 5-8. SDD Chapter Generation (01~08)

Generate chapters 01 through 08 using the `code2spec-doc-generation` skill and corresponding templates.

### 5-9. IPC/ENUM Catalog Generation

Generate `09-ipc-enum-catalog.md` using the `.ipc_enum_template.md` template.

**Primary data source: LLM extraction results** (from Step 3-1e):

1. **LLM ENUM results** — `${ANALYSIS_DIR}/llm-extraction/llm-enum-results.json`

   - Populates: ENUM Definitions section
   - Fields: name, values, type, source

2. **LLM Constant results** — `${ANALYSIS_DIR}/llm-extraction/llm-constant-results.json`

   - Populates: Constant Definitions section, Error Code Catalog section
   - Fields: name, value, type, usage_context, source
   - Error codes: Filter where `type == "error_code"` or name matches `EXIT_*`, `ERROR_*`, `ERR_*`

3. **LLM IPC results** — `${ANALYSIS_DIR}/llm-extraction/llm-ipc-results.json`
   - Populates: IPC Mechanism Summary section, Message ID Catalog section, Signal/Event Mapping section
   - Fields: mechanism, source_component, target_component, data, source

**Supplementary data sources** (fill gaps not covered by LLM):

4. AST `graph-raw.md` — Enum Definitions and Constant Definitions sections
5. Direct source code analysis via `search_files` for patterns LLM may have missed
6. IPC data from `tree-sitter-output/ipc-from-ast-extracted.json`

**Section population order** (LLM data first, then supplementary):

| Section               | Primary Source                                                | Supplementary Source             |
| --------------------- | ------------------------------------------------------------- | -------------------------------- |
| ENUM Definitions      | llm-enum-results.json                                         | graph-raw.md enum nodes          |
| Message ID Catalog    | llm-ipc-results.json (filter by mechanism)                    | search*files for MSG*_/OPCODE\__ |
| Constant Definitions  | llm-constant-results.json (filter type != error_code)         | graph-raw.md constant nodes      |
| Signal/Event Mapping  | llm-ipc-results.json (filter mechanism == broadcast_receiver) | search_files for on*/handle*     |
| Error Code Catalog    | llm-constant-results.json (filter type == error_code)         | search*files for ERR*_/EXIT\__   |
| IPC Mechanism Summary | llm-ipc-results.json                                          | ipc-from-ast-extracted.json      |

**All entries MUST include `[Source: file:line]` citation** — zero inference compliance.

Output: `<output-dir>/09-ipc-enum-catalog.md`

### 5-10. FR Index Generation

Generate FR index using the `code2spec-functional-requirement` skill.

Output: `<output-dir>/functional-requirements/index.md`
