#!/usr/bin/env python3
"""CLI for Code2Spec progress, history, and document-index commands.

Implementation is split by responsibility:
- progress.state: progress/resume state and traceability rows
- progress.history: runtime stats and history rendering
- doc_index.commands: source dependency map and core manifest indexing
"""

from __future__ import annotations

import argparse

try:
    from .history import (
        cmd_finalize_history,
        cmd_session_init,
        cmd_workflow_end,
        cmd_workflow_start,
    )
    from .state import (
        cmd_append_context,
        cmd_init,
        cmd_next_chunk,
        cmd_status,
        cmd_update,
    )
    from .telemetry import cmd_telemetry_event, cmd_telemetry_summary, cmd_workflow_fail
except ImportError:  # script/installed-tools flat execution
    from progress.history import (
        cmd_finalize_history,
        cmd_session_init,
        cmd_workflow_end,
        cmd_workflow_start,
    )
    from progress.state import (
        cmd_append_context,
        cmd_init,
        cmd_next_chunk,
        cmd_status,
        cmd_update,
    )
    from progress.telemetry import cmd_telemetry_event, cmd_telemetry_summary, cmd_workflow_fail

try:
    from ..doc_index.commands import cmd_build_deps_map, cmd_save_core_manifest
    from ..quality_metrics import cmd_compute_metrics, cmd_quality_gate
