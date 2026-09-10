#!/usr/bin/env python3
"""Explicit progress/history CLI for Code2Spec."""

from __future__ import annotations

try:
    from .progress.cli import main
except ImportError:  # script/installed-tools flat execution
    from progress.cli import main


if __name__ == "__main__":
    main()
