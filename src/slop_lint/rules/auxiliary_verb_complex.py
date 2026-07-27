"""ASD-STE100 disallows auxiliary verbs used to build complex verb constructions.

Modal/auxiliary chains (e.g. "should have finished checking") are not
approved verb forms. Flag a modal verb followed by "have" (optionally
"have been") plus a participle, as a heuristic proxy.
"""

from __future__ import annotations

import re

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding
from slop_lint.rules.position import resolve_position

name = "auxiliary-verb-complex"

_MODALS = "can|could|may|might|must|shall|should|will|would"
_IRREGULAR_PARTICIPLES = (
    "done|made|given|taken|written|seen|known|shown|found|held|built|"
    "sent|kept|left|brought|bought|caught|taught|thought|set|put|read"
)
_COMPLEX_VERB_RE = re.compile(
    rf"\b(?:{_MODALS})\b\s+have\s+(?:been\s+)?"
    rf"(\w+ed|{_IRREGULAR_PARTICIPLES})\b(?:\s+(\w+ing)\b)?",
    re.IGNORECASE,
)


def check(block: TextBlock, config: Config) -> list[Finding]:
    findings: list[Finding] = []
    for match in _COMPLEX_VERB_RE.finditer(block.text):
        line, col = resolve_position(block, match.start())
        findings.append(
            Finding(
                rule=name,
                message=f'complex verb construction: "{match.group(0)}"',
                line=line,
                col=col,
            )
        )
    return findings
