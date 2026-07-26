"""Run the enabled rules against every text block in a source file."""

from __future__ import annotations

from pathlib import Path

from slop_lint.config import Config
from slop_lint.extract import extract_text_blocks, extract_text_blocks_for_file
from slop_lint.rules import REGISTRY
from slop_lint.rules.base import Finding


def lint_source(source: str, config: Config, path: Path | None = None) -> list[Finding]:
    active_rules = [REGISTRY[name] for name in config.enabled_rules if name in REGISTRY]
    if path is not None:
        blocks = extract_text_blocks_for_file(path, source)
    else:
        blocks = extract_text_blocks(source)
    findings: list[Finding] = []
    for block in blocks:
        for rule in active_rules:
            findings.extend(rule.check(block, config))
    return sorted(findings, key=lambda f: (f.line, f.col))
