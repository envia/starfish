---
name: code2spec-modules
description: "Run W2 module analysis: Module Design Cards, FR docs, progress tracking, and spec cache updates."
metadata:
  code-skills:
    id: code2spec/code2spec-modules
---

# Claude Code Skill: code2spec-modules

> This skill is generated from the code2spec workflow markdown for Claude Code.
> Shared templates are installed under `.claude/code2spec/templates/`; Python tools are installed under `.code2spec-tools/`.
> Installed tool build metadata is recorded at `.code2spec-tools/build-info.json`.

# Workflow: code2spec-modules (W2)

**Workflow format**: 1
**Tool version**: install/runtime resolved (`.code2spec-tools/build-info.json`)
**마지막 수정**: 2026-04-21

Core 모듈 심층 분석 → Module Design Card + FR 문서 생성.
**청크 단위 처리로 중단/재개 가능.**

> **W2가 FR·모듈 트리 전체를 소유한다**: W1은 `functional-requirements/`·`modules/`를 만들지 않는다.
> W2가 디렉토리 생성부터 개별 문서(`modules/<m>.md`·`functional-requirements/<m>-fr.md`)와
> **인덱스**(`modules/README.md`·`functional-requirements/index.md`)까지 모두 생성한다. 인덱스는
> 실제 생성된 모듈/FR을 나열하며, 청크 완료마다(또는 W2 종료 시) 최신화한다.

**선행 조건**: `code2spec-discovery` (W1) 완료 — `.analysis/state/delta/analysis-progress.json` 존재
**다음 워크플로우**: `code2spec-finalize` (W3)

> **deep-wiki 인용 근거 (Target B)**: Module Design Card·FR 문서의 백틱 deep-link 인용은 W1이 생성한
> `${OUTPUT_DIR}/.ast/api.json`(심볼 라인/시그니처)과 `${OUTPUT_DIR}/repo.json`의 `deepLink.base`(host별
> base URL)를 근거로 작성합니다. 인용 스타일·`Relevant source files` 블록 규율은 `functional-requirement`
> 스킬과 템플릿(PR5)을 따릅니다. 이 문서들은 W3의 wiki 검증 파이프라인(Step 2-W)에서 SDD 챕터와 동일하게 검증됩니다.

---

## 🚀 AI 자동 실행 지침 — 워크플로우 제공 시

> **CRITICAL**: 사용자가 이 워크플로우 문서를 제공하고 /code2spec-modules 또는 W2 실행을 요청하면:
> 
> 1. **질문 없이 즉시 Step 1 부터 시작** — "What would you like me to do?" 같은 질문 금지
> 2. **W2 완전 완료 지침 준수** — 모든 pending 모듈을 한 번에 처리
> 3. **청크 단위 출력** — 개별 모듈 요약 금지, 청크 완료 후에만 요약
> 
> ```text
> 잘못된 예 (금지):
>   "You've provided the code2spec-modules workflow documentation but haven't specified a task..."
>   "Would you like me to: 1. Execute W2... 2. Analyze..."
>   "Module 1 completed. To continue, run..."
> ```
> 
> ```text
> 올바른 예:
>   "[W2 시작] code2spec-modules 워크플로우를 실행합니다."
>   "[Step 1/3] 재개 상태 확인 중..."
>   "[Chunk 1 완료] 10/28 모듈 처리됨"
> ```

---

## Path Variable Contract

W2는 W1과 같은 `<analysis-target-path>`를 사용합니다. W1이 `/repo/src`로 실행됐다면 W2 산출물도 `/repo/src/code2spec` 아래에 이어서 생성합니다.

```bash
WORKSPACE_ROOT="<installed-project-root>"      # .code2spec-tools, .code2spec-venv 위치
ANALYSIS_TARGET="<same-analysis-target-as-W1>"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
```

`${STATE_DIR}/code2spec-config.json`에 `workspace_root`, `analysis_target`, `output_root`가 있으면 그 값을 우선 확인합니다.
W2를 직접 실행할 때도 W1과 동일한 분석 대상 경로를 넘겨야 하며, repo root를 넘기면 scoped build와 산출물이 섞일 수 있습니다.

---

