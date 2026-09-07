#!/usr/bin/env python3
"""Module Groups Configuration Loader - YAML 설정 파싱 및 검증."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import yaml


@dataclass
class ModuleGroup:
    """모듈 그룹 정의."""
    name: str
    files: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    rationale: str = ""
    domain: str | None = None
    hitl_review: str = ""


@dataclass
class ModuleGroupConfig:
    """모듈 그룹핑 설정."""
    version: int = 1
    modules: list[ModuleGroup] = field(default_factory=list)

    # 자동 그룹핑 설정 (선택적)
    auto_grouping_enabled: bool = False
    auto_grouping_algorithm: str = "llm"  # "llm" | "pattern" | "community"

    @classmethod
    def from_yaml(cls, yaml_path: str) -> ModuleGroupConfig:
        """YAML 파일에서 설정 로드."""
        with open(yaml_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> ModuleGroupConfig:
        """딕셔너리에서 설정 생성."""
        version = data.get('version', 1)
        auto_grouping = data.get('auto_grouping', {})

        modules = []
        for mod_data in data.get('modules', []):
            modules.append(ModuleGroup(
                name=mod_data.get('name', ''),
                files=mod_data.get('files', []),
                patterns=mod_data.get('patterns', []),
                rationale=mod_data.get('rationale', ''),
                domain=mod_data.get('domain'),
                hitl_review=mod_data.get('hitl_review', ''),
            ))

        return cls(
            version=version,
            modules=modules,
            auto_grouping_enabled=auto_grouping.get('enabled', False),
            auto_grouping_algorithm=auto_grouping.get('algorithm', 'llm'),
        )

    def to_dict(self) -> dict:
        """딕셔너리로 변환."""
        return {
            'version': self.version,
            'modules': [
                {
                    'name': m.name,
                    'files': m.files,
                    'patterns': m.patterns,
                    'rationale': m.rationale,
                    'domain': m.domain,
                    'hitl_review': m.hitl_review,
                }
                for m in self.modules
            ],
            'auto_grouping': {
                'enabled': self.auto_grouping_enabled,
                'algorithm': self.auto_grouping_algorithm,
            } if self.auto_grouping_enabled else {},
        }

    def get_module_by_name(self, name: str) -> ModuleGroup | None:
        """이름으로 모듈 검색."""
        for m in self.modules:
            if m.name == name:
                return m
        return None

    def get_all_files(self) -> list[str]:
        """모든 모듈의 파일 목록 (중복 제거)."""
        files = set()
        for m in self.modules:
            files.update(m.files)
        return sorted(files)

    def get_file_module_map(self) -> dict[str, str]:
        """파일 → 모듈 이름 매핑."""
        file_to_module = {}
        for m in self.modules:
            for f in m.files:
                file_to_module[f] = m.name
        return file_to_module

    def save(self, yaml_path: str) -> None:
        """YAML 파일로 저장."""
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)


def load_config(config_path: str) -> ModuleGroupConfig:
    """설정 파일 로드."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    return ModuleGroupConfig.from_yaml(config_path)


def validate_config(config: ModuleGroupConfig) -> list[str]:
    """설정 유효성 검사."""
    errors = []

    # 모듈 이름 중복 검사
    names = [m.name for m in config.modules]
    if len(names) != len(set(names)):
        duplicates = [n for n in names if names.count(n) > 1]
        errors.append(f"Duplicate module names: {set(duplicates)}")

    # 파일 중복 검사
    file_count = {}
    for m in config.modules:
        for f in m.files:
            file_count[f] = file_count.get(f, 0) + 1

    duplicates = [f for f, c in file_count.items() if c > 1]
    if duplicates:
        errors.append(f"Files belong to multiple modules: {duplicates}")

    # 빈 모듈 검사
    for m in config.modules:
        if not m.name:
            errors.append("Module with empty name found")
        if not m.files and not m.patterns:
            errors.append(f"Module '{m.name}' has no files or patterns")

    return errors
