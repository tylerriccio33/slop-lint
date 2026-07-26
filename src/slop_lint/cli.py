"""Command-line entry point: ``slop-lint file1.py file2.py ...``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from slop_lint.config import load_config
from slop_lint.linter import lint_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="slop-lint")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)

    config = load_config()
    had_findings = False

    for path in args.files:
        if path.suffix != ".py":
            continue
        source = path.read_text(encoding="utf-8")
        for finding in lint_source(source, config):
            had_findings = True
            print(f"{path}:{finding.line}:{finding.col}: [{finding.rule}] {finding.message}")

    return 1 if had_findings else 0


if __name__ == "__main__":
    sys.exit(main())
