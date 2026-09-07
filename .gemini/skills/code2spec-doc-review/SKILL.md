---
name: code2spec-doc-review
metadata:
  code-skills:
    id: code2spec/code2spec-doc-review
description: "code2spec 생성물(SDD)의 레이아웃·출처 링크·필수 산출·검증 결과를 생성 직후 리뷰하고 교정하는 스킬. sdd/ 같은 임의 하위폴더 이탈, [Source:] 미변환 링크, repo.json/.ast/qualityScore 누락, 검증 hard gate 실패를 체크리스트로 잡아 자동 교정 후 재검증한다. W3(finalize) 마무리 단계에서 실행. Use when finalizing/publishing a code2spec wiki, or when the dashboard doesn't render the output correctly."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# code2spec-doc-review — 생성물 리뷰 & 교정 (Target B, 이슈 #16 작업 B)

생성이 끝난 SDD가 **대시보드에서 그대로 렌더되고 검증을 통과하는 형태**인지 결정적으로 점검하고, 위반을 자동 교정한다. 결정적 도구가 실제 판정을 하고, LLM은 그 출력을 읽어 남은 교정(문장 인용 추가·loose 파일 흡수 등)을 수행한다.

## 공통 변수

```bash
WORKSPACE_ROOT="<installed-project-root>"      # .code2spec-tools 위치
ANALYSIS_TARGET="<W1/W2와 동일한 분석 대상>"
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
WIKI_CLI="${WORKSPACE_ROOT}/.code2spec-tools/wiki_cli.py"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"       # 문서 루트(= wiki-dir)
```

## Step 1 — 결정적 리뷰 실행

`wiki_cli.py finalize` 한 번이 (self-heal로) `.ast`/`repo.json` 보장 → `[Source:]`→deep-link 변환 →
레이아웃 lint → 검증 파이프라인(hard gate + qualityScore)까지 수행한다. 이미 finalize를 돌렸다면
개별 도구로 재점검할 수 있다.

```bash
${PYTHON} "${WIKI_CLI}" finalize --repo "${ANALYSIS_TARGET}" \
  [--remote-url <url>] [--branch <name>]      # remote가 불명확하면 지정
```

출력에서 다음 신호를 읽는다: `[layout] ...`(레이아웃), `[convert-source-tags] N 개`(링크 변환),
`[<axis>] exit/score`(검증 축), `qualityScore`(repo.json 기록).

## Step 2 — 체크리스트 판정 (모두 충족해야 "리뷰 통과")

| 항목 | 판정 기준 | 근거 |
|---|---|---|
| **레이아웃** | `[layout] SUMMARY — errors=0`; 필수 챕터가 `OUTPUT_DIR` 루트에 직접(있음), `sdd/` 등 하위폴더·비표준 loose md(`logic-extraction.md`·`pattern-mapping.md`) 없음 | `validate_layout.py` |
| **링크 스타일** | `[Source:]` 잔존 0(비파일 설명 제외), 코드 인용이 모두 `src:` 축약 deep-link(전체 URL 잔존 0 — 발견되면 해당 인용을 축약형으로 직접 수정) | `[layout] WARN` [Source: 잔존 수], `grep -c "\[Source:"`, `grep -c "](https\?://[^)]*/blob/"` |
| **필수 산출** | `OUTPUT_DIR/repo.json`·`.ast/{api,deps}.json` 존재, `repo.json.qualityScore`(dict) 기록됨 | 파일 존재 + repo.json |
| **검증 hard gate** | `requiredSlots·astBaseline·wikiStructure·mermaidSyntax·grounding·claimGrounding·diagramAccuracy·moduleFrPairing` 통과(틀린 부분 0까지) | `validate-generated-wiki` |
| **soft 축 리포트** | grounding·claim·symbol/package/diagram coverage 점수를 보고(낮아도 실패 아님, 재작성 판단 근거) | `repo.json.qualityBreakdown` |

## Step 3 — 자동 교정 후 재실행

- **레이아웃 ERROR(sdd/ 오배치)**: 하위폴더의 문서를 `OUTPUT_DIR` 루트로 이동(`git mv`), 상호링크의 상대경로 점검.
- **비표준 loose md**: 내용을 해당 챕터/모듈 카드에 흡수하고 파일 삭제.
- **`[Source:]` 잔존**: `wiki_cli.py finalize` 재실행(변환기 재적용) 또는 해당 인용을 deep-link로 직접 수정.
- **grounding DRIFT(soft)**: 심볼 deep-link의 `#L<n>`이 실제 라인과 어긋나면 `.ast/api.json` 기준으로 라인을 교정한다. **없는 근거를 지어내지 않는다**(Zero-Inference).
- **symbol/diagram coverage 낮음(soft)**: 주요 심볼 언급·다이어그램 edge를 `.ast/deps.json` 근거로 보강(선택, 실패 아님).

교정 후 Step 1을 재실행해 hard gate 통과와 레이아웃 errors=0을 확인한다.

## 산출

리뷰 결과를 한 줄 체크리스트로 보고: 레이아웃 ✅/❌ · [Source:] 잔존 수 · repo.json/.ast 유무 · hard gate 통과 여부 · qualityScore 요약. 미충족 항목과 교정 조치를 명시한다.

> 이 스킬은 **W3(finalize) 마무리** 또는 publish 직전 필수 단계로 실행한다. 결정적 판정은
> `tools/wiki/verification/validate_layout.py`·`validate_generated_wiki.py`·`convert_source_tags.py`가
> 담당하고, LLM은 그 출력을 근거로만 교정한다(추측 금지).
