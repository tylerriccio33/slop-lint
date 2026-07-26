"""ASD-STE100 allows a higher word limit for descriptive text than for instructions.

Cap procedures at 20 words per sentence; cap descriptive (non-procedure)
text at 25. This rule needs a text-kind distinction that
``max-sentence-length`` does not make. Not yet implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "descriptive-sentence-length"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
