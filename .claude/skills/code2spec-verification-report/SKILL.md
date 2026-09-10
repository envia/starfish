---
name: code2spec-verification-report
metadata:
  code-skills:
    id: code2spec/code2spec-verification-report
description: "W3(finalize)에서 검증 → verification-report.md 기록 → hard gate가 모두 통과할 때까지 교정 루프 → 리포트 갱신을 수행하는 스킬. hard gate=requiredSlots·astBaseline·wikiStructure·mermaidSyntax·grounding·claimGrounding·diagramAccuracy·moduleFrPairing(틀린 부분은 모두 고침). soft=symbolCoverage·packageCoverage(측정, 게이트 아님). repo.json.qualityScore·qualityBreakdown과 .trust/claims.json을 읽어 (1)요약표 (2)축별 상세 (3)개선 수행 내역을 기록. Use at the end of W3."
---

# Skill: Verification Report (W3 검증 리포트 생성)

## Objective

W3에서 **검증 → 리포트 기록 → hard gate가 모두 통과할 때까지 교정 루프 → 리포트 갱신**을 수행한다.
결정적 산출물(`repo.json`·`.trust/*.json`)을 읽어 사람이 읽는 **`<OUTPUT_DIR>/verification-report.md`**를
만들고, hard gate에 걸린 "틀린 부분"을 모두 고친 뒤 최종 결과로 리포트를 업데이트한다.

- `OUTPUT_DIR` = 분석 대상의 `code2spec/` (SDD 루트). 리포트는 이 루트 바로 아래에 만든다.
- 점수·통과 여부는 **재계산하지 않고 산출물의 값을 그대로 옮긴다**(추측·재계산 금지).
- **Zero-Inference**: 점수를 올리려고 내용을 지어내지 않는다. 틀린 것을 **사실대로 바로잡을 뿐**이며,
  근거가 없으면 해당 서술을 제거하고 "코드에서 확인 불가"로 남긴다.

## ⛔ 대형 산출물 읽기 규율 (토큰) — 파일 읽기 도구 금지, 질의만

검증 산출물은 실제 저장소에서 수 MB급이다(`results[]` 수천 건, api/deps 전체 심볼·엣지).
교정에 필요한 건 "contradicted 15건의 page·line·reason" 같은 **소량의 좌표**인데, 파일을 통째로
컨텍스트에 올리면 필요한 양의 수백 배를 토큰으로 지불한다. 그래서 아래 파일은 **Read/cat 등
전체 읽기 도구로 열지 않는다** — `query_artifacts.py`(또는 python/jq/grep) 질의로만 접근한다.

| 파일 | 전체 읽기 | 대신 사용 |
|---|---|---|
| `<OUTPUT_DIR>/repo.json` | ⛔ | `query_artifacts.py <OUTPUT_DIR> summary` |
| `<OUTPUT_DIR>/.trust/claims.json` | ⛔ | `… list --source claims --status contradicted` (링크별 롤업은 `--source links`) |
| `<OUTPUT_DIR>/.ast/api.json` | ⛔ | `… symbols --file <path>` / `… symbols --name <Sym>` |
| `<OUTPUT_DIR>/.ast/deps.json` | ⛔ | `… edges --node <Node> [--to <Node>] [--kind …]` |

```bash
QUERY="${WORKSPACE_ROOT}/.code2spec-tools/wiki/verification/query_artifacts.py"
${PYTHON} "$QUERY" "$OUTPUT_DIR" list --source claims --status contradicted --limit 30
```

- 출력 마지막 줄 `# source=… matched=M shown=S`가 **잘린 건수를 항상 알려준다**. `matched > shown`이면
  `--offset`으로 이어서 받는다 — 첫 30건만 보고 "잔여 0건"이라고 적으면 안 된다.
- 위키 `.md` 본문·`verification-report.md`처럼 실제로 편집해야 하는 파일은 이 규율 대상이 아니다
  (정상적으로 읽고 고친다). 금지 대상은 위 표의 **기계 산출 대형 JSON/JSONL뿐**이다.
