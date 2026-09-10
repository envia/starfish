"""
LLM-Based AST Analyzer for ENUM, Constant, and IPC Extraction.

This module provides LLM-powered analysis of AST JSON to extract:
- ENUM definitions (Java, Kotlin, @IntDef, etc.)
- Constants (Java const, Kotlin const val, C++ #define, etc.)
- IPC patterns (Binder, Socket, BroadcastReceiver, etc.)

Uses the same 3-step pattern as type_discovery.py:
  1. generate_prompt() → saves llm-prompt.md
  2. Cline LLM processes the prompt
  3. parse_llm_response() → returns structured extraction results

Token-efficient pipeline: AST → Filter → Semantic Markdown → Single LLM call.
No chunking. No raw JSON. Compact markdown that LLMs natively understand.
"""

import json
import logging
import os
from pathlib import Path

try:
    from tools.llm_prompts import (
        CONSTANT_EXTRACTION_PROMPT,
        ENUM_EXTRACTION_PROMPT,
        IPC_EXTRACTION_PROMPT,
    )
except ImportError:
    from llm_prompts import (
        CONSTANT_EXTRACTION_PROMPT,
        ENUM_EXTRACTION_PROMPT,
        IPC_EXTRACTION_PROMPT,
    )

try:
    from tools.llm_client import LLMClient
except ImportError:
    from llm_client import LLMClient

logger = logging.getLogger(__name__)


