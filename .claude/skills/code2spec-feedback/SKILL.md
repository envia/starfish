---
name: code2spec-feedback
description: "Collect and submit code2spec feedback."
metadata:
  code-skills:
    id: code2spec/code2spec-feedback
---

# Claude Code Skill: code2spec-feedback

> This skill is generated from the code2spec workflow markdown for Claude Code.
> Shared templates are installed under `.claude/code2spec/templates/`; Python tools are installed under `.code2spec-tools/`.
> Installed tool build metadata is recorded at `.code2spec-tools/build-info.json`.

# code2spec-feedback

gh CLI로 피드백을 GitHub Issue로 제출

# code2spec-feedback — GitHub Issue로 피드백 제출

gh CLI를 사용하여 사용자 피드백을 GitHub Enterprise Issue로 제출합니다.

## 대상 리포지토리

- **Host**: github.sec.samsung.net
- **Repo**: specflow/code2spec_voc
- **Label**: feedback

## 프로세스

### 1. 대화 컨텍스트 수집

최근 대화를 분석하여 피드백 소재를 파악합니다:
- 어떤 작업을 수행 중이었는지
- 무엇이 잘 되었거나 안 되었는지
- 구체적인 불편 사항이나 개선 제안

### 2. 피드백 초안 작성

**제목**: 한 문장으로 요약 (예: "certify-trace 단계에서 에러 메시지가 불명확함")

**본문** 구성:
```markdown
## 상황
[어떤 작업을 하고 있었는지]

## 문제 / 제안
[발생한 문제 또는 개선 제안]

## 기대 동작
[어떻게 동작하면 좋겠는지]

## 추가 컨텍스트
[관련 워크플로우, 에러 메시지 등]
```

### 3. 민감 정보 익명화 (필수)

제출 전 반드시 다음을 치환합니다:
- 파일 경로 → `<path>`
- API 키, 토큰, 시크릿 → `<redacted>`
- 회사/조직명 → `<company>`
- 개인 이름 → `<user>`
- 내부 URL → `<url>` (공개 URL은 유지)

### 4. 사용자 확인 (필수)

초안을 보여주고 반드시 승인을 받습니다:

```
피드백 초안을 작성했습니다:

제목: [제목]

본문:
[본문]

이대로 제출할까요? 수정이 필요하면 말씀해주세요.
```

### 5. gh CLI로 제출

승인 후 다음 명령어로 제출합니다:

```bash
GH_HOST=github.sec.samsung.net gh issue create \
  --repo specflow/code2spec_voc \
  --title "피드백 제목" \
  --body "피드백 본문" \
  --label feedback
```

### gh CLI 미설치 시 대체 방법

gh CLI를 사용할 수 없는 경우, 브라우저로 직접 제출할 수 있도록 URL을 생성합니다:

```
https://github.sec.samsung.net/specflow/code2spec_voc/issues/new?title=<encoded-title>&body=<encoded-body>&labels=feedback
```

## 가드레일

- 제출 전 반드시 초안을 보여주고 사용자 승인을 받을 것
- 민감 정보를 반드시 익명화할 것
- 사용자가 수정을 요청하면 반영 후 다시 확인받을 것
- 승인 없이 절대 제출하지 말 것
- gh CLI 인증 상태를 먼저 확인할 것 (`gh auth status`)
- `GH_HOST=github.sec.samsung.net` 환경변수를 반드시 설정할 것
