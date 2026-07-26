"""ASD-STE100 forbids dropping sentence parts to save words.

Terse fragments (e.g. "Remove panel, replace seal, install cover.") omit
verbs, subjects, or articles that a full instruction requires. Not yet
implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "no-omitted-sentence-parts"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
