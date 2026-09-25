"""Command-line entry point: ``slop-lint file1.py file2.py ...``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from slop_lint import color
from slop_lint.config import PRESETS, load_config
from slop_lint.extract import is_supported_file
from slop_lint.linter import lint_source
from slop_lint.strip import strip_prose


def _fix(paths: list[Path], use_color: bool) -> int:
    fixed = 0
    for path in paths:
        if path.suffix != ".py":
            continue
        source = path.read_text(encoding="utf-8")
        try:
            stripped = strip_prose(source)
        except SyntaxError as exc:
            print(f"{path}: skipped, could not parse: {exc}", file=sys.stderr)
            continue
        if stripped != source:
            path.write_text(stripped, encoding="utf-8")
            fixed += 1
            print(f"{color.cyan(str(path), enabled=use_color)}: stripped docstrings and comments")
    if fixed:
        print(color.bold(f"Fixed {fixed} file{'s' if fixed != 1 else ''}", enabled=use_color))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="slop-lint")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument(
        "--preset", choices=PRESETS, help="strict: flag every docstring and comment"
    )
    parser.add_argument(
        "--budget",
        type=int,
        metavar="N",
        help="allow one prose line per N lines of code in each module, class, and def",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="remove every docstring and comment from Python files (strict preset)",
    )
    args = parser.parse_args(argv)

    use_color = color.supports_color()
    if args.fix:
        return _fix(args.files, use_color)

    config = load_config().with_preset(args.preset).with_budget(args.budget)
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
