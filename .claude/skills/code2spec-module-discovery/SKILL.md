---
name: code2spec-module-discovery
metadata:
  code-skills:
    id: code2spec/code2spec-module-discovery
description: "LLM 기반 Logical Module Boundary Discovery. AST 의존성 그래프와 파일 목록을 분석하여 도메인/기능 단위 모듈 경계를 제안합니다. HITL (Human-in-the-Loop) 검증을 통해 최종 모듈 그룹핑을 확정합니다."
argument-hint: "--ast-dir <path> --output-dir <path> --prompt <A|B>"
---

# Skill: Module Discovery (LLM 기반 Logical Module 그룹핑)

## Objective

AST 의존성 그래프와 파일 목록을 기반으로 LLM 이 Logical Module 경계를 자동으로 발견하고 제안합니다.

사용자는 제안된 모듈을 검토 (HITL) 하여 최종 모듈 그룹핑을 확정합니다.

## When to Use

- **W1의 모듈 확정 하위 단계 (Logical 모드 전용)**: 별도 워크플로가 아니라 `code2spec-discovery`(W1)
  안의 Discovery Pipeline **Step 3-2**에서 실행된다. AST export 직후, W1의 Core 목록 확정(Step 3-4/3-5)
  이전에 모듈 경계를 발견·확정한다. (Physical 모드는 이 단계를 건너뛰고 파일 단위로 진행)
- **Logical Module 단위 분석이 필요할 때**: 기존 파일 단위보다 문맥 있는 그룹핑이 필요
- **도메인 경계를 발견하고 싶을 때**: 코드베이스의 도메인 구조를 자동으로 파악

> **왜 W1인가**: W2(`code2spec-modules`)가 각 모듈을 분석해 실제 FR·Module Design Card를 쓰려면
> **먼저 모듈 목록이 확정**돼 있어야 한다. 그 확정이 W1의 핵심 산출물이며, 이 스킬은 Logical 모드에서
> 그 확정을 만드는 W1 내부 단계다. FR·모듈 문서 자체는 여기서 만들지 않는다(전부 W2 소관).

## Instructions

### Step 1: Module Discovery 실행

```bash
WORKSPACE_ROOT="<installed-project-root>"
ANALYSIS_TARGET="<analysis-target-path>"
PYTHON="${WORKSPACE_ROOT}/.code2spec-venv/bin/python"
OUTPUT_DIR="${ANALYSIS_TARGET}/code2spec"
ANALYSIS_DIR="${OUTPUT_DIR}/.analysis"
STATE_DIR="${ANALYSIS_DIR}/state/delta"
AST_DIR="${ANALYSIS_DIR}/cache/code-to-ast"

# Module Discovery 실행 (프롬프트 생성)
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" discover \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}/module-discovery" \
  --prompt A
```

### Step 2: LLM 에 프롬프트 전송

1. 생성된 프롬프트 파일 확인:
   ```bash
   cat "${ANALYSIS_DIR}/module-discovery/llm-prompt.md"
   ```

2. LLM 에게 프롬프트 전송 및 응답 생성

3. LLM 응답을 YAML 파일로 저장:
   ```bash
   # 예: llm-response.yaml
   ```

### Step 3: LLM 응답 검토 (HITL)

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" review \
  --ast-dir "${AST_DIR}" \
  --output-dir "${ANALYSIS_DIR}/module-discovery" \
  --llm-response "${ANALYSIS_DIR}/module-discovery/llm-response.yaml" \
  --output "module-groups-proposed.yaml"
