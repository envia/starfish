#!/usr/bin/env python3
"""
CLI Entry Point for LLM-Based AST Extraction.

Provides command-line interface for running ENUM, Constant, and IPC
extraction using Cline's NATIVE LLM (not stub LLMClient).

SUPPORTED MODES:
  --generate-prompts-only: Generate prompts for Cline to process with its native LLM
  --merge-only: Merge rule-based + Cline's LLM results after Cline processes prompts

DEPRECATED:
  --hybrid-auto: REMOVED - called stub LLM (0 results)
  Use --generate-prompts-only + Cline native LLM + --merge-only instead.

Usage:
    # Step 1: Generate prompts (no LLM call)
    python tools/llm_extract_cli.py --ast-json graph-raw.json --extract all --generate-prompts-only

    # Step 2: Cline processes prompts with NATIVE LLM (saves JSON results)

    # Step 3: Merge results
    python tools/llm_extract_cli.py --load-results llm-extraction/ --merge-only --ast-json graph-raw.json
"""

import argparse
import json
import os
import sys
import time

try:
    from tools.llm_ast_analyzer import LLMASTAnalyzer
    from tools.llm_client import LLMClient
    from tools.patterns import (
        CONSTANT_KINDS,
        CONSTANT_NAME_PATTERNS,
        ENUM_KINDS,
        ENUM_NAME_PATTERNS,
        IPC_KINDS,
        IPC_NAME_PATTERNS,
        parse_json_from_markdown,
    )
except ImportError:
    from llm_ast_analyzer import LLMASTAnalyzer
    from llm_client import LLMClient
    from patterns import (
        CONSTANT_KINDS,
        CONSTANT_NAME_PATTERNS,
        ENUM_KINDS,
        ENUM_NAME_PATTERNS,
        IPC_KINDS,
        IPC_NAME_PATTERNS,
        parse_json_from_markdown,
    )



def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="LLM-Based AST Extraction for ENUM, Constant, and IPC patterns using Cline's NATIVE LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Step 1: Generate prompts (no LLM call - file I/O only)
  python tools/llm_extract_cli.py --ast-json graph-raw.json --extract all --generate-prompts-only

  # Step 2: Cline processes prompts with NATIVE LLM (saves JSON to llm-*-results.json)

  # Step 3: Merge rule-based + Cline's LLM results
  python tools/llm_extract_cli.py --load-results llm-extraction/ --merge-only --ast-json graph-raw.json

  # Extract only enums
  python tools/llm_extract_cli.py --ast-json graph-raw.json --extract enum --generate-prompts-only

  # Validate extraction completeness (report only)
  python tools/llm_extract_cli.py --validate --ast-json graph-raw.json --load-results llm-extraction/

  # Same, as a gate: exit 1 if the extraction is below the thresholds
  python tools/llm_extract_cli.py --validate --ast-json graph-raw.json --load-results llm-extraction/ \\
      --min-enum 5 --min-constant 20 --min-ipc 10
