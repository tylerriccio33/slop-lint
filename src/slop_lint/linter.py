"""Run the enabled rules against every text block in a source file."""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import extract_text_blocks
from slop_lint.rules import REGISTRY
from slop_lint.rules.base import Finding


def lint_source(source: str, config: Config) -> list[Finding]:
    active_rules = [REGISTRY[name] for name in config.enabled_rules if name in REGISTRY]
    findings: list[Finding] = []
    for block in extract_text_blocks(source):
        for rule in active_rules:
            findings.extend(rule.check(block, config))
    return sorted(findings, key=lambda f: (f.line, f.col))