- 도구가 커버하지 못하는 질의는 `python - <<'PY'` 인라인 스크립트나 `jq`/`grep`으로 **필터링된
  결과만** 출력한다. 어떤 경우에도 JSON 전문을 stdout으로 흘리지 않는다.

> **⚠️ 이 스킬은 "검증 1회 + 기록"으로 끝나지 않는다.** `wiki_cli.py finalize`가 non-zero로 끝났거나
> hard gate 축에 100 미만이 남아 있으면 스킬은 **아직 진행 중**이다 — finalize의 결정적 교정
> (`fix-citation-labels`·`fix-deeplink-lines` 등)은 기계적으로 고칠 수 있는 것만 처리하며, 남은 실패는
> **LLM이 본문을 정정하라고 넘긴 것**이다. 아래 교정 루프를 수행하지 않고 실패 점수를 기록만 한 채
> 완료로 보고하는 것은 이 스킬의 미완수다(예: grounding 98·diagramAccuracy 36 상태로 종료 보고 금지).

## W3 검증·교정 루프 (핵심 절차)

이 스킬은 아래 루프를 수행한다. **hard gate(8축)**: `requiredSlots`·`astBaseline`·`wikiStructure`·
`mermaidSyntax`·`grounding`·`claimGrounding`·`diagramAccuracy`·`moduleFrPairing`. **soft(게이트 아님)**:
`symbolCoverage`·`packageCoverage`.

