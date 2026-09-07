# Code2Spec Session History

## 세션 정보

- **실행 일시**: 2026-08-27 10:41:56
- **code2spec 버전**: 0.5.3
- **실행 유형**: full
- **Coding assistants**: gemini-cli
- **History format**: v2 hybrid
- **분석 모드**: Detail
- **분석 대상**: `/home/hwang/work/F/starfish_`

## 코드 규모

- 총 파일 수: 330개
- 총 라인 수: 102,438행
- 클래스 수: 373개
- 함수 수: 5,630개
- 총 용량: 3,547,397 bytes (3464.3 KB)
- 기준: AST 파싱된 소스 파일 기준 (hidden dot 경로 제외, min_lines=0)

### 확장자별 통계

| 확장자 | 파일 수 | 라인 수 | 용량 |
|--------|--------|---------|------|
| .cpp | 150 | 69,922 | 2,437,542 |
| .h | 118 | 21,160 | 685,635 |
| .py | 43 | 8,144 | 311,056 |
| .java | 11 | 1,708 | 57,758 |
| .js | 8 | 1,504 | 55,406 |

## 워크플로우별 상세

| Workflow | 시작 | 종료 | 소요시간 | 상태 |
|----------|------|------|----------|------|
| W1 | 10:41:56 | 10:42:04 | 8초 | ✅ passed |
| W2 | 10:46:17 | 10:47:44 | 1분 27초 | ✅ passed |
| W3 | 10:49:15 | 10:54:17 | 5분 2초 | ✅ passed |
| **총계** | | | **6분 37초** | |

### Workflow coding assistants

| Workflow | Coding Assistant |
|----------|------------------|
| W1 | gemini-cli |
| W2 | gemini-cli |
| W3 | gemini-cli |

## Telemetry 요약

- 이벤트 파일: `telemetry-events.jsonl`
- 이벤트 수: 29개
- Coding assistants: gemini-cli
- Git repo: `github.sec.samsung.net/jh1984-hwang/starfish` @ `master`
- Token 사용량: unknown (provider token source 미연동)

### Workflow 사용 횟수

| Workflow | Started | Completed | In Progress | Failed | Attempts |
|----------|--------:|----------:|------------:|-------:|---------:|
| W1 | 1 | 1 | 0 | 0 | 1 |
| W2 | 1 | 1 | 0 | 0 | 1 |
| W3 | 1 | 1 | 0 | 0 | 1 |

## 결과물 요약

- 모듈 수: 17/17
- MD 파일: 49개
- MD 총 라인 수: 3,055행
- 비고: W1+W2+W3 terminal status recorded

## 품질 메트릭

| 메트릭 | 값 | 세부 |
|--------|------|------|
| Evidence Precision | 95.85% | 208/217 태그 유효 |
| Source Coverage | 100.00% | 330/330 파일 참조 |
| Core Coverage | 100.00% | 17/17 Core 모듈 카드 생성 |
| Broken Source Link Rate | 0.00% | 0/217 링크 깨짐 |
| Quality Gate | PASS | 0 issues (`.analysis/reports/quality/quality-issues.json`) |