## 🚨 전역 AI 동작 원칙 — ⭐️ 필독 ⭐️

1. **약어 유추 절대 금지**: 코드·README 에 정의 없으면 원문 그대로
2. **코드 밖 상상 금지**: 폴더명·클래스명만 보고 목적·기능 추측 금지
3. **출처 표기 강제**: 모든 주장에 백틱 deep-link ``[`Sym`](src:path#L<n>)`` 필수. 인용할 심볼이 없으면 백틱 **파일명** 라벨 ``[`file.ext`](src:path#L<n>)``를 쓴다 — **`[출처]`처럼 백틱 없는 라벨은 금지**(검증에서 스킵되어 틀린 라인이 그대로 남는다). 라인은 `.ast/api.json`에서. host 접두사는 적지 않는다 — 렌더 시 `repo.json.deepLink.base`가 붙는다. 상세: [grounding-and-deep-links.md](../skills/code2spec-doc-generation/references/grounding-and-deep-links.md)
4. **정보 없으면**: `"코드에서 확인 불가"` 기재

---

## 🤖 AI 출력 행동 규칙 — W2 워크플로우 전용

> **중요**: 이 규칙은 W2 워크플로우 실행 중 AI 의 출력 빈도를 제어합니다.

### 청크 단위 출력 원칙

1. **개별 모듈 처리 중에는 요약 출력 금지**
   - 각 모듈을 처리할 때는 조용히 명령만 실행
   - 모듈 완료 후 즉시 요약 테이블 출력하지 않음
   - "To Continue W2" 같은 계속 진행 안내 출력 금지

2. **청크 완료 후에만 요약 출력**
   - `next-chunk` 명령으로 다음 청크를 가져온 후 처리
   - 청크 내 모든 모듈 (최대 10 개) 을 처리 완료한 후에만 요약 출력
   - 요약 형식:
     ```
     [Chunk N 완료] X/Y 모듈 처리됨
     
     | 모듈 | SDD Doc | FR Doc | 상태 |
     |------|---------|--------|------|
     | ...  | ...     | ...    | ✅   |
     ```

3. **워크플로우 완전 완료 시 최종 요약**
   - `next-chunk` 가 `ALL_DONE`을 반환할 때까지 계속
   - 최종 요약: 총 모듈 수, 생성된 파일 수, 소요시간
   - "To Continue W2" 출력 금지 — 한 번에 완료

### W2 완전 완료 지침

**CRITICAL**: 사용자가 W2 워크플로우를 앵커하면:
- **모든 pending 모듈을 한 번에 처리** — 중간에 중지 금지
- **`ALL_DONE`이 나올 때까지 계속** — 사용자가 수동으로 계속하라고 하지 않음
- **최종 요약만 출력** — 청크별 요약은 선택적

```text
올바른 예:
  [Chunk 1 완료] 10/28 모듈 처리됨
  [Chunk 2 완료] 20/28 모듈 처리됨
  [Chunk 3 완료] 28/28 모듈 처리됨
  
  [W2 완료] 총 28 개 모듈 처리 완료
  - Module Design Card: 28 개 생성
  - FR 문서: 28 개 생성
  - 소요시간: 45 분
```

```text
잘못된 예 (금지):
  모듈 1 처리 완료 → 요약 출력 ❌
  "To Continue W2, run the next command..." ❌
  모듈 2 처리 완료 → 요약 출력 ❌
```

---

## 단계 개요

| Step | 내용                              | 유형 |
| ---- | --------------------------------- | ---- |
| 1    | 재개 상태 및 실행 컨텍스트 확인   | 자동 |
| 2    | 청크 단위 모듈 분석 및 문서 생성  | 자동 |
| 3    | Traceability 반영 및 W2 종료 기록 | 자동 |

---

## Step 1: 재개 상태 및 실행 컨텍스트 확인

### 목표

W1 산출물을 읽어 W2를 안전하게 재개할 수 있는 상태인지 확인합니다.

### 작업 내용

1. `code-to-ast` CLI 사용 가능 여부 확인
2. `code2spec-config.json`에서 `ANALYSIS_SCOPE` 로드
3. `module-groups.yaml` 존재 여부 확인 (없으면 W1 재분석 필요)
4. progress tracker 상태 확인
5. W2 시작 시간 기록

### 실행 명령

```bash
WORKSPACE_ROOT="<installed-project-root>"
ANALYSIS_TARGET="<same-analysis-target-as-W1>"
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" --help

ANALYSIS_SCOPE=$(${PYTHON} -c "import json; print(json.load(open('${STATE_DIR}/code2spec-config.json'))['analysis_scope'])")

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-start \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W2 \
  --coding-agent "claude-code"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" status \
  --output-dir "${ANALYSIS_DIR}"
```

### Delta progress 재개/복구 케이스 처리

정상적인 delta batch는 `/code2spec-delta` 내부 embedded phase에서 모듈 재생성을 끝냅니다.
다만 중단 복구나 레거시 handoff로 본 W2를 직접 실행하는 경우,
`analysis-progress.json`에 `delta: true`가 있고 `pending: []`이면 청크 루프를 **완전히 건너뛰고 Step 3으로 점프**합니다.

```bash
DELTA_PENDING=$(${PYTHON} -c "import json; d=json.load(open('${STATE_DIR}/analysis-progress.json')); print(len(d.get('pending', [])) if d.get('delta') else -1)")
if [ "${DELTA_PENDING}" = "0" ]; then
  echo "[W2] Delta 모드 + pending=[]. 모듈 분석 건너뜀."
  # → Step 3으로 진행
fi
```

> 그 외 케이스(delta + pending≥1, 또는 비-delta 일반 실행)는 모두 동일하게 Step 2 청크 루프 진행.

### 모드 해석

사용자가 HITL 리뷰에서 승인한 모든 모듈이 Core로 분류되므로,
별도의 분석 범위 선택 없이 자동으로 전체 모듈에 대해 상세 분석을 수행합니다.

| ANALYSIS_SCOPE | 모드      | W2 분석 방식                                         |
| -------------- | --------- | ---------------------------------------------------- |
| 3              | 🟢 Detail | 전체 모듈 / Module Design Card + 전체 FR (자동 설정) |

> **모든 모듈이 Core로 분류됩니다.**
> 사용자가 HITL 리뷰에서 승인한 모듈 경계이므로 Core/Peripheral 분류를 생략합니다.
> ANALYSIS_SCOPE는 항상 3 (Detail)로 자동 설정됩니다.

### 완료 조건

- CLI 접근 가능
- ANALYSIS_SCOPE 로드 완료
- progress tracker 상태 확인 완료
- W2 시작 시간 기록 완료

---

## Step 2: 청크 단위 모듈 분석 및 문서 생성

### 목표

pending 모듈을 10개 이하 청크로 반복 처리하면서:

1. 모듈 분석
2. Module Design Card 생성
3. 필요 시 FR 생성
4. 완료 마킹

을 반복합니다.

### 반복 루프

```text
WHILE pending 모듈이 남아 있으면:
  1. next-chunk 조회
  2. 청크 내 각 모듈 분석
  3. 문서 생성
  4. 완료 마킹
  5. context-summary 업데이트
ALL_DONE이면 Step 3으로 이동
```

### 다음 청크 조회

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" next-chunk \
  --output-dir "${ANALYSIS_DIR}"
```

`ALL_DONE`가 나오면 반복 종료.

### 청크 내 각 모듈 처리

각 모듈에 대해 순서대로 수행:

모듈 그룹(예: `task-management`)이 분석 단위입니다.
`module-groups.yaml`에서 각 모듈의 파일 목록과 메타데이터를 로드하여 처리합니다.

##### A. 모듈 심층 분석

- `module-groups.yaml`에서 해당 모듈의 파일 목록 로드
- 모듈에 속한 **모든 파일**을 읽고 분석
- `code2spec-logic-extraction` → 비즈니스 로직·알고리즘 흐름 추출
- `code2spec-pattern-mapping` → 모듈 간 의존성·상태관리·데이터 흐름 매핑

##### A-IPC. Interface Candidate 필터링 및 컨텍스트 로드

> `.analysis/interface-candidates.json`이 존재하면 모듈 소스 파일 기반으로 후보를 필터링한 뒤, LLM 입력용 compact context만 생성합니다. 전체 JSON은 source of truth로만 유지하고 프롬프트에 직접 넣지 않습니다.
> 
> **파일이 없는 경우**: W1에서 interface_scanner 실패 또는 미실행 → Module Design Card 작성자가 코드를 직접 읽고 IPC를 식별합니다.

```bash
# interface-candidates.json 존재 확인
if [ -f "${ANALYSIS_DIR}/interface-candidates.json" ]; then
  echo "[IPC] interface-candidates.json found, filtering for module..."
  # module-groups.yaml에서 해당 모듈의 파일 목록을 읽어와 필터링
  PYTHONPATH="${WORKSPACE_ROOT}/.code2spec-tools" ${PYTHON} -c "
from interface_scanner.module_filter import filter_candidates_for_module, write_module_candidate_context
from interface_scanner.schema import CandidateCollection
import json, os, yaml
max_bytes = int(os.environ.get('CODE2SPEC_INTERFACE_CONTEXT_MAX_BYTES', '24000'))
collection = CandidateCollection.from_dict(json.load(open('${ANALYSIS_DIR}/interface-candidates.json')))
groups = yaml.safe_load(open('${STATE_DIR}/module-groups.yaml'))
for g in groups.get('modules', []):
  if g['name'] == '<module-name>':
    source_files = g.get('files', [])
    candidates = filter_candidates_for_module(collection, '<module-name>', source_files)
    context_path = write_module_candidate_context('${ANALYSIS_DIR}', '<module-name>', source_files, candidates, max_context_bytes=max_bytes)
    print(f'  [IPC] {len(candidates)} interface candidates found for module; compact context: {context_path}')
    break
"
else
  echo "[IPC] No interface-candidates.json found. LLM will identify IPC from source code."
  echo "      (Module Design Card IPC section must summarize source evidence only)"
fi
```

**Case 1: interface-candidates.json 존재**
필터링된 후보는 `${ANALYSIS_DIR}/interface-candidates/by-module/<module>.json` compact context로 저장하고, 이 파일만 Module Design Card의 `IPC / Message / Interface Contracts` 섹션 작성에 사용합니다. `truncated=true`이면 포함된 후보를 우선 요약하고 omitted count와 byte budget 초과를 명시합니다.

**Case 2: interface-candidates.json 미존재**
- 모듈별 compact context 파일 미생성
- Module Design Card 생성 시 작성자는 코드를 직접 읽어 Android Intent, EventBus, 메시지 큐 등 IPC 패턴을 식별합니다.
- 새로 식별한 protocol 후보는 문서 본문에 내부 검토 태그를 남기지 말고, 증거와 confidence만 사용자용 문장으로 요약합니다.
- IPC 없음이 확실하면 명시적으로 기재합니다.

> **W2 IPC 분석 입력 지침**:
> - 제공된 후보는 evidence-backed 입력으로만 사용합니다.
> - `verification`, `promotion`, `candidate`, `low`, `llm_suggested` 같은 내부 후보 상태값은 Module Design Card 본문에 그대로 쓰지 않습니다.
> - 소스 evidence 없이 후보를 confirmed contract로 승격하지 않습니다.
> - 새 protocol 후보를 발견하면 사용자용 요약 문장과 백틱 deep-link ``[`Sym`](src:path#L<n>)`` 근거로만 기록합니다.
> - React props callback, DOM 이벤트, local reducer, generic EventEmitter 호출은 cross-module/interface contract가 아니면 IPC로 처리하지 않습니다.

> **대용량 후보 방지 규칙**:
> - W2 LLM에는 전체 `.analysis/interface-candidates.json`을 넣지 않습니다.
> - 모듈별 compact context(`interface-candidates/by-module/<module>.json`)만 입력합니다.
> - 기본 compact context 크기는 24,000 bytes이며 `CODE2SPEC_INTERFACE_CONTEXT_MAX_BYTES`로 조정할 수 있습니다.
> - `truncated=true`이면 omitted 후보 수를 Module Design Card에 명시하고, 필요한 경우에만 overflow artifact를 확인합니다.

##### B. Module Design Card 생성

- 템플릿: `.module_design_card_template.md`
- 저장: `${OUTPUT_DIR}/modules/<module-name>.md` (예: `modules/task-management.md`)

**LLM 프롬프트 구성:**

템플릿을 기반으로 LLM 프롬프트를 작성할 때 다음을 포함하세요:

```markdown
## IPC / Message / Interface Contracts 입력 지시

### 입력 자료
- [compact context 있으면] `/.analysis/interface-candidates/by-module/<module>.json`
- [없으면] 모듈 소스 코드

### 분석 작업
1. 정적 분석 결과가 있으면:
   - 제공된 후보들을 검증하세요 (실제로 코드에 있는가?)
   - `verified` / `likely` 항목은 반드시 포함하세요
   - 새로운 IPC 발견 시 소스 evidence와 confidence를 남기세요

2. 정적 분석 결과가 없으면:
   - 코드를 읽고 모든 IPC를 찾으세요
   - Android: Intent, BroadcastReceiver, 서비스 간 통신
   - Node.js/Electron: ipcRenderer, ipcMain, EventEmitter, Worker threads
   - 웹: postMessage, WebSocket, EventBus, pub-sub 패턴
   - 기타: 메시지 큐, 커스텀 프로토콜 등
   - 동적 채널도 포함 (template/변수로 생성되는 채널)

3. 각 IPC 항목 기록:
   - **Action/Channel**: 메시지 타입명
   - **Role**: Sender / Receiver / Bidirectional
   - **Peer**: 상대 모듈/컴포넌트
   - **Type**: Intent / Event / API / Message / Broadcast 등
   - **Confidence**: HIGH / MEDIUM / LOW (근거 포함)
   - **Evidence**: 백틱 deep-link ``[`Sym`](src:path#L<n>)`` 형식

4. IPC 없음 처리:
   - "이 모듈은 다른 컴포넌트와의 동기/비동기 IPC가 없습니다."
   - 또는 "순수 데이터 처리 모듈로 내부 상태 관리만 수행합니다."

5. 설계상 의미 추가:
   - 이 IPC 패턴이 아키텍처에서 하는 역할 설명
   - 예: "느슨한 결합", "비동기 처리", "모듈 간 데이터 흐름 제어"

### Module Design Card 출력 계약
- 이 지시문, 입력 자료 목록, 작업 목록, 주의사항, 내부 후보 상태값을 문서 본문에 복사하지 마세요.
- `## IPC / Message / Interface Contracts` 섹션에는 최종 사용자용 요약만 작성하세요.
- 작성 형식:
  - 확인된 contract가 있으면 ``- <contract 요약>. [`Sym`](src:path#L<n>)``
  - 후보 수준이면 ``- 후보: <contract 요약>; confidence=<HIGH|MEDIUM|LOW>. [`Sym`](src:path#L<n>)``
  - IPC가 없으면 `- 이 모듈에서 cross-module IPC/message contract는 코드 내 식별 불가.`처럼 명시하세요.
- 내부 표현 금지: `LLM`, `프롬프트`, `템플릿`, `제공된 후보`, `정적 분석 결과가 있으면`, `코드를 직접 읽고`, `verification`, `promotion`, `candidate`, `llm_suggested`, `llm_identified`.

### 분류 주의사항
- React props callback, DOM 이벤트는 IPC 아님
- 일반 EventEmitter 호출도 cross-module이 아니면 IPC 아님
- confidence 근거 명시 필수
```

**생성 섹션:**

- **Module Boundary**: 모듈 경계 선정 근거 (rationale from module-groups.yaml)
- **Confidence**: LLM 식별 신뢰도 (confidence from module-groups.yaml)
- **Source Files**: 모듈에 속한 전체 파일 목록
- Public Interface (모듈 내 모든 파일의 공개 인터페이스 취합)
- Key Flow 다이어그램 (모듈 내·외부 흐름 모두 포함)
- Architectural Rules
- Dependencies (모듈 간 의존성 포함)
- Quick Navigation

FR Linkage는:

- 항상 Detail 모드이므로 FR 포함

##### C. FR 문서 생성

- 항상 전체 모듈 FR 생성 (Detail 모드 자동 설정)

저장 위치:

- `${OUTPUT_DIR}/functional-requirements/<module-name>-fr.md`

##### D. 모듈 완료 마킹 + spec-cache 갱신

모듈에 속한 **각 파일**마다 spec-cache entry를 생성해야
W-DELTA에서 변경 감지가 정상 동작합니다.

```bash
# 모듈 완료 마킹 (모듈 이름 사용)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" update \
  --output-dir "${ANALYSIS_DIR}" \
  --module "task-management" \
  --status done \
  --fr-doc "functional-requirements/task-management-fr.md" \
  --sdd-doc "modules/task-management.md"

# 모듈에 속한 각 파일에 대해 spec-cache 갱신
for src_file in src/contexts/TaskContext.tsx src/contexts/TaskProvider.tsx src/components/tasks/TaskItem.tsx; do
  ${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_cache.py" spec-update \
    --output-dir "${ANALYSIS_DIR}" \
    --file "${ANALYSIS_TARGET}/${src_file}" \
    --sdd-doc "modules/task-management.md" \
    --fr-doc "functional-requirements/task-management-fr.md" \
    --mode "${SESSION_MODE:-detail}" \
    --analysis-scope "${ANALYSIS_SCOPE:-3}" \
    --workspace-root "${ANALYSIS_TARGET}"
done
```

> **spec-cache.json 갱신 필수 조건**:
> - 각 파일마다 `spec-update` 실행
> - 출력에 `[ProgressTracker] spec-cache updated: ...` 메시지 확인
> - 모든 파일이 갱신되어야 모듈 완료 처리
> - **하나라도 실패 시**: 해당 모듈을 완료 처리하지 마세요. W-DELTA에서 변경 감지 실패
> 
> Light 모드에서 FR 문서를 생략한 경우 `--fr-doc ""` 로 호출하세요.
> Module Design Card 상단에 `> **Relevant source files**` 블록에 모듈 내 전체 파일을 deep-link로 나열하세요.
> **⚠️ 경로 표기 필수**: RSF 블록과 모든 deep-link 경로는 module-groups.yaml의
> **전체 상대경로**를 그대로 사용하세요. 파일명만 쓰면 품질 메트릭에서 broken으로 집계되고,
> build-deps-map이 환각으로 간주해 source-deps-map이 비어 delta 의존성 탐지가 실패합니다.

**W2 완료 필수 체크리스트**:
- ✅ `spec-update`는 W2의 필수 완료 조건입니다
- ✅ 각 모듈의 모든 파일마다 `update` 직후 반드시 `spec-update` 실행
- ✅ `[ProgressTracker] spec-cache updated: ...` 출력 확인
- ✅ 확인 후 다음 모듈로 진행
- ✅ 실패 시 해당 모듈 완료 마킹 중단, 에러 해결 후 재시도

### 청크 완료 후 context 요약 저장

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" append-context \
  --output-dir "${ANALYSIS_DIR}" \
  --pattern "확인된 주요 패턴 요약" \
  --dependencies "주요 의존성 요약"
```

### 완료 조건

- pending 청크가 모두 처리됨
- `modules/` 및 `functional-requirements/` 디렉토리와 개별 문서가 **W2에서** 생성됨 (W1은 만들지 않음)
- **인덱스 생성**: `modules/README.md` 및 `functional-requirements/index.md`가 실제 생성된 모듈/FR을 나열하도록 생성/최신화됨
- 모든 완료 마킹 반영됨
- `${STATE_DIR}/spec-cache.json` 생성됨
- 완료된 각 모듈마다 `spec-cache.json` entry가 존재함

---

## Step 3: Traceability 반영 및 W2 종료 기록

### 목표

모든 청크가 끝난 뒤 traceability를 정리하고 W2를 종료합니다.

### 작업 내용

1. `modules-traceability.md` 업데이트
   - 파일 경로
   - FR 링크
   - Module Design Card 링크
   - AST 분석 여부
2. W2 종료 시간 기록

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-end \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W2 \
  --coding-agent "claude-code"
```

### 완료 조건

- `analysis-progress.json`: pending = []
- `modules/`: Core 모듈별 Module Design Card 생성 완료
- `functional-requirements/`: 모듈별 FR 생성 완료 (Light 제외)
- `modules-traceability.md` 업데이트 완료

**→ 다음 단계: `code2spec-finalize` (W3) 실행**