"""
    )

    parser.add_argument(
        '--ast-json',
        type=str,
        help='Path to AST JSON file (graph-raw.json) for extraction'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='llm-extraction-results.json',
        help='Path to save extraction results (default: llm-extraction-results.json)'
    )
    parser.add_argument(
        '--extract',
        type=str,
        action='append',
        choices=['enum', 'constant', 'ipc', 'all'],
        default=None,
        help='What to extract: enum, constant, ipc, or all (can specify multiple)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Directory to save prompt and result files for Cline processing'
    )
    parser.add_argument(
        '--load-results',
        type=str,
        default=None,
        help='Load previously saved results from directory instead of running extraction'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        default=False,
        help='Validate extraction completeness against AST JSON (requires --ast-json and --load-results)'
    )
    # Validation gate thresholds. Left unset, --validate stays a report
    # (exit 0); passing any of them turns it into a gate that exits 1 when the
    # merged extraction holds fewer items than required — which is what
    # code2spec-discovery Step 3-1e.3 relies on to block Step 4.
    parser.add_argument(
        '--min-enum',
        type=int,
        default=None,
        help='Fail --validate if fewer than N ENUMs were extracted'
    )
    parser.add_argument(
        '--min-constant',
        type=int,
        default=None,
        help='Fail --validate if fewer than N constants were extracted'
    )
    parser.add_argument(
        '--min-ipc',
        type=int,
        default=None,
        help='Fail --validate if fewer than N IPC patterns were extracted'
    )
    parser.add_argument(
        '--parse-response',
        type=str,
        default=None,
        help='Parse a saved LLM response file (for post-Cline processing)'
    )
    parser.add_argument(
        '--parse-type',
        type=str,
        choices=['enum', 'constant', 'ipc'],
        default=None,
        help='Type of extraction when using --parse-response'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    # Cline Autonomous Mode options - ONLY supported mode for LLM extraction
    # The --hybrid-auto mode was removed because it called stub LLM (0 results)
    parser.add_argument(
        '--generate-prompts-only',
        action='store_true',
        help='Generate LLM prompts only (no LLM call). Use when Cline will process prompts with its native LLM.'
    )
    parser.add_argument(
        '--merge-only',
        action='store_true',
        help='Merge rule-based and LLM results only (no new extraction). Use after Cline has processed prompts.'
    )

    return parser.parse_args()


def _analyze_ast_patterns(ast_data: dict) -> dict:
    """
    Analyze AST data to count detected patterns before LLM extraction.

    Args:
        ast_data: AST JSON data with 'nodes' and 'edges'

    Returns:
        Dictionary with pattern counts
    """
    nodes = ast_data.get("nodes", [])
    edges = ast_data.get("edges", [])

    enum_count = 0
    constant_count = 0
    ipc_count = 0
    error_code_count = 0

    for node in nodes:
        kind = node.get("kind", "")
        name = node.get("name", "")
        node.get("extra", {})

        # Count enums
        if kind in ENUM_KINDS or (name and ENUM_NAME_PATTERNS.search(name)):
            enum_count += 1

        # Count constants
        if kind in CONSTANT_KINDS or (name and CONSTANT_NAME_PATTERNS.search(name)):
            constant_count += 1
            # Check for error codes
            if name and (name.startswith("ERR_") or name.startswith("ERROR_") or name.startswith("EXIT_")):
                error_code_count += 1

        # Count IPC
        if kind in IPC_KINDS or (name and IPC_NAME_PATTERNS.search(name)):
            ipc_count += 1

    # Count IPC edges
    ipc_edges = [e for e in edges if e.get("kind") == "IPC"]

    return {
        "enum_candidates": enum_count,
        "constant_candidates": constant_count,
        "error_codes": error_code_count,
        "ipc_candidates": ipc_count,
        "ipc_edges": len(ipc_edges),
    }


def _rule_based_extract(ast_data: dict) -> dict:
    """
    Extract patterns using rule-based approach (patterns.py).

    Args:
        ast_data: AST JSON data with 'nodes' and 'edges'

    Returns:
        Dictionary with rule-based extractions
    """
    nodes = ast_data.get("nodes", [])
    edges = ast_data.get("edges", [])

    rule_enums = []
    rule_constants = []
    rule_ipc = []

    # Early deduplication: track seen names per category to avoid 60% duplicate overhead
    seen_enum_keys: set[str] = set()
    seen_const_keys: set[str] = set()
    seen_ipc_keys: set[str] = set()

    # Build IPC edge reference set for precise IPC node matching
    ipc_edge_sources: set[str] = set()
    ipc_edge_targets: set[str] = set()
    ipc_edge_mechanisms: dict[str, str] = {}  # node_name -> mechanism from edge
    for edge in edges:
        if edge.get("kind") == "IPC":
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            mechanism = edge.get("extra", {}).get("ipc_mechanism", "unknown")
            if src:
                ipc_edge_sources.add(src)
                # Extract bare name from qualified name (file::Class.method -> method)
                bare = src.split("::")[-1].split(".")[-1] if "::" in src else src
                ipc_edge_mechanisms[bare] = mechanism
            if tgt:
                ipc_edge_targets.add(tgt)
                bare = tgt.split("::")[-1].split(".")[-1] if "::" in tgt else tgt
                ipc_edge_mechanisms[bare] = mechanism

    for node in nodes:
        kind = node.get("kind", "")
        name = node.get("name", "")
        extra = node.get("extra", {})
        # FIX: Read source location directly from node fields (parser populates these)
        # Previously used extra.get("source_file") which was never populated.
        source_file = node.get("file_path", "unknown")
        source_line = node.get("line_start", 0)
        source_tag = f"[Source: {source_file}:{source_line}]"

        # Skip File nodes — they are not semantic entities
        if kind == "File":
            continue

        # Rule-based ENUM extraction
        if kind in ENUM_KINDS or (name and ENUM_NAME_PATTERNS.search(name)):
            dedup_key = f"{name}:{source_file}:{source_line}"
            if dedup_key not in seen_enum_keys:
                seen_enum_keys.add(dedup_key)
                # FIX: Parser stores enum values as a dict {name: value} in extra["values"],
                # not as a children list. Extract member names from the dict keys.
                values_dict = extra.get("values", {})
                if isinstance(values_dict, dict):
                    enum_values = list(values_dict.keys())
                elif isinstance(values_dict, list):
                    enum_values = values_dict
                else:
                    enum_values = []
                enum_entry = {
                    "name": name or f"anonymous_{kind}",
                    "type": kind,
                    "values": enum_values,
                    "source": source_tag,
                    "extraction_method": "rule_based"
                }
                # Include underlying type if available
                underlying = extra.get("underlying_type", "")
                if underlying:
                    enum_entry["underlying_type"] = underlying
                rule_enums.append(enum_entry)

        # Rule-based Constant extraction
        # FIX: Exclude Function/Test kinds — they are never constants.
        # Previously, IPC_KINDS={"Function"} caused functions to be checked
        # against CONSTANT_NAME_PATTERNS, misclassifying them as constants.
        if kind not in ("Function", "Test", "Class", "File") and (
            kind in CONSTANT_KINDS or (name and CONSTANT_NAME_PATTERNS.search(name))
        ):
            dedup_key = f"{name}:{source_file}:{source_line}"
            if dedup_key not in seen_const_keys:
                seen_const_keys.add(dedup_key)
                # FIX: Parser stores constant value in extra["value"], defaulting to "N/A"
                const_value = extra.get("value", extra.get("constant_value", "N/A"))
                const_entry = {
                    "name": name or "anonymous_constant",
                    "value": const_value,
                    "type": "constant",
                    "source": source_tag,
                    "extraction_method": "rule_based"
                }
                # Check for error codes
                if name and (name.startswith("ERR_") or name.startswith("ERROR_") or name.startswith("EXIT_")):
                    const_entry["type"] = "error_code"
                rule_constants.append(const_entry)

        # Rule-based IPC extraction
        # FIX: Only match nodes that have IPC edges or explicit ipc_mechanism in extra.
        # Previously, IPC_KINDS={"Class","Interface","Function"} matched ALL functions/classes,
        # and IPC_NAME_PATTERNS (case-insensitive) caught common words like "connect", "send".
        has_ipc_edge = name in ipc_edge_sources or name in ipc_edge_targets
        has_ipc_extra = bool(extra.get("ipc_mechanism"))
        if has_ipc_edge or has_ipc_extra:
            dedup_key = f"{name}:{source_file}:{source_line}"
            if dedup_key not in seen_ipc_keys:
                seen_ipc_keys.add(dedup_key)
                # Use mechanism from edge extra if available, otherwise infer
                mechanism = ipc_edge_mechanisms.get(name, "") or extra.get("ipc_mechanism", "") or _infer_ipc_mechanism(kind, name)
                ipc_entry = {
                    "name": name or "anonymous_ipc",
                    "mechanism": mechanism,
                    "source": source_tag,
                    "extraction_method": "rule_based"
                }
                rule_ipc.append(ipc_entry)

    # Extract IPC from edges (with proper source attribution)
    for edge in edges:
        if edge.get("kind") == "IPC":
            edge_extra = edge.get("extra", {})
            mechanism = edge_extra.get("ipc_mechanism", "unknown")
            edge_file = edge.get("file_path", "unknown")
            edge_line = edge.get("line", 0)
            edge_name = edge.get("target", edge.get("source", "ipc_edge"))
            dedup_key = f"{edge_name}:{edge_file}:{edge_line}"
            if dedup_key not in seen_ipc_keys:
                seen_ipc_keys.add(dedup_key)
                ipc_entry = {
                    "name": edge_name,
                    "mechanism": mechanism,
                    "source": f"[Source: {edge_file}:{edge_line}]",
                    "extraction_method": "rule_based"
                }
                rule_ipc.append(ipc_entry)

    return {
        "enums": rule_enums,
        "constants": rule_constants,
        "ipc_patterns": rule_ipc
    }



def _infer_ipc_mechanism(kind: str, name: str) -> str:
    """Infer IPC mechanism from kind/name patterns."""
    name_lower = name.lower() if name else ""
    kind_lower = kind.lower() if kind else ""

    if "binder" in name_lower or "binder" in kind_lower:
        return "binder"
    if "content" in name_lower and "provider" in name_lower:
        return "content_provider"
    if "broadcast" in name_lower or "receiver" in name_lower:
        return "broadcast_receiver"
    if "intent" in name_lower:
        return "intent"
    if "socket" in name_lower:
        return "socket"
    if "pipe" in name_lower:
        return "pipe"
    if "message" in name_lower:
        return "message_queue"

    return "unknown"


def _prepare_llm_gap_fill(ast_data: dict, rule_results: dict) -> tuple:
    """
    Prepare data for LLM gap-fill by identifying items not covered by rules.

    Args:
        ast_data: AST JSON data
        rule_results: Results from rule-based extraction

    Returns:
        Tuple of (enum_candidates, constant_candidates, ipc_candidates)
    """
    nodes = ast_data.get("nodes", [])

    # Get names already extracted by rules
    rule_enum_names = {e["name"] for e in rule_results["enums"]}
    rule_const_names = {c["name"] for c in rule_results["constants"]}
    rule_ipc_names = {i["name"] for i in rule_results["ipc_patterns"]}

    llm_enum_candidates = []
    llm_const_candidates = []
    llm_ipc_candidates = []

    for node in nodes:
        kind = node.get("kind", "")
        name = node.get("name", "")
        extra = node.get("extra", {})

        # Check if this looks like an enum but wasn't caught by rules
        if _looks_like_enum(kind, name, extra) and name not in rule_enum_names:
            llm_enum_candidates.append({
                "node": node,
                "reason": "semantic_enum"
            })

        # Check if this looks like a constant but wasn't caught by rules
        if _looks_like_constant(kind, name, extra) and name not in rule_const_names:
            llm_const_candidates.append({
                "node": node,
                "reason": "semantic_constant"
            })

        # Check if this looks like IPC but wasn't caught by rules
        if _looks_like_ipc(kind, name, extra) and name not in rule_ipc_names:
            llm_ipc_candidates.append({
                "node": node,
                "reason": "semantic_ipc"
            })

    return llm_enum_candidates, llm_const_candidates, llm_ipc_candidates


def _looks_like_enum(kind: str, name: str, extra: dict) -> bool:
    """Check if a node looks like an enum semantically."""
    # Check for sealed class, union type patterns
    kind_lower = kind.lower() if kind else ""
    name.lower() if name else ""

    semantic_patterns = [
        "sealed", "union", "variant", "option", "result",
        "enum_class", "enum_class_body"
    ]

    # Check kind
    if any(p in kind_lower for p in semantic_patterns):
        return True

    # Check if has enum-like children
    children = extra.get("children", [])
    for child in children:
        child_kind = child.get("kind", "").lower()
        if "item" in child_kind or "case" in child_kind or "variant" in child_kind:
            return True

    return False


def _looks_like_constant(kind: str, name: str, extra: dict) -> bool:
    """Check if a node looks like a constant semantically."""
    kind_lower = kind.lower() if kind else ""
    name_upper = name.upper() if name else ""

    # Check for const patterns
    if "const" in kind_lower:
        return True

    # Check for UPPER_CASE naming (common constant pattern)
    if name and name == name_upper and len(name) > 2:
        # Exclude common false positives
        if name not in ("API", "URL", "ID", "IO", "UI"):
            return True

    # Check for protocol/message patterns
    if name and ("MSG_" in name or "OPCODE_" in name or "CMD_" in name):
        return True

    return False


def _looks_like_ipc(kind: str, name: str, extra: dict) -> bool:
    """Check if a node looks like IPC semantically."""
    kind_lower = kind.lower() if kind else ""
    name_lower = name.lower() if name else ""

    # Check for IPC-related patterns
    ipc_patterns = [
        "transact", "parcel", "binder", "interface", "proxy", "stub",
        "send", "receive", "message", "channel", "pipe", "socket",
        "broadcast", "intent", "contentprovider", "aidl"
    ]

    if any(p in name_lower for p in ipc_patterns):
        return True

    if any(p in kind_lower for p in ipc_patterns):
        return True

    return False


def _run_hybrid_auto_extraction(
    ast_data: dict,
    output_path: str,
    output_dir: str,
    analyzer: LLMASTAnalyzer,
    llm_client: LLMClient,
    resume: bool = False,
    max_retries: int = 2,
) -> dict:
    """
    Run hybrid auto-LLM extraction: rule-based pre-extraction + LLM gap-fill.

    Fault-tolerance: each extraction type (ENUM, Constant, IPC) is isolated.
    If one type's LLM gap-fill fails entirely, the others continue and the
    workflow is NOT interrupted. Rule-based results are always preserved.

    Args:
        ast_data: AST JSON data
        output_path: Path to save results
        output_dir: Directory for intermediate files
        analyzer: LLMASTAnalyzer instance
        llm_client: LLMClient instance
        resume: Resume from partial extraction
        max_retries: Max retry attempts per LLM chunk on failure

    Returns:
        Combined extraction results
    """
    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)

    # Checkpoint path for resume support
    checkpoint_path = os.path.join(output_dir, ".extraction-checkpoint.json")

    # Track degradation for reporting
    degradation_log: list[dict] = []

    # Step 1: Rule-based pre-extraction (instant, always succeeds)
    print()
    print("[Step 1/5] Rule-based Pre-Extraction (instant)...")
    rule_results = _rule_based_extract(ast_data)

    rule_total = (
        len(rule_results["enums"]) +
        len(rule_results["constants"]) +
        len(rule_results["ipc_patterns"])
    )
    print(f"  ✓ ENUMs: {len(rule_results['enums'])} found")
    print(f"  ✓ Constants: {len(rule_results['constants'])} found")
    print(f"  ✓ IPC Patterns: {len(rule_results['ipc_patterns'])} found")
    print(f"  Rule-based complete: {rule_total} items")
    print()

    # Step 2: Prepare LLM gap-fill candidates
    print("[Step 2/5] Identifying LLM Gap-Fill Candidates...")
    enum_candidates, const_candidates, ipc_candidates = _prepare_llm_gap_fill(
        ast_data, rule_results
    )

    llm_total = len(enum_candidates) + len(const_candidates) + len(ipc_candidates)
    print(f"  ENUM gap-fill: {len(enum_candidates)} items")
    print(f"  Constant gap-fill: {len(const_candidates)} items")
    print(f"  IPC gap-fill: {len(ipc_candidates)} items")
    print(f"  LLM gap-fill needed: {llm_total} items")
    print()

    # Step 3: LLM gap-fill extraction — each type ISOLATED so one failure
    # does NOT interrupt the others or crash the workflow.
    print("[Step 3/5] LLM Gap-Fill Extraction (auto mode)...")

    llm_results = {
        "enums": [],
        "constants": [],
        "ipc_patterns": []
    }

    # ── ENUM extraction (isolated) ──
    if enum_candidates:
        print(f"  [1/3] ENUM gap-fill ({len(enum_candidates)} items)")
        try:
            enum_result = _stream_llm_extraction(
                llm_client, "enum", enum_candidates, ast_data,
                max_retries=max_retries,
                checkpoint_path=checkpoint_path,
                checkpoint_key="enum",
            )
            llm_results["enums"] = enum_result
            print(f"      ✓ Parsed {len(enum_result)} additional ENUMs")
        except Exception as e:
            print(f"      ✗ ENUM gap-fill FAILED: {e}")
            print(f"      ⚠️  Continuing with rule-based ENUMs only ({len(rule_results['enums'])} items)")
            degradation_log.append({
                "type": "enum",
                "status": "failed",
                "error": str(e),
                "fallback": "rule_based_only",
                "rule_based_count": len(rule_results["enums"]),
            })
    else:
        print("  [1/3] ENUM gap-fill: No items needed")

    # Save checkpoint after ENUM
    _save_checkpoint(checkpoint_path, llm_results, "enum")

    # ── Constant extraction (isolated) ──
    if const_candidates:
        print(f"  [2/3] Constant gap-fill ({len(const_candidates)} items)")
        try:
            const_result = _stream_llm_extraction(
                llm_client, "constant", const_candidates, ast_data,
                max_retries=max_retries,
                checkpoint_path=checkpoint_path,
                checkpoint_key="constant",
            )
            llm_results["constants"] = const_result
            print(f"      ✓ Parsed {len(const_result)} additional Constants")
        except Exception as e:
            print(f"      ✗ Constant gap-fill FAILED: {e}")
            print(f"      ⚠️  Continuing with rule-based constants only ({len(rule_results['constants'])} items)")
            degradation_log.append({
                "type": "constant",
                "status": "failed",
                "error": str(e),
                "fallback": "rule_based_only",
                "rule_based_count": len(rule_results["constants"]),
            })
    else:
        print("  [2/3] Constant gap-fill: No items needed")

    # Save checkpoint after Constant
    _save_checkpoint(checkpoint_path, llm_results, "constant")

    # ── IPC extraction (isolated) ──
    if ipc_candidates:
        print(f"  [3/3] IPC gap-fill ({len(ipc_candidates)} items)")
        try:
            ipc_result = _stream_llm_extraction(
                llm_client, "ipc", ipc_candidates, ast_data,
                max_retries=max_retries,
                checkpoint_path=checkpoint_path,
                checkpoint_key="ipc",
            )
            llm_results["ipc_patterns"] = ipc_result
            print(f"      ✓ Parsed {len(ipc_result)} additional IPC patterns")
        except Exception as e:
            print(f"      ✗ IPC gap-fill FAILED: {e}")
            print(f"      ⚠️  Continuing with rule-based IPC only ({len(rule_results['ipc_patterns'])} items)")
            degradation_log.append({
                "type": "ipc",
                "status": "failed",
                "error": str(e),
                "fallback": "rule_based_only",
                "rule_based_count": len(rule_results["ipc_patterns"]),
            })
    else:
        print("  [3/3] IPC gap-fill: No items needed")

    # Save final checkpoint
    _save_checkpoint(checkpoint_path, llm_results, "ipc")

    print()

    # Step 4: Merge results (rule-based + LLM)
    print("[Step 4/5] Merging Results...")
    final_results = _merge_results(rule_results, llm_results)

    print("  Final counts:")
    print(f"    ENUM:    {len(final_results['enums'])} total ({len(rule_results['enums'])} rule + {len(llm_results['enums'])} LLM)")
    print(f"    Constant: {len(final_results['constants'])} total ({len(rule_results['constants'])} rule + {len(llm_results['constants'])} LLM)")
    print(f"    IPC:      {len(final_results['ipc_patterns'])} total ({len(rule_results['ipc_patterns'])} rule + {len(llm_results['ipc_patterns'])} LLM)")
    if degradation_log:
        print(f"    ⚠️  Degradation: {len(degradation_log)} type(s) fell back to rule-based only")
    print()

    # Step 5: Save results (include degradation metadata)
    print("[Step 5/5] Saving Results...")

    # Attach degradation report to the output JSON so downstream consumers
    # know which extraction types are rule-based-only.
    output_with_meta = {
        **final_results,
        "_meta": {
            "degradation_report": degradation_log,
            "has_degradation": len(degradation_log) > 0,
        },
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_with_meta, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {output_path}")

    # Save summary
    summary_path = os.path.join(output_dir, "llm-extraction-summary.md")
    _save_extraction_summary(final_results, rule_results, llm_results, start_time, summary_path, degradation_log)
    print(f"  ✓ {summary_path}")

    # Clean up checkpoint on successful completion
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
        print("  ✓ Checkpoint cleaned up")

    elapsed = time.time() - start_time
    print()
    print(f"Total time: {elapsed:.0f}m {elapsed % 60:.0f}s")
    print()

    return final_results


def _stream_llm_extraction(
    llm_client: LLMClient,
    extraction_type: str,
    candidates: list,
    ast_data: dict,
    chunk_size: int = 15,
    max_retries: int = 2,
    checkpoint_path: str = None,
    checkpoint_key: str = None,
) -> list:
    """
    Run LLM extraction with chunked processing + retry + fault tolerance.

    Processes ALL candidates in chunks. Each chunk gets up to ``max_retries``
    attempts with exponential backoff. If a chunk fails all retries it is
    skipped — the remaining chunks still execute.

    Args:
        llm_client: LLMClient instance
        extraction_type: 'enum', 'constant', or 'ipc'
        candidates: List of candidate nodes (can be any size)
        ast_data: Full AST data for context
        chunk_size: Number of candidates per chunk (default: 15)
        max_retries: Max retry attempts per chunk on failure (default: 2)
        checkpoint_path: Path to checkpoint file for resume (optional)
        checkpoint_key: Key name for this extraction type in checkpoint (optional)

    Returns:
        List of extracted items from ALL chunks merged together
    """
    all_results = []
    total_candidates = len(candidates)
    num_chunks = (total_candidates + chunk_size - 1) // chunk_size
    failed_chunks: list[int] = []

    print(f"      Processing {total_candidates} candidates in {num_chunks} chunks of {chunk_size}...")
    print(f"      Retry policy: max {max_retries} attempts per chunk with exponential backoff")

    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = min(start_idx + chunk_size, total_candidates)
        chunk_candidates = candidates[start_idx:end_idx]

        # Build prompt for this chunk
        prompt = _build_gap_fill_prompt(extraction_type, chunk_candidates, ast_data)

        if not prompt:
            continue

        print(f"      Chunk {chunk_idx+1}/{num_chunks} (items {start_idx+1}-{end_idx}): ", end='', flush=True)

        chunk_results: list = []
        chunk_succeeded = False

        for attempt in range(1, max_retries + 2):  # 1 initial + max_retries retries
            try:
                response_text = ""

                # Use streaming if available
                if hasattr(llm_client, 'stream'):
                    for chunk_response in llm_client.stream(prompt):
                        chunk_text = chunk_response if isinstance(chunk_response, str) else str(chunk_response)
                        response_text += chunk_text
                else:
                    # Fallback to non-streaming
                    response_text = llm_client.complete(prompt)

                # Guard: if response equals prompt, the stub LLM returned the
                # prompt verbatim (no real LLM backend connected). Return empty
                # to avoid hallucinated data from example blocks in the prompt.
                if response_text == prompt:
                    print("✗ stub response (response == prompt)", end='', flush=True)
                    chunk_succeeded = True
                    break

                # Parse this chunk's results
                chunk_results = _parse_gap_fill_response(extraction_type, response_text, chunk_candidates)
                chunk_succeeded = True
                break  # success — no retry needed

            except Exception as e:
                if attempt <= max_retries:
                    backoff = 2 ** (attempt - 1)  # 1s, 2s, 4s, ...
                    print(f"✗ attempt {attempt}/{max_retries+1} failed ({e}), retrying in {backoff}s...", end='', flush=True)
                    time.sleep(backoff)
                else:
                    print(f"✗ FAILED after {max_retries+1} attempts: {e}")

        if chunk_succeeded:
            all_results.extend(chunk_results)
            print(f"✓ Extracted {len(chunk_results)} items")
        else:
            failed_chunks.append(chunk_idx + 1)
            # Continue with next chunk even if this one failed all retries

    if failed_chunks:
        print(f"      ⚠️  {len(failed_chunks)} chunk(s) failed: {failed_chunks}")

    print(f"      Total extracted from all chunks: {len(all_results)} items")
    return all_results


def _save_checkpoint(checkpoint_path: str, llm_results: dict, completed_key: str):
    """Save partial LLM extraction results to a checkpoint file.

    Called after each extraction type (enum, constant, ipc) completes or fails.
    On resume, the caller can load this file to skip already-completed types.
    """
    try:
        checkpoint = {
            "enums": llm_results.get("enums", []),
            "constants": llm_results.get("constants", []),
            "ipc_patterns": llm_results.get("ipc_patterns", []),
            "completed": completed_key,
            "timestamp": time.time(),
        }
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    except Exception:
        # Checkpoint failure should never crash the workflow
        pass


def _build_gap_fill_prompt(extraction_type: str, candidates: list, ast_data: dict) -> str:
    """
    Build concise LLM prompt for gap-fill extraction (Option C + A).

    NOTE: This function expects candidates to ALREADY be chunked by the caller
    (_stream_llm_extraction chunks ALL candidates into batches of 15).

    OPTIMIZATIONS:
    - Compact format: one line per candidate
    - Clear JSON output instructions
    - Processes ALL candidates passed (chunking done upstream)
    """
    if not candidates:
        return ""

    # Process ALL candidates passed (already chunked by _stream_llm_extraction)
    # Each chunk is ~15 candidates, small enough for single Cline message

    # Build compact candidate list
    candidate_lines = []
    for i, candidate in enumerate(candidates):
        node = candidate["node"]
        reason = candidate["reason"]
        name = node.get("name", "unknown")
        kind = node.get("kind", "unknown")
        # Use fixed source attribution from our Phase 1 fix
        source_file = node.get("file_path", "unknown")
        source_line = node.get("line_start", 0)

        # Compact one-line format: [N] name (kind, reason) @ file:line
        candidate_lines.append(f"[{i+1}] `{name}` ({kind}, {reason}) @ {source_file}:{source_line}")

    candidates_text = "\n".join(candidate_lines)

    # Option A: Clear, concise prompt optimized for Cline processing
    prompt = f"""# Task: {extraction_type.upper()} Gap-Fill Extraction