1. **검증**: `wiki_cli.py finalize` 실행(→ `repo.json.qualityScore`·`.trust/*.json` 갱신).
   **이 루프는 W3를 주관하는 에이전트가 단독으로 수행한다 — `finalize`를 서브에이전트에게
   실행시키거나 병렬로 여러 번 돌리지 않는다.** `finalize`는 위키 `.md` 본문을 제자리에서 재작성하는
   단일 writer 작업이라, 동시에 돌면 서로의 편집을 덮어쓰고 수렴 조건("교정이 더 이상 아무 파일도
   바꾸지 못함")에 도달하지 못해 라운드가 초선형으로 늘어난다. 4번 교정 작업은 페이지 단위로 나눠
   위임해도 안전하지만(파일이 겹치지 않게), **컨텍스트를 상속하는 `fork`는 쓰지 않는다** — 이 문서를
   물려받아 스스로 finalize를 돌린다. 상세는 워크플로우 `code2spec-finalize.md`의 Step 2-W 참조.
2. **기록**: Step 1~3으로 `verification-report.md`를 작성/갱신(현재 라운드 결과).
3. **판정**: hard gate 8축이 모두 통과(각 100 / N/A, claimGrounding은 contradiction 0)면 **루프 종료**.
4. **교정**: 통과 못 한 hard gate의 "틀린 부분"을 LLM이 직접 고친다(아래 축별 절차). 그 뒤
   **1번으로 돌아가 재검증**. 어떤 항목을 어떻게 고칠지는 각 축의 산출물이 위치(page:line)와 사유를
   제공하므로 추측하지 않는다:
   - **`grounding` drift** — finalize 출력의 `[grounding]` drift 목록(심볼 → `path#L<n>`, 사유)을 읽는다.
     결정적 교정이 이미 실패한 뒤이므로 남은 drift는 대개 **잘못된 심볼명/파일**이다: 그 파일의 실제
     export를 `query_artifacts.py … symbols --file <path>`로 확인해 라벨을 실제 심볼명·라인으로
     정정하거나(심볼이 어느 파일에 있는지 모르면 `symbols --name <Sym>`), 문장이 다른 파일을 설명하고
     있으면 인용 대상을 바로잡는다. 심볼이 코드 어디에도 없으면 그 서술을 삭제한다.
     **`.ast/api.json`을 통째로 읽지 않는다.**
   - **`claimGrounding` contradiction** — `list --source claims --status contradicted`로 항목을 받아
     하나씩 처리한다(`.trust/claims.json` 전체 읽기 금지). 각 항목의 `page`·`line`·`reason`이 좌표다:
     없는 파일 인용 → 실제 파일로 교체 또는 문장 삭제, 시그니처 불일치 → `reason`의 actual params로
     라벨 수정, 라벨 파일명 불일치 → 실제 basename으로 수정. 건수가 많으면 `pages --source claims
     --status contradicted`로 페이지별 분포를 먼저 보고 페이지 단위로 처리한다.
   - **`diagramAccuracy` 미지원 edge** — **삭제가 아니라 교정이 기본이다.** 다이어그램의 edge는 문서의
     주장이므로, 틀렸다면 지우는 게 아니라 사실로 바로잡는다. 우선순위:
     ① `query_artifacts.py … edges --node <A> [--to <B>]`로 그 두 노드(또는 그 모듈의 파일들)가
        실제로 갖는 관계를 찾아 **edge의 끝점·방향을 교정**한다(예: `A --> B`가 없고 `B --> A`가
        있으면 방향을 뒤집는다; 중간 노드를 거치는 관계면 그 경로로 고친다). 출력의 `kind`·`from`·`to`가
        그대로 근거가 된다 — **`.ast/deps.json`을 통째로 읽지 않는다.**
     ② 노드가 저장소 밖 외부 시스템(IdP, 외부 API 등)이면 edge를 지우지 말고 `class <node> external`을
        표시해 채점 제외로 만든다.
     ③ deps.json에 그 어떤 방향·경로의 근거도 없을 때에만 **최후 수단으로** edge를 삭제하고, 삭제
        사유를 리포트 개선 내역에 남긴다. edge를 몽땅 지워 점수만 맞춘 빈 다이어그램은 교정이 아니다.
   - **`requiredSlots`/`wikiStructure`/`mermaidSyntax`** → 누락 슬롯 생성·RSF 블록 보강·라벨 따옴표(자동 도구 재적용).
   - **`moduleFrPairing` 불일치** — `validate_module_fr_pairing.py` 출력이 항목별 좌표를 준다: 모듈에
     매칭되는 FR이 없으면(`✗ modules/<name>.md → functional-requirements/<name>-fr.md 없음`) W2로
     돌아가 그 모듈의 FR 문서를 생성한다. FR에 매칭되는 모듈이 없으면(`✗ functional-requirements/
     <name>-fr.md → modules/<name>.md 없음`) 모듈이 리네임/삭제됐는데 FR만 남은 것이므로, 그 모듈이
     실제로 아직 존재하는지 확인해 모듈 카드를 보충하거나(존재) 남은 FR을 삭제한다(진짜 폐기된 모듈).
     `-fr.md` 명명 규칙을 어긴 파일은 올바른 파일명으로 rename한다.
5. **종료 후 갱신**: hard gate가 모두 통과하면(또는 아래 안전장치로 중단하면) 최종 점수와 **3절(개선 수행 내역)**을
   반영해 `verification-report.md`를 마지막으로 업데이트한다.

> **무한 루프 안전장치**: 같은 항목이 교정 후에도 반복해서 실패하거나(예: 진짜로 근거를 댈 수 없는 서술),
> 라운드가 지나도 hard gate 실패 수가 줄지 않으면(권장 상한 **5 라운드**) 루프를 멈춘다. 이때는 해당 항목을
> **삭제하거나 "코드에서 확인 불가"로 남기고**, 리포트 3절에 "미해결(사유)"로 명시한다. 점수를 위해 조작 금지.
>
> soft 축(`symbolCoverage`·`packageCoverage`)은 낮아도 루프를 돌리지 않는다 — 리포트에 기록만 한다.

## Step 1 — 검증 산출물 로드 (값은 그대로 사용)

```bash
PYTHON="${REPO_ROOT:-.}/.code2spec-venv/bin/python"
QUERY="${WORKSPACE_ROOT}/.code2spec-tools/wiki/verification/query_artifacts.py"
OUTPUT_DIR="<analysis-target>/code2spec"

# 요약 숫자를 정확히 확인 (여기 출력된 값을 리포트에 그대로 옮긴다)
# repo.json.qualityScore/Breakdown + .trust/claims.json counts·배지 링크 수를 한 번에.
${PYTHON} "$QUERY" "$OUTPUT_DIR" summary
```

- `qualityScore[축]` — 축별 점수(0–100). `null`(None)이면 **N/A**(해당 없음: 분모 0 등).
- `qualityBreakdown.validators[축]` — 축별 요약 한 줄(상세 표의 근거).
- `.trust/claims.json` — claimGrounding(deep-link 링크 검사) 상세: `counts{supported,contradicted,unresolved}`, 술어별 `results[]`, 그리고 인용 링크 하나당 롤업 판정 `links[]`(대시보드의 링크별 신뢰 배지 데이터; `--source links`로 질의).

`results[]`의 개별 항목이 필요해지는 건 2절 상세와 교정 루프인데, 그때도 **파일을 열지 말고**
필요한 행만 뽑는다(위 §대형 산출물 읽기 규율):

```bash
# 어느 페이지를 고쳐야 하는지 (page × status 집계 — 가장 싼 질의)
${PYTHON} "$QUERY" "$OUTPUT_DIR" pages --source claims --status contradicted

# 그 페이지의 항목만 좌표·사유와 함께
${PYTHON} "$QUERY" "$OUTPUT_DIR" list --source claims --status contradicted \
  --page modules/retriever.md
```

축별 목록이 더 필요하면 해당 검증기를 `--json`(파일로)/`--list`로 재실행하되, **그 JSON도 다시
`query_artifacts.py`나 `jq`로 필터해서 본다** — 검증기 출력 파일 역시 대형 JSON이다.

## Step 2 — 검증 축 메타데이터 (고정: 리포트 요약표의 "필수 여부·Gate 기준")

| 검증 축 | 분류 | Gate 기준 | 근거/의미 |
|---|---|---|---|
| `requiredSlots` | **필수(hard gate)** | 점수 **100**(필수 챕터·구조 슬롯 모두 존재) | 하나라도 없으면 0 → finalize `exit 1` |
| `astBaseline` | **필수(hard gate)** | 점수 **100**(.ast api/deps 비어있지 않음) | AST 근거가 없으면 문서 검증 불가 |
| `wikiStructure` | **필수(hard gate)** | 점수 **100**(RSF 블록·구조 규약 준수) | 구조 오류 있으면 0 |
| `mermaidSyntax` | **필수(hard gate)** | 점수 **100** / 다이어그램 0개면 **N/A** | 파싱 실패 라벨 하나로도 0 |
| `grounding` | **필수(hard gate)** | 점수 **100**(drift 0) / deep-link 0개면 **N/A** | 심볼 deep-link `#L`이 실제 라인을 가리키는지 |
| `claimGrounding` | **필수(hard gate)** | **contradiction 0** / claim 0개면 **N/A** | deep-link 링크의 파일/라인/심볼 실재(.trust/claims.json) |
| `diagramAccuracy` | **필수(hard gate)** | 점수 **100**(미지원 edge 0) / edge 0개면 **N/A** | mermaid edge가 .ast/deps.json에 실재하는지 |
| `moduleFrPairing` | **필수(hard gate)** | 점수 **100**(모듈↔FR 1:1 매칭, 명명 규칙 위반 0) / `modules/`·`functional-requirements/` 둘 다 없으면 **N/A** | `modules/<name>.md` 하나당 `functional-requirements/<name>-fr.md`가 정확히 하나씩 존재해야 함(양방향) |
| `symbolCoverage` | 소프트 | 게이트 아님(점수만) / 심볼 0개면 N/A | 주요 심볼이 문서에 언급된 비율(단순 커버리지 측정) |
| `packageCoverage` | 소프트 | 게이트 아님(점수만) / 패키지 0개면 N/A | 패키지가 문서에 다뤄진 비율(단순 커버리지 측정) |

> **전체 통과 판정**: 위 **hard gate 8축이 모두 100(또는 N/A / claimGrounding은 contradiction 0)**이면
> 검증 통과(finalize `exit 0`). `grounding`·`claimGrounding`·`diagramAccuracy`는 "틀린 부분(drift·
> contradiction·미지원 edge)은 모두 고쳐야 한다"는 원칙에 따라 hard로 승격됐다 — 이 검증기들은 틀린
> 부분이 있을 때만 exit≠0을 내므로 통과 = 틀린 부분 0.
> `symbolCoverage`·`packageCoverage`(단순 커버리지)는 soft로, 점수가 낮아도 통과에 영향이 없다
> (진단·개선 우선순위 용도). `sentenceCoverage`·`atomicClaims`는 제거된 축이라 표에 넣지 않는다.

