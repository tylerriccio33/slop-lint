"""ASD-STE100 requires active voice. Flag "be" + past-participle as a heuristic proxy."""

from __future__ import annotations

import re

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding
from slop_lint.rules.position import resolve_position

name = "passive-voice"

_IRREGULAR_PARTICIPLES = (
    "done|made|given|taken|written|seen|known|shown|found|held|built|"
    "sent|kept|left|brought|bought|caught|taught|thought|set|put|read"
)
_PASSIVE_RE = re.compile(
    rf"\b(is|are|was|were|be|been|being)\b\s+(?:\w+ly\s+)?"
    rf"(\w+ed|{_IRREGULAR_PARTICIPLES})\b",
    re.IGNORECASE,
)


def check(block: TextBlock, config: Config) -> list[Finding]:
    findings: list[Finding] = []
    for match in _PASSIVE_RE.finditer(block.text):
        line, col = resolve_position(block, match.start())
        findings.append(
            Finding(
                rule=name,
                message=f'possible passive voice: "{match.group(0)}"',
                line=line,
                col=col,
            )
        )
    return findings