class LLMASTAnalyzer:
    """
    LLM-powered AST analyzer for extracting enums, constants, and IPC patterns.

    Token-efficient pipeline: AST → Filter → Semantic Markdown → Single LLM call.
    No chunking. No raw JSON. Compact markdown that LLMs natively understand.
    """

    def __init__(self, llm_client: LLMClient | None = None, output_dir: str | None = None):
        """
        Initialize the LLM AST Analyzer.

        Args:
            llm_client: Optional LLMClient instance. If not provided, creates default.
            output_dir: Directory to save prompt files for Cline processing.
        """
        self.llm_client = llm_client or LLMClient()
        self.output_dir = output_dir
        self._enum_results = []
        self._constant_results = []
        self._ipc_results = []
        logger.info("LLMASTAnalyzer initialized")

    def _load_ast_json(self, ast_json) -> dict:
        """
        Load AST JSON from file path or dict.

        Args:
            ast_json: Either a dict with AST data, or a string path to a JSON file.

        Returns:
            Dictionary containing AST structure
        """
        if isinstance(ast_json, dict):
            return ast_json

        if isinstance(ast_json, str):
            # It's a file path
            path = Path(ast_json)
            if not path.exists():
                raise FileNotFoundError(f"AST JSON file not found: {ast_json}")
            with open(path, encoding='utf-8') as f:
                return json.load(f)

        raise ValueError(f"ast_json must be dict or file path, got {type(ast_json)}")

    def _save_prompt(self, prompt: str, prompt_type: str) -> str:
        """
        Save prompt to file for Cline to process.

        Args:
            prompt: The formatted prompt string
            prompt_type: Type of prompt (enum/constant/ipc)

        Returns:
            Path to saved prompt file
        """
        if not self.output_dir:
            return ""

        os.makedirs(self.output_dir, exist_ok=True)
        prompt_path = os.path.join(self.output_dir, f"llm-{prompt_type}-prompt.md")
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        logger.info(f"Saved {prompt_type} prompt to {prompt_path}")
        return prompt_path

    def _save_results(self, results: list, result_type: str) -> str:
        """
        Save extraction results to JSON file.

        Args:
            results: List of extracted items
            result_type: Type of results (enum/constant/ipc)

        Returns:
            Path to saved results file
        """
        if not self.output_dir:
            return ""

        os.makedirs(self.output_dir, exist_ok=True)
        results_path = os.path.join(self.output_dir, f"llm-{result_type}-results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {result_type} results ({len(results)} items) to {results_path}")
        return results_path

    # =========================================================================
    # ENUM Extraction
    # =========================================================================

    def extract_enums(self, ast_json, save_prompt: bool = True) -> list[dict]:
        """
        Extract ENUM definitions from AST using LLM analysis.

        Pre-filters AST to enum-relevant nodes, converts to compact semantic
        markdown, and generates a single prompt for Cline's LLM.

        Args:
            ast_json: Dictionary containing parsed AST structure, or path to JSON file
            save_prompt: Whether to save the prompt file for Cline processing

        Returns:
            List of dicts with keys: name, values, type, language, source
        """
        logger.info("Starting ENUM extraction with LLM")

        # Load AST data
        ast_data = self._load_ast_json(ast_json)

        # Format prompt with AST data (single call, semantic markdown)
        prompt = self.llm_client.format_prompt_with_ast(
            ENUM_EXTRACTION_PROMPT, ast_data, extraction_type="enum"
        )

        # Save prompt for Cline to process
        if save_prompt:
            self._save_prompt(prompt, "enum")

        # Store prompt for reference
        self._enum_prompt = prompt
        self._enum_results = []

        logger.info("ENUM extraction: single prompt prepared for Cline LLM")
        return self._enum_results

    def parse_enum_response(self, response: str) -> list[dict]:
        """
        Parse Cline's LLM response for ENUM extraction.

        Args:
            response: Raw LLM response text containing extracted enums

        Returns:
            List of enum dicts with keys: name, values, type, language, source
        """
        parsed = self.llm_client.parse_extraction_response(response, expected_type='list')

        if not isinstance(parsed, list):
            logger.error("ENUM response is not a list")
            return []

        # Validate and normalize each enum entry
        validated_enums = []
        for item in parsed:
            if not isinstance(item, dict):
                continue

            enum_entry = {
                "name": item.get("name", "UNKNOWN"),
                "values": item.get("values", []),
                "type": item.get("type", "unknown"),
                "language": item.get("language", "unknown"),
                "source": item.get("source", "[Source: unknown:0]")
            }

            # Validate source citation format
            if not enum_entry["source"].startswith("[Source:"):
                enum_entry["source"] = f"[Source: {enum_entry['source']}]"

            # Warn about unqualified generic enum names (Gap 1)
            _GENERIC_ENUM_NAMES = frozenset({
                "type", "state", "mode", "kind", "status", "category",
                "level", "flag", "action", "role", "phase", "style",
            })
            bare_name = enum_entry["name"].split(".")[-1]
            if "." not in enum_entry["name"] and bare_name.lower() in _GENERIC_ENUM_NAMES:
                logger.warning(
                    f"ENUM name '{enum_entry['name']}' is unqualified — "
                    f"should be 'EnclosingClass.{enum_entry['name']}'"
                )

            validated_enums.append(enum_entry)

        self._enum_results = validated_enums

        # Save results
        self._save_results(validated_enums, "enum")

        logger.info(f"Parsed {len(validated_enums)} enums from LLM response")
        return validated_enums

    # =========================================================================
    # Constant Extraction
    # =========================================================================

    def extract_constants(self, ast_json, save_prompt: bool = True) -> list[dict]:
        """
        Extract constant definitions from AST using LLM analysis.

        Pre-filters AST to constant-relevant nodes, converts to compact semantic
        markdown, and generates a single prompt for Cline's LLM.

        Args:
            ast_json: Dictionary containing parsed AST structure, or path to JSON file
            save_prompt: Whether to save the prompt file for Cline processing

        Returns:
            List of dicts with keys: name, value, type, language, usage_context, source
        """
        logger.info("Starting Constant extraction with LLM")

        # Load AST data
        ast_data = self._load_ast_json(ast_json)

        # Format prompt with AST data (single call, semantic markdown)
        prompt = self.llm_client.format_prompt_with_ast(
            CONSTANT_EXTRACTION_PROMPT, ast_data, extraction_type="constant"
        )

        # Save prompt for Cline to process
        if save_prompt:
            self._save_prompt(prompt, "constant")

        # Store prompt for reference
        self._constant_prompt = prompt
        self._constant_results = []

        logger.info("Constant extraction: single prompt prepared for Cline LLM")
        return self._constant_results

    def parse_constant_response(self, response: str) -> list[dict]:
        """
        Parse Cline's LLM response for Constant extraction.

        Args:
            response: Raw LLM response text containing extracted constants

        Returns:
            List of constant dicts with keys: name, value, type, language, usage_context, source
        """
        parsed = self.llm_client.parse_extraction_response(response, expected_type='list')

        if not isinstance(parsed, list):
            logger.error("Constant response is not a list")
            return []

        # Validate and normalize each constant entry
        validated_constants = []
        for item in parsed:
            if not isinstance(item, dict):
                continue

            constant_entry = {
                "name": item.get("name", "UNKNOWN"),
                "value": item.get("value", ""),
                "type": item.get("type", "unknown"),
                "language": item.get("language", "unknown"),
                "usage_context": item.get("usage_context", ""),
                "source": item.get("source", "[Source: unknown:0]")
            }

            # Validate source citation format
            if not constant_entry["source"].startswith("[Source:"):
                constant_entry["source"] = f"[Source: {constant_entry['source']}]"

            validated_constants.append(constant_entry)

        self._constant_results = validated_constants

        # Save results
        self._save_results(validated_constants, "constant")

        logger.info(f"Parsed {len(validated_constants)} constants from LLM response")
        return validated_constants

    # =========================================================================
    # IPC Pattern Extraction
    # =========================================================================

    def extract_ipc_patterns(self, ast_json, save_prompt: bool = True) -> list[dict]:
        """
        Extract IPC patterns from AST using LLM analysis.

        Pre-filters AST to IPC-relevant nodes and edges, converts to compact
        semantic markdown, and generates a single prompt for Cline's LLM.

        Args:
            ast_json: Dictionary containing parsed AST structure, or path to JSON file
            save_prompt: Whether to save the prompt file for Cline processing

        Returns:
            List of dicts with keys: mechanism, source_component, target_component, data, language, source
        """
        logger.info("Starting IPC pattern extraction with LLM")

        # Load AST data
        ast_data = self._load_ast_json(ast_json)

        # Format prompt with AST data (single call, semantic markdown)
        prompt = self.llm_client.format_prompt_with_ast(
            IPC_EXTRACTION_PROMPT, ast_data, extraction_type="ipc"
        )

        # Save prompt for Cline to process
        if save_prompt:
            self._save_prompt(prompt, "ipc")

        # Store prompt for reference
        self._ipc_prompt = prompt
        self._ipc_results = []

        logger.info("IPC extraction: single prompt prepared for Cline LLM")
        return self._ipc_results

    def parse_ipc_response(self, response: str) -> list[dict]:
        """
        Parse Cline's LLM response for IPC pattern extraction.

        Args:
            response: Raw LLM response text containing extracted IPC patterns

        Returns:
            List of IPC dicts with keys: mechanism, source_component, target_component, data, language, source
        """
        parsed = self.llm_client.parse_extraction_response(response, expected_type='list')

        if not isinstance(parsed, list):
            logger.error("IPC response is not a list")
            return []

        # Validate and normalize each IPC entry
        validated_ipc = []
        for item in parsed:
            if not isinstance(item, dict):
                continue

            ipc_entry = {
                "mechanism": item.get("mechanism", "unknown"),
                "source_component": item.get("source_component", ""),
                "target_component": item.get("target_component", ""),
                "data": item.get("data", ""),
                "language": item.get("language", "unknown"),
                "source": item.get("source", "[Source: unknown:0]"),
                "message_ids": item.get("message_ids", []),
                "signal_events": item.get("signal_events", []),
            }

            # Validate source citation format
            if not ipc_entry["source"].startswith("[Source:"):
                ipc_entry["source"] = f"[Source: {ipc_entry['source']}]"

            validated_ipc.append(ipc_entry)

        self._ipc_results = validated_ipc

        # Save results
        self._save_results(validated_ipc, "ipc")

        logger.info(f"Parsed {len(validated_ipc)} IPC patterns from LLM response")
        return validated_ipc

    # =========================================================================
    # Combined extraction
    # =========================================================================

    def extract_all(self, ast_json, save_prompt: bool = True) -> dict:
        """
        Run all extractions (enum, constant, IPC) on the AST data.

        Each extraction type gets a single prompt with pre-filtered,
        compact semantic markdown. No chunking.

        Args:
            ast_json: Dictionary containing parsed AST structure, or path to JSON file
            save_prompt: Whether to save prompt files for Cline processing

        Returns:
            Dict with keys: enums, constants, ipc_patterns
        """
        logger.info("Starting full LLM extraction (enum + constant + IPC)")

        results = {
            "enums": self.extract_enums(ast_json, save_prompt=save_prompt),
            "constants": self.extract_constants(ast_json, save_prompt=save_prompt),
            "ipc_patterns": self.extract_ipc_patterns(ast_json, save_prompt=save_prompt),
        }

        return results

    def get_all_results(self) -> dict:
        """
        Get all accumulated extraction results.

        Returns:
            Dict with keys: enums, constants, ipc_patterns
        """
        return {
            "enums": self._enum_results,
            "constants": self._constant_results,
            "ipc_patterns": self._ipc_results,
        }

    def load_results(self, results_dir: str) -> dict:
        """
        Load previously saved extraction results from JSON files.

        Args:
            results_dir: Directory containing llm-*-results.json files

        Returns:
            Dict with keys: enums, constants, ipc_patterns
        """
        results = {"enums": [], "constants": [], "ipc_patterns": []}

        for key, filename in [("enums", "llm-enum-results.json"),
                              ("constants", "llm-constant-results.json"),
                              ("ipc_patterns", "llm-ipc-results.json")]:
            path = os.path.join(results_dir, filename)
            if os.path.exists(path):
                with open(path, encoding='utf-8') as f:
                    results[key] = json.load(f)
                logger.info(f"Loaded {len(results[key])} {key} from {path}")

        self._enum_results = results["enums"]
        self._constant_results = results["constants"]
        self._ipc_results = results["ipc_patterns"]

        return results

    # =========================================================================
    # Completeness Validation (Gap 8)
    # =========================================================================

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a name to its bare form for comparison.

        Extracted names may be qualified (e.g. ``ClassName.EnumName``) while
        AST-side names are raw (e.g. ``EnumName``).  Stripping qualification
        ensures the two sets are comparable.
        """
        if not name:
            return ""
        # Take the last component after '.' (qualified name) or '::' (edge id)
        bare = name.rsplit(".", 1)[-1]
        bare = bare.rsplit("::", 1)[-1]
        return bare

    def validate_completeness(self, ast_json, extraction_results=None) -> dict:
        """Compare AST node counts against extraction results to find gaps.

        Counts enum/constant/IPC-relevant nodes in the AST JSON and compares
        against extracted results to produce a coverage report.

        Args:
            ast_json: Dictionary containing parsed AST structure, or path to JSON file
            extraction_results: Optional dict with keys: enums, constants, ipc_patterns.
                              If None, uses self._enum_results etc.

        Returns:
            Dict with per-category coverage:
            {
                "enum": {"total_in_ast": N, "extracted": M, "missing": [...], "rate": "M/N%"},
                "constant": {"total_in_ast": N, "extracted": M, "missing": [...], "rate": "M/N%"},
                "ipc": {"total_in_ast": N, "extracted": M, "missing": [...], "rate": "M/N%"},
                "overall_rate": "M/N%"
            }
        """
        try:
            from tools.patterns import (
                CONSTANT_KINDS,
                CONSTANT_NAME_PATTERNS,
                ENUM_KINDS,
                ENUM_NAME_PATTERNS,
            )
        except ImportError:
            from patterns import (
                CONSTANT_KINDS,
                CONSTANT_NAME_PATTERNS,
                ENUM_KINDS,
                ENUM_NAME_PATTERNS,
            )

        ast_data = self._load_ast_json(ast_json)
        nodes = ast_data.get("nodes", [])
        edges = ast_data.get("edges", [])

        if extraction_results is None:
            extraction_results = self.get_all_results()

        report = {}
        total_ast = 0
        total_extracted = 0

        # --- ENUM coverage ---
        enum_ast_names = set()
        for n in nodes:
            kind = n.get("kind", "")
            name = n.get("name", n.get("file_path", ""))
            if kind in ENUM_KINDS or (name and ENUM_NAME_PATTERNS.search(name)):
                enum_ast_names.add(name)

        enum_extracted_names = {self._normalize_name(e.get("name", "")) for e in extraction_results.get("enums", [])}
        enum_missing = sorted(enum_ast_names - enum_extracted_names)
        enum_total = len(enum_ast_names)
        enum_count = len(enum_ast_names & enum_extracted_names)

        report["enum"] = {
            "total_in_ast": enum_total,
            "extracted": enum_count,
            "missing": enum_missing,
            "rate": f"{enum_count}/{enum_total} ({100*enum_count//enum_total if enum_total else 0}%)",
        }
        total_ast += enum_total
        total_extracted += enum_count

        # --- Constant coverage ---
        const_ast_names = set()
        for n in nodes:
            kind = n.get("kind", "")
            name = n.get("name", "")
            if kind in CONSTANT_KINDS or (name and CONSTANT_NAME_PATTERNS.search(name)):
                const_ast_names.add(name)

        const_extracted_names = {self._normalize_name(c.get("name", "")) for c in extraction_results.get("constants", [])}
        const_missing = sorted(const_ast_names - const_extracted_names)
        const_total = len(const_ast_names)
        const_count = len(const_ast_names & const_extracted_names)

        report["constant"] = {
            "total_in_ast": const_total,
            "extracted": const_count,
            "missing": const_missing,
            "rate": f"{const_count}/{const_total} ({100*const_count//const_total if const_total else 0}%)",
        }
        total_ast += const_total
        total_extracted += const_count

        # --- IPC coverage ---
        # The denominator mirrors what the extractor actually treats as IPC
        # (llm_extract_cli._rule_based_extract): a node qualifies only if it sits
        # on an IPC edge or carries an explicit ipc_mechanism. Using
        # IPC_KINDS/IPC_NAME_PATTERNS here instead — as this function used to —
        # counts every class named `*Channel` and every `connect()` as a missed
        # extraction, so the reported rate understates coverage by an order of
        # magnitude and can never reach 100%.
        ipc_edge_endpoints = set()
        for e in edges:
            if e.get("kind") == "IPC":
                for endpoint in (e.get("source", ""), e.get("target", "")):
                    if endpoint:
                        ipc_edge_endpoints.add(endpoint)

        ipc_ast_names = {self._normalize_name(ep) for ep in ipc_edge_endpoints}
        for n in nodes:
            name = n.get("name", "")
            if not name:
                continue
            if name in ipc_edge_endpoints or n.get("extra", {}).get("ipc_mechanism"):
                ipc_ast_names.add(self._normalize_name(name))
        ipc_ast_names.discard("")

        # Rule-based IPC entries carry `name`/`mechanism`, LLM-extracted ones
        # carry source_component/target_component. Read every key, or the
        # numerator drops all rule-based hits while the denominator keeps them.
        ipc_extracted_names = set()
        for ipc in extraction_results.get("ipc_patterns", []):
            for key in ("name", "source_component", "target_component"):
                value = ipc.get(key, "")
                if value:
                    ipc_extracted_names.add(self._normalize_name(value))

        ipc_missing = sorted(ipc_ast_names - ipc_extracted_names)
        ipc_total = len(ipc_ast_names)
        ipc_count = len(ipc_ast_names & ipc_extracted_names)

        report["ipc"] = {
            "total_in_ast": ipc_total,
            "extracted": ipc_count,
            "missing": ipc_missing,
            "rate": f"{ipc_count}/{ipc_total} ({100*ipc_count//ipc_total if ipc_total else 0}%)",
        }
        total_ast += ipc_total
        total_extracted += ipc_count

        report["overall_rate"] = f"{total_extracted}/{total_ast} ({100*total_extracted//total_ast if total_ast else 0}%)"

        return report