## Step 3 — `verification-report.md` 작성

`<OUTPUT_DIR>/verification-report.md`를 아래 구조로 생성한다. 숫자는 각 라운드의 Step 1 출력에서
그대로 옮긴다. **개선 내역은 한 테이블로 뭉치지 말고 각 검증 축 상세(2절) 하위에** 둔다.

> **⚠️ 점수만 나열한 리포트는 무효다.** 점수는 신뢰의 근거가 아니라 요약일 뿐이다 — 독자가 검증
> 결과를 신뢰하려면 **각 hard gate 축의 2절 상세에 근거가 있어야 한다**: 실패·교정된 축은 잔여
> drift/contradicted/미지원 edge의 **실제 목록**(무엇이, 어디서, 왜)을, 처음부터 통과한 축은
> "잔여 0건"과 그 판정의 출처(검증기 출력·`.trust/*.json` 경로)를 적는다. 이 근거 없이 요약표만
> 있는 파일은 이 스킬의 산출물로 인정되지 않는다. 리포트 **생성 자체도 선택이 아니다** — 검증을
> 1회라도 실행했다면 그 라운드 결과가 리포트에 기록돼야 하며, finalize도 리포트가 없으면 매번
> 경고를 출력한다.

> **라운드 기록**: 교정 루프의 **매 라운드마다** `wiki_cli.py finalize` 직후 qualityScore 스냅샷을
> (축별 점수) 남겨둔다. 요약표(1절)는 이 스냅샷들을 **R1 → R2 → … → 최종** 열로 보여주고, 각 축
> 상세(2절)는 그 축이 라운드마다 어떻게 바뀌었는지를 적는다.

