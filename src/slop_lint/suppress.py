"""Inline suppression comments: ``# slop-lint: ignore`` / ``# slop-lint: ignore[rule-name]``."""

from __future__ import annotations

import re

from slop_lint.rules.base import Finding

_SUPPRESS_RE = re.compile(r"#\s*slop-lint:\s*ignore(?:\[([\w,\s-]+)\])?")


def parse_suppressions(source: str) -> dict[int, frozenset[str] | None]:
    """Map source line numbers to the rule names to suppress there.

    ``None`` means the line suppresses every rule. A frozenset restricts
    suppression to those specific rule names.
    """
    suppressions: dict[int, frozenset[str] | None] = {}
    for lineno, line in enumerate(source.splitlines(), start=1):
        match = _SUPPRESS_RE.search(line)
        if not match:
            continue
        rules = match.group(1)
        if rules is None:
            suppressions[lineno] = None
        else:
            suppressions[lineno] = frozenset(
                name.strip() for name in rules.split(",") if name.strip()
            )
    return suppressions


def filter_suppressed(findings: list[Finding], source: str) -> list[Finding]:
    """Drop findings whose line carries a matching ``# slop-lint: ignore`` comment."""
    suppressions = parse_suppressions(source)
    if not suppressions:
        return findings
    kept: list[Finding] = []
    for finding in findings:
        rules = suppressions.get(finding.line, ())
        if rules is None or finding.rule in rules:
            continue
        kept.append(finding)
    return kept