```

### Step 4: 제안된 모듈 검토 및 수정

1. `module-groups-proposed.yaml` 파일 확인:
   ```bash
   cat "${ANALYSIS_DIR}/module-discovery/module-groups-proposed.yaml"
   ```

2. 필요한 경우 파일 수정:
   - 모듈 이름 변경
   - 파일 이동/추가/제거
   - rationale 수정

3. 유효성 검사:
   ```bash
   ${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" validate \
     --config "${ANALYSIS_DIR}/module-discovery/module-groups-proposed.yaml"
   ```

### Step 5: 최종 모듈 그룹핑 저장

```bash
${PYTHON} "${WORKSPACE_ROOT}/.code2spec-tools/group_cli.py" save \
  --config "${ANALYSIS_DIR}/module-discovery/module-groups-proposed.yaml" \
  --output-dir "${STATE_DIR}"
```

## Output Format

LLM 은 다음 YAML 형식으로 응답해야 합니다:

```yaml
modules:
  - name: "module-name"
    files:
      - "src/path/to/file1.tsx"
      - "src/path/to/file2.tsx"
    rationale: "Why these files are grouped together"
    confidence: 0.85
```

### Rules for LLM

- 모듈명은 kebab-case 사용 (예: `user-management`, `task-core`)
- 각 모듈은 2-20 개 파일 포함
- "other" 모듈을 만들지 않음
- 모든 모듈에 의미있는 이름 부여
- confidence score (0.0-1.0) 포함

## Example Output

```yaml
version: 1
modules:
  - name: "app-core"
    files:
      - "src/App.tsx"
      - "src/main.tsx"
      - "src/router.tsx"
      - "src/layouts/MainLayout.tsx"
    rationale: "애플리케이션 진입점과 라우팅, 기본 레이아웃"
    confidence: 0.95

  - name: "user-management"
    files:
      - "src/contexts/UserContext.tsx"
      - "src/contexts/UserProvider.tsx"
      - "src/types/user.ts"
      - "src/pages/UserProfile.tsx"
    rationale: "사용자 상태 관리, 인증, 프로필 관련 기능"
    confidence: 0.90

  - name: "task-management"
    files:
      - "src/contexts/TaskContext.tsx"
      - "src/contexts/TaskProvider.tsx"
      - "src/pages/AddTask.tsx"
      - "src/pages/Home.tsx"
      - "src/components/tasks/*.tsx"
    rationale: "할일 관리의 핵심 기능 (CRUD, 목록, 상세)"
    confidence: 0.92
```

## HITL Review Checklist

검토 시 다음 항목을 확인하세요:

- [ ] 모듈 이름이 명확하고 일관된가?
- [ ] 각 모듈의 파일이 응집도 있는가?
- [ ] 파일이 여러 모듈에 중복되지 않는가?
- [ ] 테스트 파일이 적절히 처리되었는가?
- [ ] 도메인 경계가 논리적인가?

## Integration with code2spec

Module Discovery 는 별도 워크플로가 아니라 **W1(`code2spec-discovery`) 내부의 모듈 확정 하위 단계**
(Step 3-2, Logical 모드)로 통합됩니다:

```
W1 code2spec-discovery ─────────────────────────────→ W2 code2spec-modules → W3 code2spec-finalize
   ├─ AST 그래프 생성
   ├─ [Logical] module-discovery(이 스킬) → 모듈 경계 발견 (HITL 검증)   ← 여기
   ├─ Core 목록 확정 (module-priority-reviewed.md / module-groups.yaml)
   └─ 시스템 문서(01~09)
```

- **W1**: AST 그래프 생성 → (Logical이면) module-discovery로 **모듈 목록 확정** → 시스템 문서(01~09).
  확정된 모듈 목록(`.analysis`의 `module-groups.yaml`·`module-priority-reviewed.md`·`core-manifest.json`)이
  W2로의 핸드오프다. **FR·모듈 문서/인덱스는 만들지 않는다.**
- **W2**: 확정된 모듈을 심층 분석해 `modules/*.md`·`functional-requirements/*-fr.md`와 인덱스를 생성
- **W3**: 문서 완성(상호링크·Quick Reference)

## Troubleshooting

### LLM 응답이 YAML 형식이 아닌 경우

- 프롬프트에서 "You MUST output ONLY in the following YAML format" 강조
- 코드 블록 (```yaml) 으로 감싸서 출력하도록 지시

### 파일 경로가 일치하지 않는 경우

- 절대경로 vs 상대경로 문제 확인
- `_normalize_paths` 함수가 경로 정규화를 올바르게 수행하는지 확인

### 모듈에 파일이 없는 경우

- LLM 이 잘못된 파일명을 생성했을 수 있음
- HITL 검토 시 실제 존재하는 파일인지 확인

## References

- [LLM Module Discovery 테스트 결과](../../../test-module-discovery/test-result-report.md)
- [implementation_plan.md](../../../implementation_plan.md)