### 1. 검증 결과 요약 (라운드별 추이)

- 헤더에 `verifiedAt`(최종 검증 시각), **총 라운드 수**, **전체 통과 여부**(최종 hard gate 모두 통과 → ✅ / 실패 → ❌)를 적는다.
- 요약표는 **각 축의 라운드별 점수 추이**를 보여준다(교정으로 점수가 어떻게 올라갔는지 한눈에):

```markdown
| 검증 축 | 필수 여부 | Gate 기준 | R1 | R2 | R3(최종) | 통과 |
|---|---|---|---|---|---|---|
| requiredSlots | 필수(hard) | 100 | 100 | 100 | 100 | ✅ |
| astBaseline | 필수(hard) | 100 | 100 | 100 | 100 | ✅ |
| wikiStructure | 필수(hard) | 100 | 0 | 100 | 100 | ✅ |
| mermaidSyntax | 필수(hard) | 100 | 100 | 100 | 100 | ✅ |
| grounding | 필수(hard) | drift 0 | 49 | 93 | 100 | ✅ |
| claimGrounding | 필수(hard) | contradiction 0 | 98 | 100 | 100 | ✅ |
| diagramAccuracy | 필수(hard) | 미지원 0 | 36 | 75 | 100 | ✅ |
| moduleFrPairing | 필수(hard) | 100 | 82 | 100 | 100 | ✅ |
| symbolCoverage | 소프트 | — | 20 | 21 | 22 | ⚠️ |
| packageCoverage | 소프트 | — | 100 | 100 | 100 | ✅ |
```

- 라운드가 1회면 R1 열 하나만(추이 없음). 라운드 수만큼 열을 만든다. 값은 각 라운드 qualityScore(정수/N/A).
- 통과 열(최종 기준): 필수(hard)는 최종 100/contradiction0이면 ✅ / 실패면 ❌ / N/A면 ➖. 소프트·측정전용은 ✅(높음)·⚠️(낮음/이슈)·➖(N/A). 전체 통과는 **hard gate 8축**만으로 판정.

### 2. 축별 상세 (+ 축별 개선 내역)

각 축을 소제목(`### 2.1 requiredSlots` …)으로 두고, 아래 **두 부분**을 함께 적는다:

