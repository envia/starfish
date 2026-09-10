---
name: code2spec-delta
description: "Run W-DELTA batch: update existing code2spec docs from changed source files and finalize outputs without invoking W2/W3 separately."
metadata:
  code-skills:
    id: code2spec/code2spec-delta
---

# Claude Code Skill: code2spec-delta

> This skill is generated from the code2spec workflow markdown for Claude Code.
> Shared templates are installed under `.claude/code2spec/templates/`; Python tools are installed under `.code2spec-tools/`.
> Installed tool build metadata is recorded at `.code2spec-tools/build-info.json`.

# Workflow: code2spec-delta (W-DELTA)

**Workflow format**: 1
**Tool version**: install/runtime resolved (`.code2spec-tools/build-info.json`)
**마지막 수정**: 2026-04-29

이미 한 번 W1+W2+W3를 완료한 프로젝트에서 **소스 변경분만 spec 문서에 반영**하기 위한 진입점.
전체 재실행 대신 변경된 파일에 해당하는 Module Design Card / FR 문서만 부분 재생성합니다.

**선행 조건**:

- 이전에 W1+W2+W3 완료 — `code2spec/.analysis/state/delta/spec-cache.json` 존재
- `code2spec/.analysis/state/delta/code2spec-config.json` 존재 (mode/scope 재사용)

**실행 방식**: 본 워크플로우는 단일 batch 진입점입니다.
사용자는 W-DELTA만 실행합니다. W-DELTA 내부에서 W2의 모듈 재생성 절차와 W3의 finalize 절차를 **embedded phase**로 수행하며,
`/code2spec-modules` 또는 `/code2spec-finalize` 워크플로우를 별도로 호출하지 않습니다.

---

## Path Variable Contract

W-DELTA는 이전 full build와 같은 scoped output을 재사용합니다.
`/repo/src`에서 W1+W2+W3를 수행했다면 delta도 `/repo/src/code2spec/.analysis/state/delta/spec-cache.json`을 기준으로 계산해야 합니다.

```bash
WORKSPACE_ROOT="<installed-project-root>"      # .code2spec-tools, .code2spec-venv 위치
ANALYSIS_TARGET="<same-analysis-target-as-full-build>"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
AST_DIR="${ANALYSIS_DIR}/cache/code-to-ast"
```

`${ANALYSIS_DIR}/state/delta/code2spec-config.json`에 `analysis_target`, `workspace_root`, `output_root`가 있으면 그 값을 우선 사용합니다.
`delta-plan`에는 반드시 `--repo "${ANALYSIS_TARGET}"`를 넘깁니다. scoped build에서 repo root를 넘기면 분석 대상 밖 파일이 `new`/`peripheral`로 섞일 수 있습니다.

---

## 🚨 전역 AI 동작 원칙 — ⭐️ 필독 ⭐️

