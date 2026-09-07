"""code2spec: Extract AST and maintain spec generation artifacts."""

from .version import get_code2spec_version

__version__ = get_code2spec_version()

# Public modules — direct imports are also supported (e.g. `from tools.patterns import ...`).
# Re-exporting here provides convenience for `from tools import LLMClient, patterns, ...`.
__all__ = [
    "get_code2spec_version",
    "__version__",
    "patterns",
    "type_discovery",
    "llm_client",
    "llm_ast_analyzer",
]
