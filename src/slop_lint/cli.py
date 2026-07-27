"""Command-line entry point: ``slop-lint file1.py file2.py ...``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from slop_lint import color
from slop_lint.config import load_config
from slop_lint.extract import is_supported_file
from slop_lint.linter import lint_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="slop-lint")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)

    config = load_config()
    use_color = color.supports_color()
    finding_count = 0

    for path in args.files:
        if not is_supported_file(path):
            continue
        source = path.read_text(encoding="utf-8")
        for finding in lint_source(source, config, path=path):
            finding_count += 1
            location = color.cyan(f"{path}:{finding.line}:{finding.col}", enabled=use_color)
            rule = color.bold_red(finding.rule, enabled=use_color)
            print(f"{location}: {rule} {finding.message}")

    if finding_count:
        summary = color.bold(
            f"Found {finding_count} issue{'s' if finding_count != 1 else ''}", enabled=use_color
        )
        print(summary)

    return 1 if finding_count else 0


if __name__ == "__main__":
    sys.exit(main())
