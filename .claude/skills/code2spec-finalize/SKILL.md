---
name: code2spec-finalize
description: "Run W3 finalize: interlinking, quick reference, history, and dependency-map refresh."
metadata:
  code-skills:
    id: code2spec/code2spec-finalize
---

# Claude Code Skill: code2spec-finalize

> This skill is generated from the code2spec workflow markdown for Claude Code.
> Shared templates are installed under `.claude/code2spec/templates/`; Python tools are installed under `.code2spec-tools/`.
> Installed tool build metadata is recorded at `.code2spec-tools/build-info.json`.

# Workflow: code2spec-finalize (W3)

**Workflow format**: 1
**Tool version**: install/runtime resolved (`.code2spec-tools/build-info.json`)
**마지막 수정**: 2026-04-22

문서 간 연결 → Quick Reference 생성 → **Code Wiki 검증(`wiki_cli.py finalize`, 필수)** → History 업데이트.
**토큰 부담 낮음. 완주 보장.**

> **⚠️ W3는 Step 2(base 4지표)에서 끝나지 않는다.** Step 2-W의 `wiki_cli.py finalize`(deep-wiki 8 hard gate +
> `verification-report.md` + 신뢰 배지)를 **반드시 실행**한 뒤 Step 3으로 간다.

**선행 조건**: `code2spec-modules` (W2) 완료 — modules/ + functional-requirements/ 존재

---

## Path Variable Contract

W3는 W1/W2와 같은 `<analysis-target-path>`의 scoped output을 마무리합니다.
전체 프로젝트 분석이면 `/repo/code2spec`, `src` scoped 분석이면 `/repo/src/code2spec`에 README, quick reference, history를 생성합니다.

```bash
WORKSPACE_ROOT="<installed-project-root>"      # .code2spec-tools, .code2spec-venv 위치
ANALYSIS_TARGET="<same-analysis-target-as-W1>"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
```

`${STATE_DIR}/code2spec-config.json`의 `analysis_target`/`output_root`와 일치하는지 먼저 확인합니다.

---

## 🚨 전역 AI 동작 원칙 — ⭐️ 필독 ⭐️