## Purpose
Extract {extraction_type} patterns that rule-based extraction missed.
These require semantic analysis (e.g., sealed classes, complex enum patterns, semantic constants).

## Candidates to Analyze ({len(candidates)} items)
{candidates_text}

## Output Format - CRITICAL
Return ONLY a valid JSON array. Each entry MUST have:
- "name": The pattern name (use qualified names like "ClassName.EnumName")
- "values": Array of values/member names (for enums) OR "value" string (for constants)
- "source": Exact format "[Source: file/path.ext:line_number]"
- "type": "{extraction_type}"

## Example Output
```json
[
  {{
    "name": "MyClass.State",
    "values": ["ACTIVE", "INACTIVE", "PENDING"],
    "type": "enum",
    "source": "[Source: src/models/state.ts:45]"
  }}
]
```

## Rules
1. Return ONLY the JSON array - no explanations, no markdown except the code block
2. Every entry MUST include source citation in exact format: `[Source: file:line]`
3. Only include true {extraction_type}s - be conservative, avoid false positives
4. For enums: extract all member names in "values" array
5. For constants: extract the actual value in "value" field
6. Use qualified names (e.g., "ClassName.MemberName" not just "MemberName")

## Response Format
Respond with ONLY:
```json
[... your extracted items ...]
```
"""

    return prompt


def _parse_gap_fill_response(extraction_type: str, response: str, candidates: list) -> list:
    """Parse LLM response for gap-fill extraction.

    Uses the shared ``parse_json_from_markdown`` utility from patterns.py
    instead of inline regex, ensuring consistent JSON extraction across modules.
    """
    parsed = parse_json_from_markdown(response)

    if isinstance(parsed, list):
        for item in parsed:
            item["extraction_method"] = "llm_gap_fill"
        return parsed
    return []


def _merge_results(rule_results: dict, llm_results: dict) -> dict:
    """
    Merge rule-based and LLM results, with deduplication.
    LLM results take precedence (they have better metadata).
    """
    # Use dict for deduplication by name
    final_enums = {}
    final_constants = {}
    final_ipc = {}

    # Add rule-based results first
    for e in rule_results["enums"]:
        key = e.get("name", id(e))
        final_enums[key] = e

    for c in rule_results["constants"]:
        key = c.get("name", id(c))
        final_constants[key] = c

    for i in rule_results["ipc_patterns"]:
        key = i.get("name", id(i))
        final_ipc[key] = i

    # LLM results overwrite (better metadata)
    for e in llm_results["enums"]:
        key = e.get("name", id(e))
        final_enums[key] = e

    for c in llm_results["constants"]:
        key = c.get("name", id(c))
        final_constants[key] = c

    for i in llm_results["ipc_patterns"]:
        key = i.get("name", id(i))
        final_ipc[key] = i

    return {
        "enums": list(final_enums.values()),
        "constants": list(final_constants.values()),
        "ipc_patterns": list(final_ipc.values())
    }


def _save_extraction_summary(
    final_results: dict,
    rule_results: dict,
    llm_results: dict,
    start_time: float,
    summary_path: str,
    degradation_log: list = None,
):
    """Save human-readable extraction summary."""
    elapsed = time.time() - start_time

    summary = f"""# LLM Extraction Summary

