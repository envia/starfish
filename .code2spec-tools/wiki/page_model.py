"""Single source of truth for the code2spec SDD output contract.

The wiki machinery (deep-link / repo.json / validation) layers onto code2spec's
existing SDD — chapters 01..09 plus ``modules/`` and ``functional-requirements/`` —
rather than producing a separate page set. This module names the slots that the
validation pyramid checks (requiredSlots) and that the dashboard lists
(topLevelEntries), so the two consumers never drift apart:

* ``prepare_code_wiki.py`` → ``repo.json.topLevelEntries``
* ``verification/validate_generated_wiki.py`` → requiredSlots hard gate

The chapter set mirrors ``templates/.code2spec_template.md`` (IEEE 1016 Enhanced).
"""

from __future__ import annotations

# 항상 생성되는 시스템 SDD 챕터 + 진입 문서.
MANDATORY_CHAPTERS: list[str] = [
    "README.md",
    "01-introduction.md",
    "02-architecture.md",
    "03-design-patterns.md",
    "05-external-interfaces.md",
    "06-configuration-deployment.md",
    "08-security-quality.md",
]

# 근거가 있을 때만 생성되는 챕터(코드에 해당 계층/근거가 없으면 생략될 수 있음).
# data-layer(데이터 계층)·resources(정적 리소스)·ipc-enum(IPC 상수)은 repo 특성에 따라 조건부다.
CONDITIONAL_CHAPTERS: list[str] = [
    "04-data-layer.md",
    "07-resources.md",
    "09-ipc-enum-catalog.md",
]

# W2가 채우는 구조적 산출(디렉토리/인덱스). 검증은 "비어있지 않은지"를 본다.
STRUCTURAL_SLOTS: list[str] = [
    "modules/",
    "functional-requirements/index.md",
]

# 검증 requiredSlots hard gate 대상 — 항상 존재해야 하는 최소 집합.
# 조건부 챕터는 여기 넣지 않는다(없다고 실패시키지 않음).
REQUIRED_SLOTS: list[str] = [*MANDATORY_CHAPTERS, *STRUCTURAL_SLOTS]

# repo.json.topLevelEntries — 대시보드 navigation 순서(README + 챕터 01..09).
TOP_LEVEL_ENTRIES: list[str] = [
    "README.md",
    "01-introduction.md",
    "02-architecture.md",
    "03-design-patterns.md",
    "04-data-layer.md",
    "05-external-interfaces.md",
    "06-configuration-deployment.md",
    "07-resources.md",
    "08-security-quality.md",
    "09-ipc-enum-catalog.md",
]

# 전체 SDD 챕터(순서대로) — mandatory + conditional 합집합을 챕터 번호순으로.
ALL_CHAPTERS: list[str] = [f for f in TOP_LEVEL_ENTRIES if f != "README.md"]
