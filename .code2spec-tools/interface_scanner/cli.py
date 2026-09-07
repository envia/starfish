"""CLI entry point for the interface candidate scanner."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from .reporter import generate_markdown_report
from .scanner import run_scan
from .schema import validate_collection


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="interface_scanner",
        description="Scan source code for interface/protocol candidates (IPC, messaging, etc.)",
    )
    parser.add_argument("--repo", required=True, help="Repository root path to scan")
    parser.add_argument("--ast-dir", default=None, help="AST output directory (optional)")
    parser.add_argument("--output-dir", required=True, help="Output directory for artifacts")
    parser.add_argument("--families", default="message", help="Comma-separated families (default: message)")
    parser.add_argument("--targets", default="android,node,react", help="Comma-separated targets (default: android,node,react)")
    parser.add_argument("--strict", action="store_true", help="Fail on scanner error instead of continuing")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    output_dir = Path(args.output_dir).resolve()
    ast_dir = Path(args.ast_dir).resolve() if args.ast_dir else None
    families = [f.strip() for f in args.families.split(",") if f.strip()]
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]

    if not repo_path.is_dir():
        print(f"[interface_scanner] ERROR: repo path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        collection = run_scan(
            repo_path=repo_path,
            ast_dir=ast_dir,
            families=families,
            targets=targets,
            output_dir=output_dir,
        )
    except Exception as e:
        error_artifact = output_dir / "interface-candidate-scan-error.json"
        error_artifact.write_text(json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, indent=2), encoding="utf-8")
        print(f"[interface_scanner] ERROR: {e}", file=sys.stderr)
        if args.strict:
            sys.exit(1)
        print("[interface_scanner] Non-strict mode: continuing despite scanner failure.")
        return

    # Validate
    errors = validate_collection(collection)
    if errors:
        print(f"[interface_scanner] WARNING: {len(errors)} validation errors found:", file=sys.stderr)
        for err in errors[:10]:
            print(f"  - {err}", file=sys.stderr)

    # Write interface-candidates.json
    candidates_path = output_dir / "interface-candidates.json"
    data = collection.to_dict()
    # Ensure output_dir is populated in the artifact
    if not data.get("output_dir"):
        data["output_dir"] = str(output_dir)
    candidates_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[interface_scanner] Written: {candidates_path} ({len(collection.candidates)} candidates)")

    # Write message-contract-candidates.md
    md_path = output_dir / "message-contract-candidates.md"
    md_content = generate_markdown_report(collection)
    md_path.write_text(md_content, encoding="utf-8")
    print(f"[interface_scanner] Written: {md_path}")

    # Write optional metrics
    metrics_path = output_dir / "interface-candidate-metrics.json"
    metrics_path.write_text(json.dumps(collection.metrics, indent=2) + "\n", encoding="utf-8")
    print(f"[interface_scanner] Written: {metrics_path}")


if __name__ == "__main__":
    main()
