# Grounding & Deep-Links (검증 영향 규율)

이 문서는 code2spec SDD 본문에 deep-wiki 계열 검증(grounding · wikiStructure)을
통과시키기 위한 **검증 지표에 영향을 주는 작성 규율만** 모은 것이다. Zero-Inference·챕터 구성 등
일반 작성 규칙은 상위 `SKILL.md`와 템플릿을 그대로 따른다. 이 규율은 SDD 산출물이 검증
파이프라인(플랜 PR4)과 대시보드에 투입될 때 적용된다.

## 0. 근거 소스는 `.ast/`, 링크는 `src:` 축약형

- 심볼 라인·시그니처는 `.ast/api.json`에서만 가져온다(추측 금지). `.ast/`는 code2spec tree-sitter
  그래프를 `tools/wiki/ast_adapter.py`가 변환한 산출물이다(스키마: `docs/wiki/ast-schema.md`).
- **deep-link는 host URL을 적지 않는다.** `src:<repo-상대경로>[#L<라인>]` 축약형으로 쓰고,
  host/owner/branch 접두사는 렌더 시 `repo.json.deepLink.base`가 붙는다. 즉 `github.com`을
  가정할 일이 애초에 없다(사내 enterprise GitHub·gitlab·cgit·gerrit 모두 같은 본문으로 동작).

```markdown
✅ [`RetrieverService`](src:src/retriever.ts#L42)
⛔ [`RetrieverService`](https://github.example.com/Org/Repo/blob/main/src/retriever.ts#L42)
```

> **왜 축약형인가**: 링크마다 반복되는 고정 접두사가 문서 문자의 ~28%를 차지했다. 축약형은
> 문서를 **-27%**, 읽기 토큰을 **-21%** 줄이고, 저장소 이관·브랜치 변경 시 `repo.json` 한 곳만
> 바뀌면 모든 링크가 따라온다. `repo.json`이 문서와 함께 생성되므로 복원은 무손실이다.
>
> **맨 상대경로(`](src/x.ts)`)를 쓰지 않는 이유**: SDD는 대상 저장소의 `code2spec/` 하위에
> 생성되므로 맨 상대경로는 `code2spec/modules/src/x.ts`로 해석되어 404가 된다. `src:`는
> 진짜 상대링크(문서 간 이동 `../modules/x.md`)와 절대 충돌하지 않는다.
>
> 라인 앵커는 host 형식(`#n`·`#l`·`#lines-`)이 아니라 **항상 `#L`**로 쓴다 — host 형식은
> 렌더 시점에 붙는다. 전체 URL을 적어도 검증은 통과하지만 그만큼 문서가 커지므로,
> **생성 단계에서 축약형으로 쓰는 것이 규칙이다**(사후 일괄 변환기는 두지 않는다).

## 1. `Relevant source files` 블록 — 모든 .md 상단 (wikiStructure)

`README.md`·`01`~`09` 챕터·`modules/*`·`functional-requirements/*` 등 **모든 .md**는 H1 바로 아래에
다음 blockquote 블록을 둔다. wikiStructure 검증기가 이 헤더 존재를 확인한다.

```markdown
# <문서 제목>

> **Relevant source files**
>
> - [<path/to/file.ext>](src:<path/to/file.ext>)
> - [<path/to/another.ext>](src:<path/to/another.ext>)

<본문 시작>
```

- 라인 번호 없이 **파일 단위** deep-link만(페이지 scope). 3~12개 권장.
- 정말 매핑할 코드가 없는 문서도 최소 1개(관련 manifest·README·docs)를 적는다.
- 위치는 H1 바로 아래, 사이에 다른 단락을 끼우지 않는다.

## 2. 코드 심볼은 백틱 deep-link 인용 (grounding)

본문에서 함수·클래스·enum·상수·환경변수·파라미터를 언급하면, 그 식별자를 아래 형태로 링크한다.
grounding 검증기가 `#L<n>` 라인에 실제로 그 심볼이 있는지 대조한다.

```markdown
[`RetrieverService`](src:src/retriever.ts#L42) 는 질의를 …
```

- 라벨은 **백틱으로 감싼 식별자**, 링크는 `src:<repo-relative-path>#L<line>`.
- **`#L<line>`은 그 심볼의 실제 정의 라인이다** — `.ast/api.json`의 해당 심볼 `line`에서 가져온다.
  **`#L1`(파일 top)을 디폴트로 박지 말 것**(예: `Sha256Hasher`가 4행에 정의되면 `#L4`, `#L1` 아님).
  라인이 틀리면 finalize의 `fix_deeplink_lines`가 api.json 기준으로 자동 교정하고, grounding hard gate가
  라인 정합을 강제한다(drift가 남아 있으면 finalize가 실패한다). 링크 없는 식별자 인용 금지, 빈 `foo()` 금지.