1. **약어 유추 절대 금지**: 코드·README에 정의 없으면 원문 그대로
2. **코드 밖 상상 금지**: 폴더명·클래스명만 보고 목적·기능 추측 금지
3. **출처 표기 강제**: 모든 외부 소스 출처는 백틱 deep-link ``[`Sym`](src:path#L<n>)`` (host 접두사는 적지 않는다 — 렌더 시 `repo.json.deepLink.base`가 붙는다)
4. **정보 없으면**: `"코드에서 확인 불가"` 기재

---

## 단계 개요

| Step | 내용                                                            | 유형              | 담당    |
| ---- | --------------------------------------------------------------- | ----------------- | ------- |
| 1    | 사전 조건 확인 (spec-cache 존재)                                | 자동              | W-DELTA |
| 2    | AST export 재실행 (parse-cache 자동 활용)                       | 자동              | W-DELTA |
| 3    | Core manifest 갱신 + `delta-plan` 실행 → diff-plan.json         | 자동              | W-DELTA |
| 4    | 상세 diff 요약 표시 + 진행 confirm                              | Human-in-the-Loop | W-DELTA |
| 5    | removed 모듈 cleanup (docs/traceability/cache)                  | 자동              | W-DELTA |
| 6    | code2spec_progress init `--from-diff-plan`                      | 자동              | W-DELTA |
| 7    | embedded module regeneration phase (W2 프로토콜 내장)           | 자동              | W-DELTA |
| 8    | embedded finalize phase: interlink + quick-reference + deps-map | 자동              | W-DELTA |
| 9    | 품질 메트릭 계산                                                | 자동              | W-DELTA |
| 10   | W-DELTA 종료 기록 + history 업데이트                            | 자동              | W-DELTA |

---

## Step 1: 사전 조건 확인

### 목표

W-DELTA가 안전하게 실행될 수 있는 상태인지 검증. 캐시가 없거나 무효화된 경우 full rebuild 안내.

### 사용자 안내 계약 (LLM 필수 응답)

`spec-cache.json` 또는 `code2spec-config.json`이 없으면 shell 에러만 출력하고
조용히 종료하지 마세요. LLM은 사용자에게 자연어로 다음을 반드시 설명해야 합니다.

1. 현재 delta 분석을 진행할 수 없는 이유
   - delta 분석은 이전 full build의 `spec-cache.json`과 설정 파일이 필요합니다.
2. 사용자가 다음에 실행해야 할 순서
   - `/code2spec-discovery` → `/code2spec-modules` → `/code2spec-finalize`
3. full build 완료 후 다시 `/code2spec-delta`를 실행하면 변경분만 분석된다는 점
4. 이 상태에서는 `delta-plan`이나 module regeneration을 계속 실행하지 않는다는 점

권장 사용자 메시지:

```text
현재 프로젝트에는 delta 분석에 필요한 code2spec/.analysis/state/delta/spec-cache.json이 없습니다.
delta 분석은 이전 full build 결과와 설정을 기준으로 변경분을 계산하므로, 첫 실행에서는 사용할 수 없습니다.

먼저 /code2spec-discovery → /code2spec-modules → /code2spec-finalize 순서로 full build를 완료해 주세요.
그 후 /code2spec-delta를 다시 실행하면 변경된 소스에 해당하는 문서만 갱신할 수 있습니다.
```

### 실행 명령

```bash
WORKSPACE_ROOT="<installed-project-root>"
ANALYSIS_TARGET="<same-analysis-target-as-full-build>"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
AST_DIR="${ANALYSIS_DIR}/cache/code-to-ast"
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"

if [ ! -f "${ANALYSIS_DIR}/state/delta/spec-cache.json" ]; then
  echo "[ERROR] spec-cache.json 없음: delta 분석은 이전 full build 결과가 필요합니다."
  echo "[NEXT] /code2spec-discovery → /code2spec-modules → /code2spec-finalize 를 먼저 실행하세요."
  echo "[LLM] 사용자에게 delta 분석을 중단하는 이유와 위 full build 순서를 자연어로 설명하세요."
  exit 1
fi

if [ ! -f "${ANALYSIS_DIR}/state/delta/code2spec-config.json" ]; then
  echo "[ERROR] code2spec-config.json 없음: delta 분석은 이전 full build 설정이 필요합니다."
  echo "[NEXT] /code2spec-discovery → /code2spec-modules → /code2spec-finalize 를 먼저 실행하세요."
  echo "[LLM] 사용자에게 delta 분석을 중단하는 이유와 위 full build 순서를 자연어로 설명하세요."
  exit 1
fi

# 기존 설정 로드
ANALYSIS_SCOPE=$(${PYTHON} -c "import json; print(json.load(open('${ANALYSIS_DIR}/state/delta/code2spec-config.json'))['analysis_scope'])")
DOC_LANG=$(${PYTHON} -c "import json; print(json.load(open('${ANALYSIS_DIR}/state/delta/code2spec-config.json'))['doc_lang'])")
ANALYSIS_TARGET=$(${PYTHON} -c "import json; d=json.load(open('${ANALYSIS_DIR}/state/delta/code2spec-config.json')); print(d.get('analysis_target', '${ANALYSIS_TARGET}'))")
WORKSPACE_ROOT=$(${PYTHON} -c "import json; d=json.load(open('${ANALYSIS_DIR}/state/delta/code2spec-config.json')); print(d.get('workspace_root', '${WORKSPACE_ROOT}'))")
OUTPUT_DIR=$(${PYTHON} -c "import json; d=json.load(open('${ANALYSIS_DIR}/state/delta/code2spec-config.json')); print(d.get('output_root', '${OUTPUT_DIR}'))")
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
AST_DIR="${ANALYSIS_DIR}/cache/code-to-ast"
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
SESSION_MODE="detail"

# 모듈 경계 정보 확인 (필수 — 없으면 레거시 Physical 모드 산출물)
MODULE_GROUPS_FILE="${ANALYSIS_DIR}/state/delta/module-groups.yaml"
if [ ! -f "${MODULE_GROUPS_FILE}" ]; then
  echo "[ERROR] module-groups.yaml 없음: 레거시(Physical 모드) 산출물이거나 Module Discovery 미실행 상태입니다."
  echo "[NEXT] /code2spec-discovery → /code2spec-modules → /code2spec-finalize 로 전체 재분석을 먼저 실행하세요."
  echo "[LLM] 사용자에게 delta 분석을 중단하는 이유와 위 전체 재분석 순서를 자연어로 설명하세요."
  exit 1
fi
echo "[W-DELTA] module-groups.yaml 확인 완료"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" session-init \
  --output-dir "${ANALYSIS_DIR}" \
  --target-path "${ANALYSIS_TARGET}" \
  --workspace-root "${WORKSPACE_ROOT}" \
  --analysis-target "${ANALYSIS_TARGET}" \
  --output-root "${OUTPUT_DIR}" \
  --mode "${SESSION_MODE}" \
  --run-type delta \
  --coding-agent "claude-code"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-start \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W-DELTA \
  --coding-agent "claude-code"
```

### 완료 조건

- spec-cache.json, code2spec-config.json 존재 확인
- ANALYSIS_SCOPE / DOC_LANG / SESSION_MODE 로드 완료
- runtime-stats.json: `run_type=delta`, workflow=`W-DELTA`로 새 세션 시작
- spec-cache/config 누락 시 LLM이 사용자에게 full build 필요성과 실행 순서를 설명하고 W-DELTA를 중단

---

## Step 2: AST export 재실행

### 목표

소스 코드에 대한 최신 AST 산출. 이미 [tools/cache_manager.py](../../../tools/cache_manager.py)의 parse-cache가 file_hash 비교로 변경된 파일만 다시 파싱합니다 — 별도 처리 불필요.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" export \
  --repo "${ANALYSIS_TARGET}" \
  --format both \
  --output-dir "${AST_DIR}"
```

### 완료 조건

- `${AST_DIR}/graph-raw.json` 갱신
- `${AST_DIR}/.cache/parse-cache.json` 생성/갱신 확인
- "Cache: N cached, M changed/new" 메시지로 캐시 효과 확인

---

## Step 3: delta-plan 실행

### 목표

최신 Core 목록과 소스 파일을 기존 cache/deps와 비교하여
`unchanged` / `changed` / `promoted` / `dependent_changed` / `removed` /
`peripheral_new` / `peripheral_changed` / `moved`로 분류하고 `diff-plan.json` 생성.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" save-core-manifest \
  --output-dir "${ANALYSIS_DIR}" \
  --priority-file "${ANALYSIS_DIR}/analysis-notes/module-priority-reviewed.md" \
  --workspace-root "${ANALYSIS_TARGET}" \
  --analysis-scope "${ANALYSIS_SCOPE}" \
  --mode "${SESSION_MODE}" \
  --module-groups "${MODULE_GROUPS_FILE}"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/cli.py" delta-plan \
  --repo "${ANALYSIS_TARGET}" \
  --analysis-dir "${ANALYSIS_DIR}" \
  --module-groups "${MODULE_GROUPS_FILE}"
```

### delta-plan 동작 (모듈 단위 집계)

`--module-groups`가 제공되면, 파일 단위 diff 결과를 모듈 단위로 집계합니다:

- 모듈 내 **1개 파일이라도 changed** → 해당 모듈 전체를 `changed`로 분류
- 모듈 내 **1개 파일이라도 removed** → 해당 모듈을 `changed`로 분류 (모듈 전체 재생성)
- 모듈 내 **모든 파일 unchanged** → `unchanged`
- **신규 파일**이 모듈에 속하면 → 해당 모듈 `changed`
- `promoted`/`peripheral_*` 카테고리는 발생하지 않음 (모든 모듈이 Core)

### 출력 파일

- `${STATE_DIR}/diff-plan.json`

### 완료 조건

- diff-plan.json 생성됨
- stdout에 "Unchanged / Changed / Promoted / Dependent Changed / Removed / Peripheral / Moved" 요약 출력

---

## Step 4: diff 확인 (Human-in-the-Loop)

### 목표

사용자에게 변경 분류 결과를 보여주고 진행 여부 확인. **무효화(`invalidated=true`)** 또는 **변경 없음(needs_work=false)** 분기 처리.

### 실행 명령

```bash
${PYTHON} - <<PY
import json, pathlib
plan = json.loads(pathlib.Path("${STATE_DIR}/diff-plan.json").read_text(encoding="utf-8"))
s = plan["summary"]
print(f"  Unchanged: {s['unchanged']}")
print(f"  Changed:   {s['changed']}")
print(f"  New:       {s['new']}")
print(f"  Promoted:  {s.get('promoted', 0)}")
print(f"  Dependent: {s.get('dependent_changed', 0)}")
print(f"  Removed:   {s['removed']}")
print(f"  Peripheral new/changed: {s.get('peripheral_new', 0)} / {s.get('peripheral_changed', 0)}")
print(f"  Moved:     {s.get('moved', 0)}")
if plan.get("invalidated"):
    print(f"\n  ⚠ INVALIDATED: {plan.get('invalidated_reason','')}")
PY
```

### 사용자에게 제시

```text
[W-DELTA Step 4] 변경 분류 결과를 확인합니다.

  Unchanged: N
  Changed:   M  ← Module Card / FR 재생성 대상
  Promoted:  P  ← 새 Core 진입으로 신규 생성 대상
  Dependent: D  ← 참조 소스 변경으로 재생성 대상
  New:       K  ← 하위 호환/명시 신규 생성 대상
  Removed:   L  ← Module Card / FR 삭제 대상
  Moved:     R  ← 새 경로 기준 재생성 + 이전 cache/doc 정리 대상
  Peripheral: PN new / PC changed  ← 기본 제외, 필요 시 후속 확장 대상

진행 옵션:
  1) 진행 (Standard) — changed/promoted/dependent/new/moved는 LLM 재생성, removed는 삭제
  2) 취소 — 아무것도 변경하지 않고 종료

선택: __________
```

### 분기 처리

- **invalidated=true**: "캐시 무효화. /code2spec-discovery 부터 full rebuild를 권장합니다." 안내 후 종료.
- **needs_work=false (M+K+P+D+R+L=0)**: "변경 사항 없음. 진행 시 quick-reference/source-deps-map/history만 갱신됩니다. 진행하시겠습니까?" 확인.
- **취소**: diff-plan.json은 유지, 종료.

### 완료 조건

- 사용자 진행 동의 또는 취소

---

## Step 5: removed 모듈 cleanup

### 목표

삭제된 소스에 해당하는 `modules/<name>.md`, `functional-requirements/<name>-fr.md`, traceability 행, spec-cache 항목을 한꺼번에 정리. **W3에 delta 여부를 강요하지 않기 위해 W-DELTA가 직접 처리**.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_cache.py" cleanup-removed \
  --output-dir "${ANALYSIS_DIR}" \
  --diff-plan "${STATE_DIR}/diff-plan.json"
```

removed가 0건이면 "No removed modules to clean up." 출력 후 종료 (정상).

### 완료 조건

- 삭제 대상 docs 모두 제거
- modules-traceability.md에서 해당 행 제거
- spec-cache.json에서 해당 항목 제거

---

## Step 6: code2spec_progress init `--from-diff-plan`

### 목표

W-DELTA의 embedded module regeneration phase가 changed+new+promoted+dependent_changed+moved 모듈만 처리하도록 pending 큐를 구성합니다.
unchanged 모듈은 `completed`로 분류돼 regeneration phase가 자연스럽게 건너뜁니다.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" init \
  --output-dir "${ANALYSIS_DIR}" \
  --from-diff-plan "${STATE_DIR}/diff-plan.json"
```

### 완료 조건

- analysis-progress.json: `delta: true`, `pending = changed + new + promoted + dependent_changed + moved`, `completed = unchanged`
- 출력: "Initialized (delta): N pending (regen targets), M skipped (unchanged)"

---

## Step 7: embedded module regeneration phase

### 목표

`/code2spec-modules`를 별도 호출하지 않고, W-DELTA 내부에서 W2와 동일한 모듈 생성 계약을 수행합니다.
처리 대상은 Step 6에서 만든 `pending = changed + new + promoted + dependent_changed + moved`만입니다.
`unchanged` 모듈의 기존 `modules/*.md` / `functional-requirements/*-fr.md`는 수정하지 않습니다.

### 실행 원칙

- `analysis-progress.json`의 `pending`이 0이면 본 phase를 건너뜁니다.
- pending이 있으면 `code2spec_progress next-chunk`로 청크를 가져와 각 모듈을 분석합니다.
- 각 모듈 산출물은 W2와 동일하게 생성합니다:
  - `modules/<module>.md` Module Design Card
  - `functional-requirements/<module>-fr.md`
  - Module Design Card 상단(H1 아래)에 `> **Relevant source files**` 블록 명시
  - 모든 코드 주장에 백틱 deep-link ``[`Sym`](src:path#L<n>)`` 출처 표기
- 각 모듈 완료 직후 `update`와 `spec-update`를 호출하여 traceability/spec-cache를 갱신합니다.
- 이 phase는 **W-DELTA의 일부**입니다. `workflow-start/end --workflow W2`를 호출하지 않습니다.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" status \
  --output-dir "${ANALYSIS_DIR}"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" next-chunk \
  --output-dir "${ANALYSIS_DIR}"
```

#### 모듈 단위 재생성

모듈 그룹(예: `task-management`)이 재생성 단위입니다.
`module-groups.yaml`에서 각 모듈의 파일 목록을 로드하여 처리합니다.

각 pending 모듈 문서 생성 후:

```bash
# 모듈 완료 마킹 (모듈 이름 사용)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" update \
  --output-dir "${ANALYSIS_DIR}" \
  --module "<module-name>" \
  --status done \
  --fr-doc "functional-requirements/<module-name>-fr.md" \
  --sdd-doc "modules/<module-name>.md" \
  --ast "✅"

# 모듈에 속한 각 파일에 대해 spec-cache 갱신
for src_file in <module-files>; do
  ${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_cache.py" spec-update \
    --output-dir "${ANALYSIS_DIR}" \
    --file "${ANALYSIS_TARGET}/${src_file}" \
    --sdd-doc "modules/<module-name>.md" \
    --fr-doc "functional-requirements/<module-name>-fr.md" \
    --mode "${SESSION_MODE}" \
    --analysis-scope "${ANALYSIS_SCOPE}" \
    --workspace-root "${ANALYSIS_TARGET}"
done
```


### 완료 조건

- `code2spec_progress status` 기준 pending=0
- changed/new/promoted/dependent_changed/moved 대상의 Module Card / FR 문서 갱신 완료
- spec-cache.json이 새 hash 및 Source Files 의존성을 반영
- modules-traceability.md가 갱신 대상 행만 patch

---

## Step 8: embedded finalize phase

### 목표

`/code2spec-finalize`를 별도 호출하지 않고, W-DELTA 내부에서 finalize 산출물을 갱신합니다.
removed/moved cleanup은 Step 5에서 끝났으므로, 여기서는 남아 있는 문서들의 링크/요약/의존성 맵을 최신화합니다.

### 작업 내용

1. `modules-traceability.md`는 전체 재생성하지 말고 Step 7에서 patch된 행을 유지합니다.
2. `README.md` TOC와 `code2spec-quick-reference.md`를 현재 `modules/`, `functional-requirements/`, SDD 문서 상태 기준으로 재생성합니다.
3. 모든 Module Design Card를 순회해 `source-deps-map.json`을 갱신합니다.
4. Delta 안내 문구를 종료 요약에 포함합니다.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" build-deps-map \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}"
```

### 완료 조건

- code2spec/README.md 갱신
- code2spec/code2spec-quick-reference.md 갱신
- code2spec/.analysis/state/delta/source-deps-map.json 갱신
- 시스템 SDD(01~08)는 자동 갱신 대상이 아님을 종료 요약에 표시

---

## Step 9: 품질 메트릭 계산 및 Acceptance Gate

### 목표

갱신된 문서의 품질을 정량적으로 평가하여 `quality-metrics.json`에 저장한다.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" compute-metrics \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}"

set +e
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" quality-gate \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}" \
  --run-type delta
QUALITY_GATE_EXIT=$?
set -e

if [ "${QUALITY_GATE_EXIT}" -eq 2 ]; then
  echo "[QUALITY_GATE] FAIL 또는 metrics 누락. .analysis/reports/quality/quality-issues.json 확인 필요."
elif [ "${QUALITY_GATE_EXIT}" -ne 0 ]; then
  exit "${QUALITY_GATE_EXIT}"
fi
```

### 완료 조건

- quality-metrics.json 생성 완료
- quality-issues.json 생성 완료 (`PASS`/`WARN`/`FAIL`)
- 4개 메트릭 값이 0.0~1.0 범위 내

> `quality-gate`가 `FAIL` 또는 `WARN`을 반환해도 자동 repair/regeneration은 수행하지 않는다. `.analysis/reports/quality/quality-issues.json`은 진단 기록으로 보존하고, `finalize-history`가 history.md에 메트릭과 Quality Gate 상태를 기록한다.
>
> 재생성이 필요해 보이는 경우 사용자에게 별도 알림만 제공한다. 실제 repair/regeneration은 사용자가 명시적으로 승인하거나 별도 workflow를 실행할 때만 수행한다.
>
> `finalize-history`(Step 10)는 내부적으로 `.analysis/reports/quality/quality-metrics.json`이 존재하면 history.md에 메트릭 섹션을 자동 추가한다.

---

## Step 9-W: Code Wiki 재검증 + 스냅샷 갱신 (deep-wiki, Target B)

### 목표

delta 재생성으로 SDD 문서가 갱신됐으므로, deep-wiki `spec-cache.json` 스냅샷을 현재 상태로 전진시키고
`repo.json.qualityScore`를 다시 계산한다. base delta-plan(Step 3)이 재생성 대상을 이미 구동하므로
**별도의 wiki diff는 W-DELTA에 넣지 않는다** — 여기서는 W3와 동일한 finalize만 재실행한다.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/wiki_cli.py" finalize \
  --repo "${ANALYSIS_TARGET}" \
  --output-dir "${OUTPUT_DIR}"
```

- `write-wiki-metadata` → `spec-cache-manager --action mark-all`(새 기준점) → `validate-generated-wiki --tier full`
- `.ast`/`repo.json`이 없으면(첫 delta 이전 full build가 구버전) W1의 `wiki_cli.py prepare --skip-export --skip-discover`를 먼저 1회 수행한다.

### 완료 조건

- `${STATE_DIR}/spec-cache.json` 이 현재 git 상태로 갱신됨
- `${OUTPUT_DIR}/repo.json.qualityScore` 재계산됨
- hard gate 실패 시 `.trust` 리포트 확인 후 문서 보정

> **standalone wiki delta(참고)**: code2spec W-DELTA 없이 wiki만 독립 운용할 때는
> `wiki_cli.py diff`가 spec-cache 대비 변경을 `${STATE_DIR}/wiki-diff-plan.json`(base `diff-plan.json`과
> 충돌 없는 별도 파일)로 산출하고, `parse_wiki_rsf.py`가 각 페이지의 `Relevant source files`와 교차해
> 재생성 대상을 판정한다. code2spec 파이프라인 안에서는 base delta-plan이 이 역할을 대신한다.

---

## Step 10: W-DELTA 종료 기록 + history 업데이트

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-end \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W-DELTA \
  --coding-agent "claude-code"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" finalize-history \
  --output-dir "${ANALYSIS_DIR}" \
  --note "W-DELTA batch 완료"
```

`history.md`는 전체 실행을 훑어볼 수 있는 `## Summary` 테이블에 delta 행을 추가하고,
`## Workflow Details`에 `W-DELTA` 소요시간 상세를 기록합니다.

### 종료 요약

```text
🎉 code2spec delta 완료!

갱신 범위:
- changed/new/promoted/dependent_changed/moved 모듈의 Module Card / FR 문서
- removed/moved 이전 경로의 docs/traceability/cache 정리
- README.md, code2spec-quick-reference.md, source-deps-map.json, history.md

⚠ Delta 모드 안내:
- 이번 실행은 module-level만 갱신했습니다.
- 시스템 SDD(01~08)는 자동 갱신 대상이 아닙니다 — 큰 아키텍처 변경이 있었다면 /code2spec-discovery 부터 full rebuild를 권장합니다.
```

---

## 알려진 제약 (사용자 안내 필요)

- **간접 의존 변경은 Source Files/deps-map에 기록된 경우 반영**: Module Card가 참조 파일을 `Relevant source files` 블록 또는 deep-link 인용으로 기록하지 않았다면 stale 가능.
- **시스템 SDD(01~08-\*.md)는 자동 갱신 안 됨**: delta 모드에서는 module-level만 갱신. 시스템 문서가 stale일 수 있다는 경고를 W-DELTA 종료 시 출력.
- **파일 rename/move**: 동일 hash move는 `moved`로 감지하되 새 경로 기준 재생성합니다.
- **spec-cache 무효화**: SPEC_CACHE_VERSION 불일치 시 cache load 단계에서 차단되고 full rebuild가 안내됩니다.

---

## Step 11: AX Artifact snapshot upload (Human-in-the-Loop)

W-DELTA에서는 download를 수행하지 않습니다. `${OUTPUT_DIR}` 전체를 AX Artifact snapshot으로 선택적으로 업로드합니다.

### 11-1. 출력 경로 안전 검사

```bash
OUTPUT_DIR_ABS=$("${PYTHON}" -c "import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())" "${OUTPUT_DIR}")
AX_ARTIFACT_UPLOAD_STATUS="missing-output"
```

canonical absolute path를 사용하며 `missing-output`은 upload를 건너뜁니다.

### 11-2. MCP 및 Git/Gerrit context 가용성 확인

사용 가능한 MCP 도구 목록에서 `ax-artifacts` 서버의 `ax_artifacts_upload` 도구를 찾습니다. 서버 이름과 도구의 논리 이름은 정확히 일치시키되, 클라이언트가 생성한 긴 qualified alias는 하드코딩하지 않습니다. 도구가 없으면 MCP 호출 없이 `skipped-no-mcp`로 기록하고 로컬 성공을 유지합니다.

```bash
GIT_CONTEXT_JSON=$(${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/git_context.py" --repo "${ANALYSIS_TARGET}" --format json)
```

- `remote_url`: `GIT_CONTEXT_JSON.remote_url`
- `branch`: `GIT_CONTEXT_JSON.branch`
- `commit_id`: `GIT_CONTEXT_JSON.commit_id`
- Git context가 불완전하면 `skipped-no-git-context`로 기록하고 HITL과 MCP 호출을 건너뜁니다.

### 11-3. 사전 HITL

```text
[W-DELTA Step 11] Code2Spec 결과를 AX Artifact에 업로드하시겠습니까?
- Upload directory: ${OUTPUT_DIR_ABS}
- coding_agent: claude-code
- agent_tool: skill:code2spec
1) 업로드
2) 건너뛰기
code2spec 디렉토리 전체 (`.analysis/`, cache, reports, state 포함)
```

### 11-4. MCP upload와 snapshot 최종 확인

`coding_agent`는 설치 시 현재 AI coding assistant에 맞게 렌더링된 `claude-code` 값을 그대로 사용합니다. 실행 중에 LLM이 이 값을 다시 추론하거나 변경하지 않습니다.

`ax-artifacts` 서버의 `ax_artifacts_upload` 도구를 호출할 때 `${OUTPUT_DIR_ABS}`와 Git context 외에 다음 metadata를 전달합니다.

- `coding_agent`: `claude-code` (설치 시 확정된 고정값)
- `channel`: `code2spec` (항상 이 고정값 사용)
- `agent_tool`: `skill:code2spec` (항상 이 고정값 사용)

최종 확인 후에만 명령을 실행하며 결과는 `uploaded`, `user-skipped`, `failed-continued` 중 하나로 기록합니다.

`ax_artifacts_upload`가 제공하는 현재 입력 schema만 사용하되 `channel`은 반드시 `code2spec`, `agent_tool` 값은 반드시 `skill:code2spec`으로 고정합니다.
