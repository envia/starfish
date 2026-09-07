---
name: code2spec-module-review
metadata:
  code-skills:
    id: code2spec/code2spec-module-review
description: "AST 분류 결과(module-priority.md)를 읽고 파일명 기준으로 Core 모듈을 모드별 상한(Light=10, Standard=20, Detail=35)까지 공격적으로 축소. module-priority-reviewed.md 생성."
argument-hint: "--priority-file <path> --mode <1|2|3> --output-dir <path>"
---

# Skill: Module Review

## Objective

`ast_analyzer.py`가 생성한 `module-priority.md`의 Core 목록을 분석 모드(ANALYSIS_SCOPE)에 맞게 축소한다.
코드를 읽지 않고 **파일명만으로** 판단하여 빠르게 처리한다.

## 모드별 target_core

| ANALYSIS_SCOPE | 모드        | target_core                         |
| -------------- | ----------- | ----------------------------------- |
| 1              | 🟡 Light    | 10개                                |
| 2              | 🔵 Standard | 20개                                |
| 3              | 🟢 Detail   | 35개                                |
| 4              | 🔴 Full     | 제한 없음 (PageRank 평균 이상 전체) |
| 5              | 🟣 Custom   | 사용자 지정 수 (--max-core N)       |

## Steps

### Step 1: module-priority.md 읽기

```bash
cat "${OUTPUT_DIR}/analysis-notes/module-priority.md"
```

Core Modules 섹션의 파일 목록을 확인한다.

### Step 2: 파일명 기준 Core 축소

**코드를 열지 않는다. 파일명과 디렉토리명만으로 판단한다.**

**Core 유지 우선순위 (높은 순):**

1. `routes/`, `route/`, `router/` — API 진입점
2. `controllers/`, `handlers/` — 요청 처리
3. `service/`, `services/` — 비즈니스 로직
4. `repositories/`, `repository/` — 데이터 접근
5. `middlewares/`, `middleware/` — 공통 처리
6. `agents/` — 핵심 에이전트 (AI/워크플로우 프로젝트)
7. `app.ts`, `server.ts`, `main.ts`, `index.ts` (루트 레벨만)

**Peripheral 이동 우선순위 (먼저 제거):**

1. `types/`, `type/`, `*.d.ts` — 타입 정의
2. `constants/`, `utils/`, `helpers/` — 유틸리티
3. `config/` — 설정
4. `db/schema`, `db/migrations` — DB 스키마/마이그레이션
5. centrality_score = 0인 파일
6. 같은 디렉토리의 유사 파일 (대표 1~2개만 유지)

target_core 초과 시 위 우선순위 역순으로 제거한다.

### Step 3: 결과 저장

검토 결과를 `${OUTPUT_DIR}/analysis-notes/module-priority-reviewed.md`에 저장:

```markdown
# Module Priority (Reviewed)

분석 모드: {Light|Standard|Detail} (ANALYSIS_SCOPE={1|2|3})
target_core: {N}개
원본 Core 수: {M}개 → 검토 후: {K}개

## 선별 기준 요약

[한 줄 요약]

## Core Modules ({K}개)

| 모듈 | centrality_score | category |
| ---- | ---------------- | -------- |

[선별된 파일]

## Peripheral로 이동 ({M-K}개)

<!-- 테이블 아닌 목록 형식 사용 (code2spec_progress가 잘못 읽는 것 방지) -->

- `파일경로` — 이유
  [제외된 파일과 이유]
```

### Step 4: 결과 보고

```
[module-review] 완료
  원본 Core: {M}개 → 검토 후: {K}개 (목표: {N}개 이내)
  저장: ${OUTPUT_DIR}/analysis-notes/module-priority-reviewed.md
```

## 준수 규칙

- 코드 파일을 열거나 읽지 않는다 — 파일명만으로 판단
- target_core를 초과하지 않는다
- 판단이 애매한 파일은 Peripheral로 이동 (보수적 판단)
- 제거 이유를 반드시 기록한다