- **§1의 RSF 파일 링크(라인 없음)는 이 인라인 심볼 인용을 대체하지 않는다.** 챕터·모듈·FR 본문·표에서
  코드 심볼(함수·클래스·상수·enum·핸들러 등)을 언급하면 **파일 단위가 아니라 반드시 `#L<라인>` 심볼
  deep-link**로 인용한다. (파일 링크만 있는 문서는 grounding이 라인 정합을 검증하지 못한다.)
- **위키 내부 이동 링크는 백틱 없이** 일반 Markdown 링크: `[아키텍처](./02-architecture.md)`.
- ⛔ **파일명을 심볼로 인용하지 말 것.** 심볼 deep-link의 라벨은 `.ast/api.json`의 **실제 export 이름**
  이어야 한다. `` `webExtractor` `` `` `aggregation.service` `` 처럼 파일 basename을 식별자로 쓰면
  claimGrounding이 "identifier not found in file"로 contradicted 처리한다. 파일에 그 이름의 export가
  없으면(예: `AuthServer.ts`가 `createAuthApp`·`AuthServerDeps`만 export) **실제 export 이름**으로 쓰고,
  파일 자체를 가리키려는 것이면 §3의 **백틱 파일명 라벨**(`` [`AuthServer.ts`](…#L<n>) ``)을 쓴다.
  (라인이 어긋난 것만 finalize의 `fix_deeplink_lines`가 자동 교정한다 — 존재하지 않는 심볼명은 못 고친다.)

> 모든 외부 소스 인용은 **deep-link로** 한다(대시보드/RAG에서
> 클릭 가능한 출처를 위해). **시스템 챕터(01~09)뿐 아니라 `modules/`·`functional-requirements/`
> 문서도 동일한 deep-link 인용을 쓰며, 같은 검증 파이프라인으로 검증된다**(제외 없음).

## 3. 문장별 출처 (Zero-Inference 작성 규율)

사실을 **주장하는** 문장은 §2의 형식으로 근거를 댄다. 근거를 댈 수 없는 문장은 쓰지 말고,
불가피하면 **"코드에서 확인 불가"** 마커를 남긴다(빈 추측 금지).

### ⛔ `[출처]` 같은 백틱 없는 라벨 금지

라인 앵커가 붙은 소스 deep-link의 라벨은 **반드시 백틱 코드 인용**이어야 한다. 검증기는
**라벨에 백틱이 있을 때만** 그 링크를 검사 대상으로 삼는다 — 즉 `[출처](...)`·`[여기](...)`처럼
백틱 없는 라벨은 통과가 아니라 **검증 자체에서 빠진다**(`skipped`). 점수에도, hard gate에도 잡히지
않으므로 틀린 라인이 영구히 남는다.

```markdown
⛔ 이 모듈은 해시를 계산한다 [출처](src:src/hasher.ts#L4).
✅ 이 모듈은 [`Sha256Hasher`](src:src/hasher.ts#L4) 로 해시를 계산한다.
```

인용할 **심볼이 없는** 근거(설정 값·manifest 항목·스크립트 한 줄 등)라면 `[출처]`가 아니라
**백틱 파일명 라벨**을 쓴다. 검증기가 이 형식을 링크된 파일의 basename과 대조해 검사한다.

```markdown
✅ 빌드는 `tsc -p .` 로 수행된다 [`package.json`](src:package.json#L12).
```

- 파일명 라벨은 `[`name.ext`]` 또는 `[`name.ext:12`]`·`[`name.ext:39-45`]` 형태를 인정한다.
- 확장자는 검증기의 알려진 확장자 목록에 있어야 한다
  (`tools/wiki/verification/validate_grounding.py`의 `KNOWN_FILE_EXTENSIONS`).
- finalize의 `fix_citation_labels`가 남아 있는 백틱 없는 라벨을 api.json 기준 심볼명(없으면 파일명)
  으로 자동 교정하지만, **생성 단계에서 애초에 백틱으로 쓰는 것이 원칙이다.**

> 문장 단위 전수 인용은 강제하지 않는다. 목차·문서 구성 안내·"코드에서 확인된 … 없음" 같은
> 부재 선언·템플릿 메타(`**생성일**:` 등)는 근거 링크가 필요 없다 — 이런 구조적 문장까지 100%
> 인용을 강제하던 문장 커버리지 게이트는 제거되었다. 근거는 grounding(심볼 deep-link가 실제
> 라인을 가리키는지)으로 검증하며, **grounding은 hard gate다**(drift 1건이라도 있으면 실패).

## 4. 다이어그램

Mermaid `graph`/`flowchart`/`sequenceDiagram`은 `diagramAccuracy`·`mermaidSyntax` 검증 대상이다.
노드 ID·edge·따옴표 규칙은 별도 문서에 두지 않고 **기존 `code2spec-code-to-diagram` 스킬의
"Validation-Aware Diagram Rules" 절**을 따른다.