## Execution Time
Total: {elapsed:.0f}m {elapsed % 60:.0f}s

## Extraction Results

| Category | Rule-Based | LLM Gap-Fill | Total |
|----------|-----------|--------------|-------|
| ENUMs | {len(rule_results['enums'])} | {len(llm_results['enums'])} | {len(final_results['enums'])} |
| Constants | {len(rule_results['constants'])} | {len(llm_results['constants'])} | {len(final_results['constants'])} |
| IPC Patterns | {len(rule_results['ipc_patterns'])} | {len(llm_results['ipc_patterns'])} | {len(final_results['ipc_patterns'])} |
| **Total** | **{sum(len(v) for v in rule_results.values())}** | **{sum(len(v) for v in llm_results.values())}** | **{sum(len(v) for v in final_results.values())}** |

## Method Breakdown

- **Rule-Based**: Instant extraction using static patterns (patterns.py)
- **LLM Gap-Fill**: Semantic analysis for items missed by rules
"""

    # Append degradation report if any types fell back to rule-based only
    if degradation_log:
        summary += "\n## ⚠️ Degradation Report\n\n"
        summary += "The following extraction types failed LLM gap-fill and fell back to rule-based only:\n\n"
        summary += "| Type | Error | Rule-Based Count |\n"
        summary += "|------|-------|-----------------|\n"
        for entry in degradation_log:
            summary += f"| {entry['type']} | {entry.get('error', 'unknown')[:80]} | {entry.get('rule_based_count', 0)} |\n"
        summary += "\n**Impact**: These categories have reduced coverage. The 09-ipc-enum-catalog.md\n"
        summary += "should note which sections are rule-based-only.\n"

    summary += "\n## Top ENUMs\n"

    for e in final_results["enums"][:10]:
        summary += f"- `{e.get('name', 'unknown')}` ({e.get('type', 'unknown')})\n"

    summary += "\n## Top Constants\n"
    for c in final_results["constants"][:10]:
        summary += f"- `{c.get('name', 'unknown')}` = {c.get('value', 'unknown')}\n"

    summary += "\n## Top IPC Patterns\n"
    for i in final_results["ipc_patterns"][:10]:
        summary += f"- `{i.get('name', 'unknown')}` ({i.get('mechanism', 'unknown')})\n"

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)


def run_extraction(ast_json_path: str, extract_types: list, output_path: str, output_dir: str = None, verbose: bool = False):
    """
    Run LLM extraction on AST JSON data.

    Args:
        ast_json_path: Path to AST JSON file
        extract_types: List of types to extract ('enum', 'constant', 'ipc', 'all')
        output_path: Path to save combined results
        output_dir: Directory for prompt/result files
        verbose: Enable verbose output
    """
    # Validate input file
    if not os.path.exists(ast_json_path):
        print(f"[ERROR] AST JSON file not found: {ast_json_path}")
        sys.exit(1)

    # Determine what to extract
    extract_all = 'all' in extract_types
    do_enum = extract_all or 'enum' in extract_types
    do_constant = extract_all or 'constant' in extract_types
    do_ipc = extract_all or 'ipc' in extract_types

    # Set default output dir
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(ast_json_path), 'llm-extraction')

    print(f"[LLM Extract] AST JSON: {ast_json_path}")
    print(f"[LLM Extract] Output: {output_path}")
    print(f"[LLM Extract] Extract: {', '.join(extract_types)}")
    print(f"[LLM Extract] Prompt dir: {output_dir}")
    print()

    # Initialize analyzer
    analyzer = LLMASTAnalyzer(output_dir=output_dir)
    LLMClient()

    # Load AST JSON
    start_time = time.time()
    print("[Step 1/4] Loading AST JSON...")
    try:
        with open(ast_json_path, encoding='utf-8') as f:
            ast_data = json.load(f)
        print(f"  Loaded AST data: {len(json.dumps(ast_data))} characters")
    except Exception as e:
        print(f"[ERROR] Failed to load AST JSON: {e}")
        sys.exit(1)

    # Analyze AST patterns (NEW STEP)
    print()
    print("[Step 2/4] Analyzing detected patterns...")
    patterns = _analyze_ast_patterns(ast_data)

    print()
    print("  ┌─────────────────────────────────────┐")
    print("  │       Detected Pattern Summary      │")
    print("  ├─────────────────────────────────────┤")
    print(f"  │ ENUM candidates:     {patterns['enum_candidates']:>5}          │")
    print(f"  │ Constant candidates: {patterns['constant_candidates']:>5}          │")
    print(f"  │   └─ Error codes:    {patterns['error_codes']:>5}          │")
    print(f"  │ IPC candidates:      {patterns['ipc_candidates']:>5}          │")
    print(f"  │   └─ IPC edges:      {patterns['ipc_edges']:>5}          │")
    print("  └─────────────────────────────────────┘")

    # Show folder structure
    print()
    print("  [Folder Structure]")
    print(f"  {output_dir}/")
    if do_enum:
        print("    ├── llm-enum-prompt.md")
    if do_constant:
        print("    ├── llm-constant-prompt.md")
    if do_ipc:
        print("    ├── llm-ipc-prompt.md")
    print(f"    └── {os.path.basename(output_path)}")

    # Generate prompts
    print()
    print("[Step 3/4] Generating LLM prompts...")

    if do_enum:
        print("  Generating ENUM extraction prompt...")
        analyzer.extract_enums(ast_data, save_prompt=True)
        print("  ✓ ENUM prompt saved")

    if do_constant:
        print("  Generating Constant extraction prompt...")
        analyzer.extract_constants(ast_data, save_prompt=True)
        print("  ✓ Constant prompt saved")

    if do_ipc:
        print("  Generating IPC extraction prompt...")
        analyzer.extract_ipc_patterns(ast_data, save_prompt=True)
        print("  ✓ IPC prompt saved")

    # Skip saving placeholder results - user must process prompts first
    print()
    print("[Step 4/4] Prompts ready for LLM processing...")

    elapsed = time.time() - start_time
    print()
    print(f"[LLM Extract] Prompts generated in {elapsed:.1f}s")
    print()
    print("=" * 60)
    print("NEXT STEPS (Manual LLM Processing Required):")
    print("=" * 60)
    print()
    print("  1. Open the prompt files in the output directory:")
    if do_enum:
        print(f"     - {output_dir}/llm-enum-prompt.md")
    if do_constant:
        print(f"     - {output_dir}/llm-constant-prompt.md")
    if do_ipc:
        print(f"     - {output_dir}/llm-ipc-prompt.md")
    print()
    print("  2. Send each prompt to Cline's LLM for processing")
    print()
    print("  3. Save LLM responses as .md files")
    print()
    print("  4. Parse responses using --parse-response flag:")
    if do_enum:
        print(f"     python tools/llm_extract_cli.py --parse-response {output_dir}/llm-enum-response.md --parse-type enum --output {output_path}")
    if do_constant:
        print(f"     python tools/llm_extract_cli.py --parse-response {output_dir}/llm-constant-response.md --parse-type constant --output {output_path}")
    if do_ipc:
        print(f"     python tools/llm_extract_cli.py --parse-response {output_dir}/llm-ipc-response.md --parse-type ipc --output {output_path}")
    print()
    print("=" * 60)
    print("NOTE: Do NOT proceed with document generation until LLM responses are parsed.")
    print("      The placeholder results file contains empty arrays until parsing.")
    print("=" * 60)


def parse_response(response_path: str, parse_type: str, output_path: str, output_dir: str = None, verbose: bool = False):
    """
    Parse a saved LLM response file.

    Args:
        response_path: Path to the LLM response file
        parse_type: Type of extraction ('enum', 'constant', 'ipc')
        output_path: Path to save results
        output_dir: Directory for result files
        verbose: Enable verbose output
    """
    if not os.path.exists(response_path):
        print(f"[ERROR] Response file not found: {response_path}")
        sys.exit(1)

    if not parse_type:
        print("[ERROR] --parse-type is required when using --parse-response")
        sys.exit(1)

    # Set default output dir
    if output_dir is None:
        output_dir = os.path.dirname(response_path) or '.'

    # Read response
    with open(response_path, encoding='utf-8') as f:
        response = f.read()

    print(f"[LLM Extract] Parsing {parse_type} response from: {response_path}")

    # Initialize analyzer and parse
    analyzer = LLMASTAnalyzer(output_dir=output_dir)

    if parse_type == 'enum':
        results = analyzer.parse_enum_response(response)
    elif parse_type == 'constant':
        results = analyzer.parse_constant_response(response)
    elif parse_type == 'ipc':
        results = analyzer.parse_ipc_response(response)
    else:
        print(f"[ERROR] Unknown parse type: {parse_type}")
        sys.exit(1)

    # Save results
    all_results = analyzer.get_all_results()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"[LLM Extract] Parsed {len(results)} {parse_type} entries")
    print(f"[LLM Extract] Results saved to: {output_path}")


def load_and_merge_results(results_dir: str, output_path: str, verbose: bool = False):
    """
    Load previously saved results and merge into single output.

    Args:
        results_dir: Directory containing llm-*-results.json files
        output_path: Path to save merged results
        verbose: Enable verbose output
    """
    if not os.path.isdir(results_dir):
        print(f"[ERROR] Results directory not found: {results_dir}")
        sys.exit(1)

    analyzer = LLMASTAnalyzer()
    results = analyzer.load_results(results_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total = len(results['enums']) + len(results['constants']) + len(results['ipc_patterns'])
    print(f"[LLM Extract] Loaded {total} results from {results_dir}")
    print(f"  Enums: {len(results['enums'])}")
    print(f"  Constants: {len(results['constants'])}")
    print(f"  IPC Patterns: {len(results['ipc_patterns'])}")
    print(f"[LLM Extract] Merged results saved to: {output_path}")


# Written by --merge-only; holds rule-based + LLM results combined.
MERGED_RESULTS_FILENAME = "llm-extraction-results.json"


def _load_results_for_validation(analyzer, results_dir: str) -> tuple[dict, str]:
    """Load the result set --validate should grade.

    The documented flow merges first, then validates, and the thresholds are
    stated against merged totals ("ENUMs: 10-50+ (rule-based + LLM gap-fill)").
    Reading only llm-*-results.json would grade the LLM gap-fill in isolation
    and fail projects whose extraction came mostly from the rule-based pass, so
    prefer the merged file and fall back to the per-type files when absent.

    Returns:
        (results, human-readable description of where they came from)
    """
    merged_path = os.path.join(results_dir, MERGED_RESULTS_FILENAME)
    if os.path.isfile(merged_path):
        try:
            with open(merged_path, encoding='utf-8') as f:
                merged = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[WARNING] Could not read {merged_path}: {e}")
            print("          Falling back to the per-type LLM result files.")
        else:
            results = {
                key: merged.get(key, []) or []
                for key in ("enums", "constants", "ipc_patterns")
            }
            return results, f"merged results ({merged_path})"

    return (
        analyzer.load_results(results_dir),
        f"LLM result files only ({results_dir}) — run --merge-only first to grade merged totals",
    )


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    # Handle --validate mode
    if args.validate:
        if not args.ast_json:
            print("[ERROR] --ast-json is required for --validate mode")
            sys.exit(1)
        if not args.load_results:
            print("[ERROR] --load-results is required for --validate mode")
            sys.exit(1)

        analyzer = LLMASTAnalyzer()
        extraction_results, source_label = _load_results_for_validation(analyzer, args.load_results)
        report = analyzer.validate_completeness(args.ast_json, extraction_results)

        extracted_counts = {
            "enum": len(extraction_results.get("enums", [])),
            "constant": len(extraction_results.get("constants", [])),
            "ipc": len(extraction_results.get("ipc_patterns", [])),
        }
        thresholds = {
            "enum": args.min_enum,
            "constant": args.min_constant,
            "ipc": args.min_ipc,
        }

        print("[Validation] Extraction Completeness Report")
        print("=" * 50)
        print(f"  Graded set: {source_label}")
        for category in ("enum", "constant", "ipc"):
            cat = report[category]
            missing_str = ", ".join(cat["missing"][:5])
            if len(cat["missing"]) > 5:
                missing_str += f", ... (+{len(cat['missing'])-5} more)"
            print(f"  {category.upper()} coverage: {cat['rate']} — missing: {missing_str or 'none'}")
        print(f"  Overall: {report['overall_rate']}")

        # Threshold gate — only when the caller asked for one, so plain
        # --validate keeps working as a report.
        if any(v is not None for v in thresholds.values()):
            print()
            print("[Validation] Threshold Gate")
            print("=" * 50)
            failures = []
            for category in ("enum", "constant", "ipc"):
                minimum = thresholds[category]
                if minimum is None:
                    continue
                count = extracted_counts[category]
                status = "OK" if count >= minimum else "FAIL"
                print(f"  {category.upper()}: {count} extracted (min {minimum}) — {status}")
                if status == "FAIL":
                    failures.append(f"{category} {count} < {minimum}")
            if failures:
                print()
                print(f"[ERROR] Validation gate failed: {'; '.join(failures)}")
                print("        Do NOT proceed to the next step — fix the extraction first.")
                sys.exit(1)
            print("  Gate passed.")
        return

    # Handle --generate-prompts-only mode (Cline Autonomous Mode Step 1)
    if args.generate_prompts_only:
        if not args.ast_json:
            print("[ERROR] --ast-json is required for --generate-prompts-only mode")
            sys.exit(1)

        print()
        print("=" * 60)
        print("GENERATE PROMPTS ONLY MODE (Cline Autonomous)")
        print("=" * 60)
        print()

        # Load AST JSON
        print("[Step 1/2] Loading AST JSON...")
        try:
            with open(args.ast_json, encoding='utf-8') as f:
                ast_data = json.load(f)
            print(f"  Loaded: {len(json.dumps(ast_data))} characters")
        except Exception as e:
            print(f"[ERROR] Failed to load AST JSON: {e}")
            sys.exit(1)

        # Set output dir
        output_dir = args.output_dir or os.path.join(os.path.dirname(args.ast_json), 'llm-extraction')
        os.makedirs(output_dir, exist_ok=True)

        # Initialize analyzer
        analyzer = LLMASTAnalyzer(output_dir=output_dir)

        # Determine what to extract
        extract_all = args.extract and ('all' in args.extract)
        do_enum = extract_all or (args.extract and 'enum' in args.extract)
        do_constant = extract_all or (args.extract and 'constant' in args.extract)
        do_ipc = extract_all or (args.extract and 'ipc' in args.extract)

        # Generate prompts only (no LLM call)
        print()
        print("[Step 2/2] Generating LLM prompts (stub mode - no LLM call)...")

        if do_enum:
            print("  Generating ENUM extraction prompt...")
            analyzer.extract_enums(ast_data, save_prompt=True)
            print(f"  ✓ ENUM prompt saved: {output_dir}/llm-enum-prompt.md")

        if do_constant:
            print("  Generating Constant extraction prompt...")
            analyzer.extract_constants(ast_data, save_prompt=True)
            print(f"  ✓ Constant prompt saved: {output_dir}/llm-constant-prompt.md")

        if do_ipc:
            print("  Generating IPC extraction prompt...")
            analyzer.extract_ipc_patterns(ast_data, save_prompt=True)
            print(f"  ✓ IPC prompt saved: {output_dir}/llm-ipc-prompt.md")

        print()
        print("=" * 60)
        print("PROMPTS GENERATED - NEXT STEPS:")
        print("=" * 60)
        print()
        print("1. Cline (AI Assistant) should now read each prompt file:")
        if do_enum:
            print(f"   - {output_dir}/llm-enum-prompt.md")
        if do_constant:
            print(f"   - {output_dir}/llm-constant-prompt.md")
        if do_ipc:
            print(f"   - {output_dir}/llm-ipc-prompt.md")
        print()
        print("2. For each prompt, Cline uses its NATIVE LLM to analyze and extract JSON")
        print()
        print("3. Save each JSON response to the corresponding result file:")
        if do_enum:
            print(f"   - {output_dir}/llm-enum-results.json")
        if do_constant:
            print(f"   - {output_dir}/llm-constant-results.json")
        if do_ipc:
            print(f"   - {output_dir}/llm-ipc-results.json")
        print()
        print("4. After all responses are saved, run with --merge-only to combine results")
        print()
        return

    # Handle --merge-only mode (Cline Autonomous Mode Step 2)
    if args.merge_only:
        if not args.load_results:
            print("[ERROR] --load-results is required for --merge-only mode")
            sys.exit(1)

        print()
        print("=" * 60)
        print("MERGE ONLY MODE (Cline Autonomous)")
        print("=" * 60)
        print()

        # Set output dir
        output_dir = args.output_dir or args.load_results

        # Load rule-based results from the same directory
        ast_json_for_rules = args.ast_json

        if ast_json_for_rules:
            print("[Step 1/3] Loading AST JSON for rule-based extraction...")
            try:
                with open(ast_json_for_rules, encoding='utf-8') as f:
                    ast_data = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load AST JSON: {e}")
                sys.exit(1)

            # Run rule-based extraction
            print("[Step 2/3] Running rule-based extraction...")
            rule_results = _rule_based_extract(ast_data)
            print(f"  ✓ ENUMs: {len(rule_results['enums'])} found")
            print(f"  ✓ Constants: {len(rule_results['constants'])} found")
            print(f"  ✓ IPC Patterns: {len(rule_results['ipc_patterns'])} found")
        else:
            print("[WARNING] --ast-json not provided, skipping rule-based extraction")
            rule_results = {"enums": [], "constants": [], "ipc_patterns": []}

        # Load LLM results from directory
        print()
        print("[Step 3/3] Loading LLM results from Cline processing...")
        analyzer = LLMASTAnalyzer(output_dir=output_dir)

        # Try to load individual result files
        llm_results = {"enums": [], "constants": [], "ipc_patterns": []}

        enum_path = os.path.join(output_dir, "llm-enum-results.json")
        if os.path.exists(enum_path):
            with open(enum_path, encoding='utf-8') as f:
                llm_results["enums"] = json.load(f)
            print(f"  ✓ Loaded ENUMs: {len(llm_results['enums'])} items")

        const_path = os.path.join(output_dir, "llm-constant-results.json")
        if os.path.exists(const_path):
            with open(const_path, encoding='utf-8') as f:
                llm_results["constants"] = json.load(f)
            print(f"  ✓ Loaded Constants: {len(llm_results['constants'])} items")

        ipc_path = os.path.join(output_dir, "llm-ipc-results.json")
        if os.path.exists(ipc_path):
            with open(ipc_path, encoding='utf-8') as f:
                llm_results["ipc_patterns"] = json.load(f)
            print(f"  ✓ Loaded IPC Patterns: {len(llm_results['ipc_patterns'])} items")

        # Merge results
        print()
        print("Merging rule-based and LLM results...")
        final_results = _merge_results(rule_results, llm_results)

        # Add metadata
        output_with_meta = {
            **final_results,
            "_meta": {
                "extraction_mode": "cline_autonomous",
                "rule_based_count": sum(len(v) for v in rule_results.values()),
                "llm_count": sum(len(v) for v in llm_results.values()),
                "total_count": sum(len(v) for v in final_results.values()),
            },
        }

        # Save merged results
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_with_meta, f, indent=2, ensure_ascii=False)

        print()
        print("=" * 60)
        print("MERGE COMPLETE")
        print("=" * 60)
        print(f"  Rule-based: {output_with_meta['_meta']['rule_based_count']} items")
        print(f"  LLM (Cline): {output_with_meta['_meta']['llm_count']} items")
        print(f"  Total: {output_with_meta['_meta']['total_count']} items")
        print(f"  Output: {args.output}")
        print()
        return

    # Handle --load-results mode
    if args.load_results:
        load_and_merge_results(args.load_results, args.output, args.verbose)
        return

    # Handle --parse-response mode
    if args.parse_response:
        parse_response(args.parse_response, args.parse_type, args.output, args.output_dir, args.verbose)
        return

    # Normal extraction mode - require --ast-json and --extract
    if not args.ast_json:
        print("[ERROR] --ast-json is required for extraction mode")
        print("Use --help for usage information")
        sys.exit(1)

    if not args.extract:
        args.extract = ['all']

    # Standard extraction mode (generate prompts for Cline native LLM processing)
    # NOTE: The --hybrid-auto mode was removed because it called stub LLM (0 results).
    # Use --generate-prompts-only + Cline native LLM + --merge-only instead.
    print()
    print("[WARNING] Running in prompt-generation mode. For LLM extraction, use:")
    print("  1. python tools/llm_extract_cli.py --generate-prompts-only --ast-json ... --extract all")
    print("  2. Let Cline process prompts with its NATIVE LLM")
    print("  3. python tools/llm_extract_cli.py --merge-only --load-results ... --ast-json ...")
    print()
    run_extraction(args.ast_json, args.extract, args.output, args.output_dir, args.verbose)


if __name__ == '__main__':
    main()
