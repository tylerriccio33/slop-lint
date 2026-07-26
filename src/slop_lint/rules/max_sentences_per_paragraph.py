"""ASD-STE100 caps paragraphs at six sentences.

A paragraph with more than six sentences should be split. Not yet
implemented.
"""

from __future__ import annotations

from slop_lint.config import Config
from slop_lint.extract import TextBlock
from slop_lint.rules.base import Finding

name = "max-sentences-per-paragraph"


def check(block: TextBlock, config: Config) -> list[Finding]:
    return []