1. **최종 결과·근거**: `qualityBreakdown.validators[축]`·`.trust/*.json` 기준의 상세 표. 권장 필드:
   - **requiredSlots / astBaseline / wikiStructure / mermaidSyntax**: 검사 항목, 결과, 근거 라인.
   - **grounding**: total / checked / aligned / drift 수 (+ 최종 잔여 drift 목록).
   - **claimGrounding**(`.trust/claims.json`): supported / contradicted / unresolved (+ 잔여 contradicted 목록)
     + 배지 링크 수(`links[]`)와 그중 `supported`가 아닌 링크 수.
   - **diagramAccuracy**: parsed / verifiable / supported / external 제외 수 (+ 잔여 미지원 edge 목록).
   - **moduleFrPairing**: modules / fr docs / matched 수(%) (+ 모듈에 매칭되는 FR 없음 목록, FR에 매칭되는
     모듈 없음 목록, `-fr.md` 명명 규칙 위반 목록).
   - **symbolCoverage / packageCoverage**: covered / total(%) + 미언급 상위 항목.

   목록은 `query_artifacts.py … list --source claims|links --status <…>` 출력을 옮긴다. 잔여 항목이
   `--limit`보다 많으면 `--offset`으로 끝까지 받아 **전량**을 적는다(footer의 `matched`가 기준 수치).
2. **개선 내역(이 축 한정)**: 교정이 있었던 축만, **라운드별로** 아래 표를 둔다. 교정이 없던 축은 "R1부터 통과, 교정 없음"으로 한 줄 표기.

```markdown
#### 개선 내역
| 라운드 | 문제(무엇이) | 원인 | 수행한 개선 | 재검증 결과 |
|---|---|---|---|---|
| R1→R2 | `IAllowlist` deep-link L1/L2 등 21건 drift | `#L`이 정의 라인과 불일치 | api.json 기준 라인 교정 (예: `IAllowlist`→L5) | 93% (잔여 6건) |
| R2→R3 | `#L1-L5` 범위 링크 6건 잔여 | 범위 링크는 L1만 검사됨 | `#L5` 단일 라인으로 변경 | 100% (drift 0) |
```

- **자동 교정**(finalize가 매 라운드 수행)도 해당 축 아래에 적는다: `fix-deeplink-lines`(#L 라인·owner 중복), `convert-source-tags`([Source:]→deep-link), `quote-mermaid-labels`(라벨 따옴표).
- **수동 교정**: 잘못된 관계 서술 삭제·정정, 심볼명 정정 등. **점수를 위해 없는 근거를 지어내지 않는다** — 근거가 없으면 서술 제거 후 "코드에서 확인 불가".
- soft 축(symbol/package coverage)은 교정 루프 대상이 아니므로 개선 내역 대신 **현황**만 적는다.

> **개선 내역을 별도 통합 섹션(구 3절)으로 만들지 않는다.** 각 축 하위에 그 축의 라운드별 개선만 둔다.

## 완료 조건

- **hard gate 8축이 최종적으로 모두 통과**(100 / N/A, claimGrounding은 contradiction 0). 유일한 예외:
  5라운드 상한까지 교정을 **실제로 수행**한 뒤에도 남은 항목이 있으면, 그 항목 각각을 삭제 또는
  "코드에서 확인 불가" 처리하고 2절 개선 내역에 "미해결(사유)"로 명시한 경우.
  **교정 루프를 수행하지 않은 채 실패 점수를 기록만 하고 완료를 선언하는 것은 허용되지 않는다.**
- `<OUTPUT_DIR>/verification-report.md` 생성됨.
- 1절 요약표가 **라운드별 추이**(R1→…→최종)를 축마다 보여주고, 최종 값이 `repo.json.qualityScore`와 일치.
- **각 hard gate 축의 2절 상세에 근거가 있음** — 잔여 항목의 실제 목록 또는 "잔여 0건"+판정 출처.
  점수만 나열한 리포트는 이 조건을 충족하지 않는다.
- 각 hard gate 실패·drift·contradicted·stale 항목의 개선 내역이 **해당 축 상세(2절) 하위**에 라운드별로 기록됨(별도 통합 테이블 없음).
- 개선 내역은 실제 수행한 것만 기록(하지 않은 개선을 지어내지 않음).
