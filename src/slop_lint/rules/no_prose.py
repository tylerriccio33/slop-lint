"""Flag every docstring and comment: the ``strict`` preset wants code with no prose."""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.pragma import is_pragma
from slop_lint.rules.base import Finding

name = "no-prose"

_PROSE_DOCS = frozenset({"markdown", "text"})


def check(block: TextBlock, config: Config) -> list[Finding]:
    if block.kind in _PROSE_DOCS:
        return []
    if block.kind == "comment" and is_pragma(block.text):
        return []
    what = "comment" if block.kind == "comment" else block.kind.replace("-", " ")
    return [Finding(rule=name, message=f"{what} not allowed", line=block.line, col=block.col)]