1. **약어 유추 절대 금지**: 코드·README에 정의 없으면 원문 그대로
2. **출처 표기 강제**: 모든 주장에 백틱 deep-link ``[`Sym`](src:path#L<n>)`` 필수(host 접두사는 적지 않는다 — 렌더 시 `repo.json.deepLink.base`가 붙는다).
3. **정보 없으면**: `"코드 내 식별 불가"` 기재

---

## 단계 개요

| Step | 내용                                       | 유형 |
| ---- | ------------------------------------------ | ---- |
| 1    | Interlinking 및 Quick Reference 생성       | 자동 |
| 2    | 품질 메트릭 계산 및 Acceptance Gate        | 자동 |
| 2-B  | Broken Source Link Repair (FAIL 시 1회 패치) | 자동 |
| 2-W  | **Code Wiki 검증 (⭐️필수): `wiki_cli.py finalize` + hard gate 교정 루프 + `verification-report.md`** | 자동 |
| 3    | History 업데이트 및 W3 종료                | 자동 |

> **⚠️ Step 2는 base 4지표일 뿐 W3의 끝이 아니다.** Step 2 다음 **Step 2-W(Code Wiki 검증)를 반드시 실행**해야
> deep-wiki 8 hard gate·`repo.json.qualityScore`·`verification-report.md`·신뢰 배지가 생성된다. Step 2만 하고
> Step 3(History)으로 넘어가는 것은 **W3 미완성**이다.

---

## Step 1: Interlinking 및 Quick Reference 생성

### 목표

W3 첫 단계에서 아래를 한 번에 생성합니다.

1. 문서 간 상호 링크
2. README.md (TOC)
3. code2spec-quick-reference.md (자동 생성)
4. W3 시작/종료 시간 기록
5. 종료 요약 (Quick Reference 용도 안내)

### W3 시작 시간 기록

```bash
WORKSPACE_ROOT="<installed-project-root>"
ANALYSIS_TARGET="<same-analysis-target-as-W1>"
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-start \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W3 \
  --coding-agent "claude-code"
```

### 문서 간 Interlinking

`code2spec-interlinking` skill로 아래 연결을 수행합니다.

- SDD 문서(01~08) ↔ modules/\*.md
- modules/_.md ↔ functional-requirements/_-fr.md
- modules-traceability.md ↔ 전체 문서
- diagrams/\*.mmd ↔ 관련 SDD 섹션

> **Delta 상태에서 finalize만 별도 실행하는 레거시/복구 케이스**: `analysis-progress.json`에 `delta: true`가 있으면 `modules-traceability.md`를 **전체 재생성하지 말고 행 단위 patch** 상태를 유지하세요. unchanged 모듈의 행은 손대지 않고, changed/new/promoted/dependent_changed/moved 모듈의 행만 status/링크를 확인합니다 (`code2spec_progress update` 가 행을 직접 갱신함). removed/moved 이전 경로는 W-DELTA cleanup 단계에서 이미 제거됐으므로 추가 작업 불필요.

각 문서 상단 네비게이션 예시:

```markdown
**관련 문서**: [02-architecture.md](02-architecture.md) | [modules/useService.md](modules/useService.md)
```

### README.md 생성

저장: `${OUTPUT_DIR}/README.md`

포함 내용:

- 시스템 문서 TOC
- Core 모듈 목록
- 분석 결과 링크

### code2spec-quick-reference.md 생성

저장: `${OUTPUT_DIR}/code2spec-quick-reference.md` (code2spec 디렉토리 내)

> **Delta 모드에서도 quick-reference는 항상 재생성합니다** (변경 모듈 수와 무관). 핵심 모듈 위치 / 기능 수정 참조 표가 stale 되지 않도록 보장.

#### Interface / Message Contract Review

> **조건부 추가**: `.analysis/message-contract-candidates.md`가 존재하면 Quick Reference에 링크를 추가합니다.
> 
> 파일이 없는 경우 (W1에서 interface_scanner 실패/미실행):
> - Quick Reference에 "Interface / Message Contract Review" 섹션 자체를 생략
> - Module Design Card의 각 `IPC / Message / Interface Contracts` 섹션만이 유일한 IPC 정보 소스

**Case 1: message-contract-candidates.md 존재 (W1 interface_scanner 성공)**
```markdown
## Interface / Message Contract Review

- System-wide message contracts: `.analysis/message-contract-candidates.md`
- Module-local contract details: `modules/<name>.md` → `IPC / Message / Interface Contracts`
```

**Case 2: message-contract-candidates.md 미존재 (W1 실패/미실행)**
- 이 섹션 전체 생략
- 사용자는 개별 모듈의 `modules/<name>.md`에서 IPC 정보 확인

> **중요**: W3는 절대 `code2spec/09-message-contracts.md`를 생성하지 않습니다.
> IPC 정보는 interface_candidates.json → message-contract-candidates.md (W1) → 모듈 카드의 IPC 섹션 (W2) 경로로만 흐릅니다.

기반 문서:

- `02-architecture.md`
- `03-design-patterns.md`
- `modules/*.md`의 Quick Navigation
- `.analysis/analysis-notes/module-priority.md`

포함 내용:

- 시스템 개요 요약 (아키텍처 패턴, 레이어 구조, 기술 스택)
- 핵심 모듈 위치 테이블 (모듈 → 파일 매핑)
- 기능 수정 시 참조 파일:라인
- 아키텍처 원칙 요약
- 코드 수정 전 확인 순서
- 주요 설계 결정 3~5개
- Core 모듈 역할 한줄 요약

형식 예시:

```markdown
# Quick Reference (code2spec)

> 코드 수정 전 반드시 확인. 아키텍처 일관성 유지 필수.

## 시스템 개요

- 아키텍처 패턴: [요약]
- 레이어 구조: [요약]
- 기술 스택: [요약]

### 주요 설계 결정

1. ...
2. ...

## 핵심 모듈 위치

| 모듈       | 파일                     | 역할                     |
| ---------- | ------------------------ | ------------------------ |
| useService | `ui/hooks/useService.ts` | 서비스 데이터 fetch/캐시 |

## 아키텍처 원칙

1. ...
2. ...

## 기능 수정 시 참조

| 기능 | 파일 | 라인 |
| ---- | ---- | ---- |
| ...  | ...  | ...  |

## 코드 수정 전 확인 순서

1. 본 Quick Reference에서 관련 모듈 찾기
2. Module Design Card (`modules/<name>.md`) 읽기
3. `02-architecture.md` → 레이어 규칙 준수 확인
4. `03-design-patterns.md` → 설계 패턴 위반 여부 확인
5. `04-data-layer.md` → 스키마 변경 시 마이그레이션 필요 여부
6. `05-external-interfaces.md` → 외부 API 변경 시 에러 처리 확인
```

### W3 종료 시간 기록

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" build-deps-map \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}"

${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" workflow-end \
  --output-dir "${ANALYSIS_DIR}" \
  --workflow W3 \
  --coding-agent "claude-code"
```

### 완료 조건

- README.md 생성 완료
- code2spec-quick-reference.md 생성 완료
- source-deps-map.json 갱신 완료
- interlinking 완료
- W3 시작/종료 기록 완료

---

## Step 2: 품질 메트릭 계산 및 Acceptance Gate

### 목표

생성된 문서의 품질을 정량적으로 평가하여 `quality-metrics.json`에 저장한다.

### 실행 명령

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" compute-metrics \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}"

set +e
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" quality-gate \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}" \
  --run-type full
QUALITY_GATE_EXIT=$?
set -e

if [ "${QUALITY_GATE_EXIT}" -eq 2 ]; then
  echo "[QUALITY_GATE] FAIL 또는 metrics 누락. .analysis/reports/quality/quality-issues.json 확인 필요."
elif [ "${QUALITY_GATE_EXIT}" -ne 0 ]; then
  exit "${QUALITY_GATE_EXIT}"
fi
```

### 생성 파일

- `${ANALYSIS_DIR}/reports/quality/quality-metrics.json` — 4개 메트릭 결과

### 메트릭 정의

| 메트릭 | 정의 | 계산식 |
|--------|------|--------|
| Evidence Precision | 코드 참조 정확도 | 유효 Source 태그 수 / 전체 Source 태그 수 |
| Source Coverage | 전체 소스 중 스펙 참조 비율 | 참조된 소스 파일 수 / 전체 소스 파일 수 |
| Core Coverage | 핵심 소스 중 스펙 참조 비율 | 참조된 Core 파일 수 / 전체 Core 파일 수 |
| Broken Source Link Rate | 깨진 Source Link 비율 | 깨진 Source 링크 수 / 전체 Source 태그 수 |

### Step 2-B: Broken Source Link Repair (1회 패치)

`QUALITY_GATE_EXIT`가 2(FAIL)이고 `quality-issues.json`에 `repair_action: "fix_broken_source_tags"` 이슈가 있으면 **1회에 한해** 아래 패치를 수행한다.

#### 수정 대상 판별 (evidence 항목별)

| `reason` | 처리 |
|---|---|
| `file_not_found` + 파일 시스템에 동일 basename이 **유일하게** 존재 | 전체 상대경로로 교체 (`[Source: basename.kt:L#]` → `[Source: full/path/basename.kt:L#]`) |
| `line_out_of_range` + 파일이 실제로 존재 | 해당 파일을 열어 올바른 라인번호를 찾아 교체 |
| `ambiguous_basename` | **건드리지 않음** |
| `file_not_found` + basename 매칭 없음 또는 복수 매칭 | **건드리지 않음** |

#### 패치 절차

1. `quality-issues.json`의 `fix_broken_source_tags` 이슈에서 `evidence` 배열을 읽는다.
2. `source_doc`별로 그룹화하여 문서를 한 번씩 열고 broken tag를 일괄 수정한다.
3. 수정 불가 태그는 건드리지 않고 넘어간다. 억지로 삭제하거나 임의 경로를 추측해 넣지 않는다.
4. 패치 완료 후 compute-metrics + quality-gate를 **1회 재실행**한다.

```bash
# 패치 완료 후 재실행 (1회만)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" compute-metrics \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}"

set +e
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" quality-gate \
  --output-dir "${ANALYSIS_DIR}" \
  --workspace-root "${ANALYSIS_TARGET}" \
  --run-type full
set -e
```

5. 재실행 후 결과가 `PASS`/`WARN`/`FAIL`에 관계없이 Step 3으로 진행한다. **추가 repair 루프는 없다.**

> 패치로 수정하지 못한 broken tag는 quality-issues.json에 계속 기록되며, 사용자가 수동으로 확인할 수 있다.

### 완료 조건

- quality-metrics.json 생성 완료
- quality-issues.json 생성 완료 (`PASS`/`WARN`/`FAIL`)
- 4개 메트릭 값이 0.0~1.0 범위 내
- FAIL 시 Broken Source Link에 한해 1회 패치 및 재평가 완료

> `finalize-history`(Step 3)는 내부적으로 `quality-metrics.json`이 존재하면 history.md에 메트릭 섹션을 자동 추가한다.

> **➡️ 다음은 Step 3이 아니라 Step 2-W다.** 여기(Step 2)의 4지표는 base 품질 게이트일 뿐이다. **반드시 Step 2-W
> (`wiki_cli.py finalize`)를 실행**해 deep-wiki 검증·`verification-report.md`·신뢰 배지를 생성한 뒤 Step 3으로 간다.

---

## Step 2-W: Code Wiki 검증 (⭐️ 필수) — `wiki_cli.py finalize` + hard gate 교정 루프

> **⚠️ 이 단계는 W3의 핵심이며 절대 건너뛰지 말 것.** Step 2(기존 4개 base 메트릭)만 하고 Step 3으로
> 넘어가면 **W3 미완성**이다. deep-wiki 검증(8 hard gate: `requiredSlots`·`astBaseline`·`wikiStructure`·
> `mermaidSyntax`·`grounding`·`claimGrounding`·`diagramAccuracy`·`moduleFrPairing`), `repo.json.qualityScore`,
> `verification-report.md`, 신뢰 데이터(`.trust/*.json`)는 **오직 이 단계에서만** 생성된다. Step 2와 별개의
> 부가지표가 아니라 **필수 검증**이다. `wiki_cli.py finalize`를 반드시 실행한다.

> **⚠️ finalize는 동시에 하나만 — W3를 주관하는 에이전트가 단독 실행한다.** `finalize`는 읽기 전용
> 검증이 아니라 **corpus 전체를 쓰는 단일 writer 작업**이다: 자동 교정 단계가 위키 `.md` 본문을
> 제자리에서 재작성하고 `repo.json`·`.trust/*.json`·`spec-cache.json`을 갱신한다. 두 개가 동시에 돌면
> (a) 같은 파일에 writer가 둘 붙어 서로의 편집을 덮어쓰고 — `spec-cache.json`은 tmp 경로가 고정이라
> 손상까지 가능하며, delta 기준점이 깨지면 다음 W-DELTA가 조용히 전량 재생성이 된다 — (b) **"교정이
> 더 이상 아무 파일도 바꾸지 못할 때 종료"라는 수렴 조건에 도달하지 못해** 양쪽이 상대의 변경을 새
> drift로 보며 라운드를 반복한다. 낭비가 N배가 아니라 초선형으로 늘어난다.
>
> 검증기는 모두 corpus 전체를 걷는다(`walk(wiki_dir)`). 그래서 **"내가 맡은 페이지만 finalize"라는
> 타협안도 없다** — 페이지를 나눠 맡겨도 전체 작업을 N번 반복하는 것과 같다.
>
> **fan-out은 fork가 아니라 컨텍스트 없는 fresh agent로 한다.** fork는 주관 에이전트의 대화 컨텍스트를
> 그대로 상속하므로 **이 문서(= "finalize를 반드시 실행한다"는 지시)까지 물려받아** 지시 범위를 벗어나
> 스스로 finalize를 반복 실행한다. 실측 사례: fork 2개가 각각 4~5라운드를 돌려 675K 토큰·51분을
> 소모했고 이는 세션 전체 토큰의 82%였다. 구체 지침은 아래 §fan-out 규칙 참조.
>
> **분업**: `finalize` 1회 → fresh agent fan-out(배정된 페이지만) → 전원 완료 대기 → 주관 에이전트가
> `finalize` 재실행. 라운드 수는 **수렴에 필요한 만큼**이다 — 줄여야 할 것은 중복 실행이며, 필요한
> 라운드를 깎아 hard gate 미통과 상태로 끝내는 것은 이 단계의 완료 조건 위반이다.

### ⛔ 대형 산출물 읽기 규율 (토큰) — 전체 읽기 금지, 질의만

이 단계가 참조하는 기계 산출물은 실제 저장소에서 수 MB급이다(`results[]` 수천 건, 전체 심볼·엣지).
교정에 필요한 건 "contradicted 15건의 page·line·reason" 같은 **소량의 좌표**인데 파일을 통째로
컨텍스트에 올리면 필요한 양의 수백 배를 토큰으로 지불한다. 아래 파일은 **Read/cat 등 전체 읽기
도구로 열지 않는다**:

```bash
QUERY="${WORKSPACE_ROOT}/.code2spec-tools/wiki/verification/query_artifacts.py"

${PYTHON} "$QUERY" "$OUTPUT_DIR" summary                                   # repo.json + .trust counts
${PYTHON} "$QUERY" "$OUTPUT_DIR" pages   --source claims --status contradicted
${PYTHON} "$QUERY" "$OUTPUT_DIR" list    --source claims --status contradicted --page <page>
${PYTHON} "$QUERY" "$OUTPUT_DIR" list    --source links  --status contradicted  # 링크별 배지 롤업
${PYTHON} "$QUERY" "$OUTPUT_DIR" symbols --file <src/path.ts>              # .ast/api.json
${PYTHON} "$QUERY" "$OUTPUT_DIR" symbols --name <Symbol>
${PYTHON} "$QUERY" "$OUTPUT_DIR" edges   --node <Node> [--to <Node>]       # .ast/deps.json
```

| 전체 읽기 금지 | 이유 |
|---|---|
| `repo.json` · `.trust/claims.json` | `results[]`·`links[]`가 수천 건 — 필요한 건 실패 항목뿐 |
| `.ast/{api,deps}.json` | 저장소 전체 심볼·엣지 — 필요한 건 한 파일/한 노드 |

- 출력 마지막 줄 `# source=… matched=M shown=S`가 **잘린 건수를 항상 알려준다**. `matched > shown`이면
  `--offset`으로 이어 받는다 — 앞 30건만 보고 "잔여 0건"으로 리포트에 적으면 안 된다.
- 위키 `.md` 본문·`verification-report.md`처럼 실제로 고쳐야 하는 파일은 규율 대상이 아니다(정상적으로
  읽고 편집한다). 금지 대상은 위 표의 **기계 산출 대형 JSON/JSONL뿐**이다.
- 도구가 못 하는 질의는 `python - <<'PY'` 인라인 스크립트나 `jq`/`grep`으로 **필터링된 결과만** 출력한다.
  JSON 전문을 stdout으로 흘리는 것은 Read로 읽는 것과 같다.

### 페이지 분담(fan-out) 규칙 — 3번 교정 루프의 본문 수정에만 적용

교정 대상 페이지가 많으면 페이지 단위로 나눌 수 있다. 단 아래를 지킨다:

- **`fork`(컨텍스트 상속)를 쓰지 않는다.** 컨텍스트 없는 일반 에이전트를 쓰고, 필요한 정보(담당
  페이지 목록, 고쳐야 할 항목의 좌표, `repo.json`의 deep-link base, 반환 형식)를 프롬프트에 모두 담는다.
  fork는 이 문서를 상속받아 스스로 finalize를 돌린다(위 ⚠️ 참조).
- **프롬프트에 금지선을 명시한다**: `wiki_cli.py finalize` 실행 금지 /
  `repo.json`·`verification-report.md`·`history.md`·`.trust/*` 쓰기 금지 / 반환은 담당 페이지의
  교정한 본문뿐.
- **대형 산출물 전체 읽기 금지도 프롬프트에 담는다** — `.ast/{api,deps}.json`·`.trust/*.json`은
  Read 하지 말고 `query_artifacts.py` 질의(`symbols`/`edges`/`list`)로만 본다.
  서브에이전트 N개가 각자 api.json을 통째로 읽으면 병렬화 이득을 토큰으로 그대로 반납한다.
- 검증기를 직접 돌려야 하면 **읽기 전용인 것만**: `validate_grounding.py`(`--json`은 자기 소유
  경로로)·`validate_diagram_accuracy.py`. `validate_wiki_claims.py`는 `.trust/`에 쓰므로
  주관 에이전트 전용이다.

**`code2spec-verification-report` 스킬**을 실행한다: **검증 → `verification-report.md` 기록 → hard gate가
모두 통과할 때까지 교정 루프 → 리포트 갱신**.

1. `wiki_cli.py finalize` **실행** (W3에서 finalize를 실행하는 지점 — 위 ⚠️대로 **주관 에이전트가
   단독으로** 실행한다. 서브에이전트에게 위임하거나 병렬로 여러 번 돌리지 않는다):

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/wiki_cli.py" finalize \
  --repo "${ANALYSIS_TARGET}" --output-dir "${OUTPUT_DIR}"
```

   내부 단계(자동): `write-wiki-metadata` → `spec-cache mark-all`(delta 기준점) → 자동 교정/진단
   (`convert-source-tags`·`quote-mermaid-labels`·`fix-citation-labels`·`fix-deeplink-lines`·`validate-layout`) →
   `validate-generated-wiki --tier full`(hard gate + soft score).
   산출: `repo.json`(qualityScore/qualityBreakdown) · `.trust/claims.json` · `spec-cache.json`.
   `.trust/claims.json`의 `links[]`(인용 링크 하나당 롤업 판정 한 줄)가 대시보드의 링크별
   신뢰 배지 데이터다 — 이전의 `.trust/atomic-claims.json`·`.claims/`는 제거됐고, finalize가
   옛 실행이 남긴 파일을 지운다.

   **finalize는 hard gate 실패를 즉시 종료로 취급하지 않는다.** 실패하면 결정적 교정을 다시 적용하고
   재검증하며(최대 3라운드), 교정이 더 이상 아무 파일도 바꾸지 못할 때에만 실패로 끝난다. 따라서 아래
   4·5 유형은 **아래 3번의 사람/LLM 교정 루프에 도달하기 전에 자동으로 해소된다**:
   - 백틱 없는 인용 라벨(`[출처]` 등) → `fix-citation-labels`가 api.json 심볼명(없으면 파일명)으로 교정
   - 틀린 `#L` 라인 → `fix-deeplink-lines`가 api.json 정의 라인(export가 아니면 소스 스캔)으로 교정

   `finalize`가 non-zero로 끝났다면 남은 것은 **기계적으로 고칠 수 없는 항목**뿐이다(존재하지 않는
   심볼명·없는 파일·코드와 어긋나는 주장). 종료 메시지가 축별로 무엇을 고쳐야 하는지 안내한다.

2. `<OUTPUT_DIR>/verification-report.md` 작성/갱신 — **finalize를 1회라도 실행했다면 이 파일은 반드시
   존재해야 한다**(finalize도 파일이 없으면 매번 경고를 출력한다). 구조:
   - **1절 요약표**: 축별 라운드 추이(R1→R2→…→최종 점수) + 최종 통과 여부. 매 라운드 qualityScore 스냅샷 기록.
   - **2절 축별 상세**: 각 hard gate 축마다 **근거를 반드시 포함** — 잔여 drift/contradicted/미지원
     edge의 실제 목록(무엇이, 어디서, 왜; `[grounding]` 출력·`.trust/claims.json`의 `results[]`에서
     그대로 옮김), 통과 축은 "잔여 0건"+판정 출처. 그 축의 라운드별 개선 내역도 여기 하위에 둔다
     (통합 테이블로 뭉치지 않음).
   - **점수만 나열한 리포트는 무효다** — 점수는 요약일 뿐, 신뢰의 근거는 축별 상세의 목록이다.
   상세 절차는 `code2spec-verification-report` 스킬을 따른다.

3. **hard gate 8축이 모두 통과할 때까지** 틀린 부분을 고치고 재검증 반복. **finalize가 non-zero로
   끝났다면 이 루프는 선택이 아니라 의무다** — 결정적 교정이 못 고친 실패는 LLM이 본문을 정정하라고
   넘긴 것이며, 실패 점수를 기록만 하고 W3를 완료로 보고하는 것은 미완수다. 축별 절차(좌표는 산출물이
   제공한다 — `code2spec-verification-report` 스킬의 교정 규칙 참조):
   - grounding drift → `[grounding]` drift 목록 기준: 잘못된 심볼명은 실제 export로 정정
     (`query_artifacts.py … symbols --file <path>` / `--name <Sym>`)
   - claimGrounding contradiction → `… list --source claims --status contradicted`의 항목
     (page:line·reason)별로 서술 정정·삭제
   - 미지원 diagram edge → **삭제가 아니라 교정이 기본**: `… edges --node <A> [--to <B>]`가 알려주는
     실제 관계로 edge의 끝점·방향을 교정하고, 외부 시스템 노드는 `class <node> external` 표시,
     어떤 근거도 없을 때에만 최후 수단으로 삭제(사유를 리포트에 남김)
   무한 루프 방지 상한 5라운드; 근거를 댈 수 없으면 서술을 삭제하고 리포트에 "미해결"로 남긴다.

4. 통과 후 최종 점수·개선 내역으로 리포트를 마무리.

### 게이트 정책

- **hard gate 8축**: `grounding`·`claimGrounding`·`diagramAccuracy`·`moduleFrPairing`은 "틀린 부분(drift·contradiction·미지원 edge·모듈/FR 불일치)은 모두 고친다" 원칙으로 hard(통과 = 틀린 부분 0). 하나라도 실패면 `wiki_cli.py`가 **결정적 교정을 재적용해 재검증하고**, 그래도 남으면 non-zero 종료.
  - `grounding`은 **deep-link의 `#L` 라인 정합을 검사하는 유일한 축**이다. `claimGrounding`은 식별자를 링크된 *파일 전체*와 대조하므로(`linked_file_mentions_identifier`) 파일은 맞고 라인만 틀린 인용을 통과시킨다. 그래서 grounding drift는 반드시 hard로 다룬다.
  - `grounding`은 **백틱 라벨만 검사**한다. `[출처]`처럼 백틱 없는 라벨은 통과가 아니라 `skipped`로 빠져 점수 분모에서 제외되므로, 그런 라벨은 애초에 만들지 않는다(§출처 표기 규율). 남은 것은 `fix-citation-labels`가 교정한다.
- **soft**(`symbolCoverage`·`packageCoverage`=단순 커버리지 측정): 점수만 기록, 루프 대상 아님.
- 점수·통과 여부는 산출물 값을 **그대로 옮긴다**(재계산·추측 금지, Zero-Inference).
- `atomicClaims` 축은 제거됐다 — 인용 claim을 별도로 수확해 채점하던 서브시스템으로, `claimGrounding`이 같은 술어(`citation_checks.py`)로 이미 hard gate 검사를 하던 것의 재측정이었다. 링크별 배지 데이터는 `.trust/claims.json`의 `links[]`가 대신한다.

### 완료 조건 (⭐️ 이걸 못 채우면 W3 미완성)

- `wiki_cli.py finalize` 실행 완료 → `repo.json.qualityScore`에 **8 hard gate + soft 점수** 기록됨
- hard gate 8축 통과. 예외는 하나뿐: **LLM 교정 루프를 5라운드까지 실제로 수행한 뒤에도** 남은
  항목을 삭제/"코드에서 확인 불가" 처리하고 리포트에 사유와 함께 "미해결"로 명시한 경우.
  교정 루프 없이 실패 점수(예: grounding 98, diagramAccuracy 36)를 기록만 한 상태는 **W3 미완성**이다
- `<OUTPUT_DIR>/verification-report.md` 생성됨 — **각 hard gate 축의 근거 목록 포함**(잔여 항목 목록
  또는 "잔여 0건"+출처; 점수만 나열한 리포트는 미완성) · `.trust/claims.json` 생성됨
- `spec-cache.json` 스냅샷 생성됨

---

## Step 3: History 업데이트 및 local finalize

> **선행 조건 확인(필수)**: 진행 전에 **Step 2-W가 실제로 수행됐는지** 확인한다 — `${OUTPUT_DIR}/repo.json`에
> `qualityScore`(8 hard gate 포함)와 `${OUTPUT_DIR}/verification-report.md`가 있어야 한다. 없으면 **Step 2-W로
> 돌아가 `wiki_cli.py finalize`를 먼저 실행**한다. (Step 2의 4지표만으로 Step 3에 오면 안 된다.)

### 목표

실행 이력을 history에 남기고 W3를 마무리합니다.

### 작업 내용

`finalize-history` CLI 호출:

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/code2spec_progress.py" finalize-history \
  --output-dir "${ANALYSIS_DIR}" \
  --note "W1+W2+W3 완료"
```

생성 파일:

- `${ANALYSIS_DIR}/history.md` — 내부 실행 상세 history
- `${OUTPUT_DIR}/history.md` — 프로젝트 전체 요약 history (`## Summary` 테이블 + `## Workflow Details`)

### 완료 조건

- history 업데이트 완료
- W3 산출물 전체 존재 확인

### 종료 요약

W3 완료 후 사용자에게 아래 요약을 출력합니다:

```text
🎉 code2spec 완료!

생성된 문서:
- 분석 대상: ${ANALYSIS_TARGET}
- 생성 위치: ${OUTPUT_DIR}
- ${OUTPUT_DIR}/README.md  (전체 TOC)
- ${OUTPUT_DIR}/history.md  (실행 이력)
- ${OUTPUT_DIR}/verification-report.md  (검증 결과 — hard gate 8축 통과 여부·라운드 추이)

검증: hard gate 8축 <통과/실패> · qualityScore <값> · 신뢰 데이터 ${OUTPUT_DIR}/.trust/

📌 ${OUTPUT_DIR}/code2spec-quick-reference.md 가 생성되었습니다.
이 파일은 바이브 코딩 시 AI 어시스턴트(Cline/Cursor)가 코딩 전 참조하는 통합 문서입니다.
- 시스템 개요, 핵심 모듈 위치, 아키텍처 원칙, 코드 수정 전 확인 순서가 포함되어 있습니다.
- 전체 코드를 로딩하지 않고도 올바른 파일을 찾고 아키텍처 원칙을 준수할 수 있습니다.
- 코딩 세션 시작 시 이 파일을 컨텍스트에 로드하면 토큰 절감(~3K)과 아키텍처 일관성 유지가 동시에 가능합니다.
```

#### Delta 상태에서 실행한 경우 추가 안내

`analysis-progress.json`에 `delta: true`가 있다면 종료 메시지 끝에 아래 한 단락을 더 출력합니다:

```text
⚠ Delta 모드 안내:
- 이번 실행은 module-level만 갱신했습니다.
- 시스템 SDD(01~08)는 자동 갱신 대상이 아닙니다 — 큰 아키텍처 변경이 있었다면 /code2spec-discovery 부터 full rebuild를 권장합니다.
```

종료 요약 초안 (아직 출력 금지)입니다. 이 시점에는 사용자에게 출력하거나 workflow를 종료하지 않습니다. Step 3 완료는 W3 완료가 아닙니다.

## Step 4: AX Artifact snapshot upload 결정 (필수 Human-in-the-Loop)

모든 W3 local finalize와 history 기록이 끝난 뒤 `${OUTPUT_DIR}` 전체를 AX Artifact snapshot으로 선택적으로 업로드합니다. 업로드 자체는 선택이지만, `${OUTPUT_DIR}`이 존재하고 upload MCP 도구와 완전한 Git context가 확인된 경우 **업로드 여부 질문과 사용자의 명시적인 응답은 필수**입니다.

### 4-1. 출력 경로 안전 검사

```bash
AX_ARTIFACT_UPLOAD_STATUS="skipped"
OUTPUT_DIR_ABS=$("${PYTHON}" -c 'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())' "${OUTPUT_DIR}")
if [ -d "${OUTPUT_DIR_ABS}" ]; then AX_ARTIFACT_UPLOAD_STATUS="output-ready"; else AX_ARTIFACT_UPLOAD_STATUS="missing-output"; fi
```

`AX_ARTIFACT_UPLOAD_STATUS=output-ready`인 경우에만 아래 MCP/Git context 가용성 검사를 수행합니다. basename `code2spec`으로 경로를 다시 만들지 않고 사용자가 선택한 `${OUTPUT_DIR}`의 canonical absolute path를 그대로 사용합니다.

### 4-2. MCP 및 Git/Gerrit context 가용성 확인

사용 가능한 MCP 도구 목록에서 `ax-artifacts` 서버의 `ax_artifacts_upload` 도구를 찾습니다. 서버 이름과 도구의 논리 이름은 정확히 일치시키되, 클라이언트가 생성한 긴 qualified alias는 하드코딩하지 않습니다. 도구가 확인되면 MCP 호출 전에 공통 CLI를 실행합니다.

```bash
GIT_CONTEXT_JSON=$(${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/git_context.py" --repo "${ANALYSIS_TARGET}" --format json)
```

- `status=ok`이고 `remote_url`, `branch`, `commit_id`가 모두 존재하면 `AX_ARTIFACT_UPLOAD_STATUS="eligible"`로 설정합니다.
- `not_git`, `incomplete`, `error`이면 `AX_ARTIFACT_UPLOAD_STATUS="skipped-no-git-context"`로 기록하고 업로드 HITL과 MCP 호출을 모두 건너뜁니다.
- remote URL은 credential이 제거된 값만 사용하며 `GIT_CONTEXT_JSON`을 파일, history, telemetry에 저장하지 않습니다.

`eligible`은 종료 상태가 아닙니다. `eligible`인 채로 W3를 완료하거나 Step 4를 생략해서는 안 됩니다.

### 4-3. 사전 HITL

이 질문은 반드시 한 번 표시하고 사용자의 응답을 기다립니다.

```text
[W3 Step 4] Code2Spec 결과를 AX Artifact에 업로드하시겠습니까?
- Upload directory: ${OUTPUT_DIR_ABS}
- 포함 범위: code2spec 디렉토리 전체 (`.analysis/`, cache, reports, state 포함)
- coding_agent: claude-code
- agent_tool: skill:code2spec
1) 업로드
2) 건너뛰기
```

사용자가 `1) 업로드`를 선택하기 전에는 upload MCP 도구를 호출하지 않습니다. 사용자가 `2) 건너뛰기`를 선택하면 `AX_ARTIFACT_UPLOAD_STATUS="user-skipped"`로 기록한 뒤 최종 출력으로 진행합니다.

### 4-4. MCP upload와 snapshot 최종 확인

`coding_agent`는 설치 시 현재 AI coding assistant에 맞게 렌더링된 `claude-code` 값을 그대로 사용합니다. 실행 중에 LLM이 이 값을 다시 추론하거나 변경하지 않습니다.

`ax-artifacts` 서버의 `ax_artifacts_upload` 도구를 다음 값으로 호출합니다.

- `source_dir`: `${OUTPUT_DIR_ABS}`
- `remote_url`: `GIT_CONTEXT_JSON.remote_url`
- `branch`: `GIT_CONTEXT_JSON.branch`
- `commit_id`: `GIT_CONTEXT_JSON.commit_id`
- `channel`: `code2spec` (항상 이 고정값 사용)
- `coding_agent`: `claude-code` (설치 시 확정된 고정값)
- `agent_tool`: `skill:code2spec` (항상 이 고정값 사용)

도구가 반환한 upload 명령은 최종 확인 후에만 실행하며 결과는 `uploaded`, `user-skipped`, `failed-continued` 중 하나로 기록합니다.

AX Artifact 사전 조건이 모두 유효한데 사용자 응답 없이 `skipped`로 간주한 상태는 완료로 인정하지 않습니다.

`ax_artifacts_upload`가 제공하는 현재 입력 schema만 사용하되 `channel`은 반드시 `code2spec`, `agent_tool` 값은 반드시 `skill:code2spec`으로 고정합니다.

**🎉 code2spec 완료**
