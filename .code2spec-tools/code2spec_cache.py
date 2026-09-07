#!/usr/bin/env python3
"""Explicit spec-cache CLI for Code2Spec delta workflows."""

from __future__ import annotations

import argparse

try:
    from .delta.commands import cmd_cleanup_removed, cmd_spec_update
except ImportError:  # script/installed-tools flat execution
    from delta.commands import cmd_cleanup_removed, cmd_spec_update


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="code2spec-cache", description="Code2Spec spec-cache maintenance commands"
    )
    sub = parser.add_subparsers(dest="command")

    p_su = sub.add_parser(
        "spec-update", help="모듈 한 개의 spec 생성 결과를 spec-cache.json에 기록"
    )
    p_su.add_argument(
        "--output-dir",
        required=True,
        help="code2spec/.analysis 디렉토리 (spec-cache.json 위치)",
    )
    p_su.add_argument("--file", required=True, help="모듈 소스 파일 경로")
    p_su.add_argument(
        "--sdd-doc", default="", help="modules/<name>.md (spec_root 상대)"
    )
    p_su.add_argument(
        "--fr-doc",
        default="",
        help="functional-requirements/<name>-fr.md (없으면 빈값)",
    )
    p_su.add_argument(
        "--code2spec-version", default="", help="현재 code2spec 버전 (없으면 자동)"
    )
    p_su.add_argument(
        "--mode",
        choices=["light", "standard", "detail", "full", "custom"],
        default="",
        help="현재 분석 모드",
    )
    p_su.add_argument(
        "--analysis-scope", type=int, default=None, help="현재 analysis_scope 1|2|3|4|5"
    )
    p_su.add_argument(
        "--workspace-root",
        default="",
        help="프로젝트 루트 경로 (Source Files 상대경로 정규화용)",
    )

    p_cr = sub.add_parser(
        "cleanup-removed",
        help="diff-plan.json의 removed_modules에 대한 docs/traceability/cache 정리",
    )
    p_cr.add_argument("--output-dir", required=True)
    p_cr.add_argument("--diff-plan", required=True, help="diff-plan.json 경로")

    args = parser.parse_args()
    if args.command == "spec-update":
        cmd_spec_update(args)
    elif args.command == "cleanup-removed":
        cmd_cleanup_removed(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
