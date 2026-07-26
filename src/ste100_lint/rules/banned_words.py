"""Flag project-specific banned words configured in pyproject.toml."""

from __future__ import annotations

import re

from ste100_lint.config import Config
from ste100_lint.extract import TextBlock
from ste100_lint.rules.base import Finding
from ste100_lint.rules.position import resolve_position

name = "banned-words"

_WORD_RE = re.compile(r"[A-Za-z']+")


def check(block: TextBlock, config: Config) -> list[Finding]:
    if not config.banned_words:
        return []
    findings: list[Finding] = []
    for match in _WORD_RE.finditer(block.text):
        word = match.group(0)
        if word.lower() not in config.banned_words:
            continue
        line, col = resolve_position(block, match.start())
        findings.append(
            Finding(
                rule=name,
                message=f'banned word "{word}"',
                line=line,
                col=col,
            )
        )
    return findings