except ImportError:  # script/installed-tools flat execution
    from doc_index.commands import cmd_build_deps_map, cmd_save_core_manifest
    from quality_metrics import cmd_compute_metrics, cmd_quality_gate


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="code2spec-progress", description="분석 진행 상태 추적기"
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="모듈 목록으로 진행 상태 초기화")
    p_init.add_argument(
        "--modules-file",
        required=False,
        help="모듈 목록 파일 (--from-diff-plan 사용 시 무시)",
    )
    p_init.add_argument("--output-dir", required=True)
    p_init.add_argument(
        "--from-diff-plan",
        default=None,
        help=(
            "diff-plan.json 경로. changed/new/promoted/dependent/moved는 "
            "pending, unchanged는 completed로 분류"
        ),
    )

    # update
    p_upd = sub.add_parser("update", help="모듈 상태 업데이트")
    p_upd.add_argument("--output-dir", required=True)
    p_upd.add_argument("--module", required=True)
    p_upd.add_argument(
        "--status", choices=["done", "failed", "in_progress"], required=True
    )
    p_upd.add_argument("--fr-doc", default="-")
    p_upd.add_argument("--sdd-doc", default="-")
    p_upd.add_argument("--ast", default="✅")
    p_upd.add_argument("--reason-category", default="unknown")
    p_upd.add_argument("--message", default="")

    # status
    p_sta = sub.add_parser("status", help="현재 진행 상태 출력")
    p_sta.add_argument("--output-dir", required=True)

    # next-chunk
    p_nc = sub.add_parser("next-chunk", help="다음 미완료 청크 출력")
    p_nc.add_argument("--output-dir", required=True)

    # append-context
    p_ctx = sub.add_parser("append-context", help="청크 완료 후 컨텍스트 요약 추가")
    p_ctx.add_argument("--output-dir", required=True)
    p_ctx.add_argument("--pattern", default="")
    p_ctx.add_argument("--dependencies", default="")

    # session-init
    p_si = sub.add_parser("session-init", help="code2spec 세션 초기화")
    p_si.add_argument("--output-dir", required=True)
    p_si.add_argument("--target-path", default="")
    p_si.add_argument(
        "--workspace-root",
        default="",
        help=".code2spec-tools/.code2spec-venv가 설치된 프로젝트 루트",
    )
    p_si.add_argument(
        "--analysis-target",
        default="",
        help="실제로 분석할 프로젝트 또는 하위 디렉토리",
    )
    p_si.add_argument(
        "--output-root",
        default="",
        help="code2spec 산출물 루트 (기본: output-dir의 spec root)",
    )
    p_si.add_argument(
        "--mode",
        choices=["light", "standard", "detail", "full", "custom"],
        default="detail",  # Physical 모드 제거 이후 워크플로우는 항상 detail을 명시적으로 전달
    )
    p_si.add_argument(
        "--run-type",
        choices=["full", "delta"],
        default="full",
        help="실행 유형. delta이면 W-DELTA 단일 워크플로우로 기록",
    )
    p_si.add_argument("--coding-agent", default="")

    # workflow-start
    p_ws = sub.add_parser("workflow-start", help="워크플로우 시작 기록")
    p_ws.add_argument("--output-dir", required=True)
    p_ws.add_argument(
        "--workflow",
        required=True,
        choices=["W1", "W2", "W3", "W-DELTA", "w1", "w2", "w3", "w-delta"],
    )
    p_ws.add_argument("--coding-agent", default="")

    # workflow-end
    p_we = sub.add_parser("workflow-end", help="워크플로우 종료 기록")
    p_we.add_argument("--output-dir", required=True)
    p_we.add_argument(
        "--workflow",
        required=True,
        choices=["W1", "W2", "W3", "W-DELTA", "w1", "w2", "w3", "w-delta"],
    )
    p_we.add_argument("--coding-agent", default="")

    # workflow-fail
    p_wf = sub.add_parser("workflow-fail", help="워크플로우 실패 상태 telemetry event 기록")
    p_wf.add_argument("--output-dir", required=True)
    p_wf.add_argument(
        "--workflow",
        required=True,
        choices=["W1", "W2", "W3", "W-DELTA", "w1", "w2", "w3", "w-delta"],
    )
    p_wf.add_argument("--step", default="")
    p_wf.add_argument("--command-label", default="")
    p_wf.add_argument("--exit-code", type=int, default=None)
    p_wf.add_argument(
        "--reason-category",
        default="unknown",
        choices=[
            "missing_prerequisite",
            "invalid_config",
            "command_failed",
            "quality_gate_failed",
            "source_parse_failed",
            "llm_generation_failed",
            "unknown",
        ],
    )
    p_wf.add_argument("--message", default="")
    p_wf.add_argument("--artifact-path", action="append", default=[])
    p_wf.add_argument("--retryable", action="store_true")

    # telemetry-event
    p_te = sub.add_parser("telemetry-event", help="local telemetry event append")
    p_te.add_argument("--output-dir", required=True)
    p_te.add_argument("--event", required=True)
    p_te.add_argument(
        "--workflow",
        choices=["W1", "W2", "W3", "W-DELTA", "w1", "w2", "w3", "w-delta"],
        default=None,
    )
    p_te.add_argument("--step", default="")
    p_te.add_argument("--module", default="")
    p_te.add_argument("--command", default="")
    p_te.add_argument("--message", default="")
    p_te.add_argument("--reason-category", default="")
    p_te.add_argument("--exit-code", type=int, default=None)
    p_te.add_argument("--artifact-path", action="append", default=[])
    p_te.add_argument("--retryable", action="store_true")

    # telemetry-summary
    p_ts = sub.add_parser(
        "telemetry-summary",
        help="finalize 없이 local telemetry aggregate 출력",
    )
    p_ts.add_argument("--output-dir", required=True)
    p_ts.add_argument("--json", action="store_true", help="JSON aggregate로 출력")

    # finalize-history
    p_fh = sub.add_parser("finalize-history", help="history.md 생성")
    p_fh.add_argument("--output-dir", required=True)
    p_fh.add_argument("--note", default="")

    # build-deps-map — source-deps-map.json 구축
    p_bdm = sub.add_parser(
        "build-deps-map",
        help="Module Design Card에서 Source Files 섹션을 파싱하여 의존성 맵 구축",
    )
    p_bdm.add_argument(
        "--output-dir", required=True, help="code2spec/.analysis 디렉토리"
    )
    p_bdm.add_argument(
        "--workspace-root",
        default="",
        help="프로젝트 루트 경로 (파일 존재 검증용)",
    )

    # save-core-manifest — core-manifest.json 저장
    p_scm = sub.add_parser(
        "save-core-manifest",
        help="Core 모듈 목록을 core-manifest.json으로 저장",
    )
    p_scm.add_argument(
        "--output-dir", required=True, help="code2spec/.analysis 디렉토리"
    )
    p_scm.add_argument(
        "--priority-file",
        default="",
        help="module-priority-reviewed.md 경로 (Core 파일 목록 추출용)",
    )
    p_scm.add_argument(
        "--workspace-root",
        default="",
        help="프로젝트 루트 경로 (상대 Core 파일 경로 정규화용)",
    )
    p_scm.add_argument(
        "--analysis-scope", type=int, default=None, help="analysis_scope 1|2|3"
    )
    p_scm.add_argument("--mode", default="", help="분석 모드 light|standard|detail")
    p_scm.add_argument(
        "--module-groups",
        default="",
        help="module-groups.yaml 경로 (Logical Module 모드 시 모듈 이름→파일 경로 확장)",
    )

    # compute-metrics — 품질 메트릭 계산
    p_cm = sub.add_parser(
        "compute-metrics",
        help="생성 문서의 품질 메트릭 계산 (EP, SC, CC, BSLR)",
    )
    p_cm.add_argument(
        "--output-dir", required=True, help="code2spec/.analysis 디렉토리"
    )
    p_cm.add_argument(
        "--workspace-root",
        default="",
        help="프로젝트 루트 경로 (Source 태그 파일 경로 검증용)",
    )

    # quality-gate — 품질 메트릭 acceptance gate 판정
    p_qg = sub.add_parser(
        "quality-gate",
        help="quality-metrics.json을 기준으로 PASS/WARN/FAIL 판정",
    )
    p_qg.add_argument(
        "--output-dir", required=True, help="code2spec/.analysis 디렉토리"
    )
    p_qg.add_argument(
        "--workspace-root",
        default="",
        help="프로젝트 루트 경로 (Source 태그 파일 경로 검증용)",
    )
    p_qg.add_argument(
        "--run-type", choices=["full", "delta"], default="full"
    )
    p_qg.add_argument("--evidence-precision-min", type=float, default=0.95)
    p_qg.add_argument("--broken-source-link-rate-max", type=float, default=0.01)
    p_qg.add_argument("--core-coverage-min", type=float, default=0.90)
    p_qg.add_argument("--source-coverage-drop-warn", type=float, default=0.20)

    args = parser.parse_args()
    if args.command == "init":
        cmd_init(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "next-chunk":
        cmd_next_chunk(args)
    elif args.command == "append-context":
        cmd_append_context(args)
    elif args.command == "session-init":
        cmd_session_init(args)
    elif args.command == "workflow-start":
        cmd_workflow_start(args)
    elif args.command == "workflow-end":
        cmd_workflow_end(args)
    elif args.command == "workflow-fail":
        cmd_workflow_fail(args)
    elif args.command == "telemetry-event":
        cmd_telemetry_event(args)
    elif args.command == "telemetry-summary":
        cmd_telemetry_summary(args)
    elif args.command == "finalize-history":
        cmd_finalize_history(args)
    elif args.command == "build-deps-map":
        cmd_build_deps_map(args)
    elif args.command == "save-core-manifest":
        cmd_save_core_manifest(args)
    elif args.command == "compute-metrics":
        cmd_compute_metrics(args)
    elif args.command == "quality-gate":
        cmd_quality_gate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
